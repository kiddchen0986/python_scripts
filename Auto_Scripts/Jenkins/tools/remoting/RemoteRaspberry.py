import paramiko
import argparse
import os
import stat


class RemoteRaspberry(object):
    """Class for sending commands to a remote Raspberry PI"""
    def __init__(self, hostname=None, username='jenkins', password='secret'):
        """Setup a connection"""
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname, username=username, password=password)
        self.sftp = self.ssh.open_sftp()

    def close(self):
        """Close all connections"""
        self.sftp.close()
        self.ssh.close()

    def run_command(self, command, folder=None, show_output=True, timeout=None):
        """Run <command> in <folder> over ssh
        :returns status, output, error
        """
        if show_output:
            print("Running remote command '{}' in {}".format(command, folder or "root folder"))

        if folder:
            command = "cd {}; {}".format(folder, command)
        _, stdout, stderr = self.ssh.exec_command(command, timeout=timeout)
        out = stdout.read().decode('utf-8')
        err = stderr.read().decode('utf-8')

        if show_output and out.strip() != "":
            print(out)
        if show_output and err.strip() != "":
            print("stderr:\n{}".format(err))

        return stdout.channel.recv_exit_status(), out, err

    def download(self, source):
        """Download file(s) over ssh"""
        if self.is_dir_on_remote(source):
            print("Downloading content of folder: {}".format(source))
            self.download_recursive(source)
        else:
            print("Downloading file: " + source)
            path, filename = os.path.split(source)
            if path and not os.path.exists(path):
                os.makedirs(path)
            self.sftp.get(source, os.path.join(path, filename))

    def download_recursive(self, source):
        """Walk through <source> on remote downloading all files in all folders"""
        items = self.sftp.listdir(source)

        if not os.path.exists(source):
            os.makedirs(source)

        for item in items:
            if self.is_dir_on_remote(source + '/' + item):
                self.download_recursive(source + '/' + item)
            else:
                self.sftp.get(source + '/' + item, source + '/' + item)  # Use same folder structure for destination

    def upload(self, source, destination):
        """Upload file(s) over ssh"""
        if os.path.isdir(source):
            print("Uploading content of folder {} to {}".format(source, destination))
            # Create destination if not existing on remote
            for folder in destination.split('/'):
                if folder and not self.is_dir_on_remote(folder):
                    self.sftp.mkdir(folder)
                    self.sftp.chdir(folder)
                elif folder:
                    self.sftp.chdir(folder)
            # Walk through source. Create folders on remote if necessary and upload files
            for root, folders, files in os.walk(source):
                curr_folder = os.path.join(destination, root.replace(source, "", 1))
                if curr_folder:
                    curr_folder = curr_folder.replace("\\", "/")
                    self.sftp.chdir()
                    self.sftp.chdir(curr_folder)

                for file in files:
                    self.sftp.put(os.path.join(root, file), file)

                for folder in folders:
                    if not self.is_dir_on_remote(folder):
                        self.sftp.mkdir(folder)
            self.sftp.chdir()  # Go back to root folder

        else:
            print("Uploading file: " + source)
            if destination is None:
                _, destination = os.path.split(source)  # Use filename from source, will be put in root folder
            else:
                path, filename = os.path.split(destination)
                if not filename:  # If destination folder specified but no filename, use filename from source
                    _, filename = os.path.split(source)
                    destination = os.path.join(destination, filename)

            # Create folders if necessary
            path, _ = os.path.split(os.path.normpath(destination))
            for folder in path.split(os.sep):
                if folder and not self.is_dir_on_remote(folder):
                    self.sftp.mkdir(folder)
                    self.sftp.chdir(folder)
                elif folder:
                    self.sftp.chdir(folder)

            self.sftp.chdir()  # Go back to root folder
            self.sftp.put(source, destination)

    def is_dir_on_remote(self, source):
        """Check if <source> is a directory
        :returns true if <source> is a directory, false otherwise"""
        try:
            return stat.S_ISDIR(self.sftp.lstat(source).st_mode)
        except FileNotFoundError:
            return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', '-ip', required=True, help='IP to host')
    parser.add_argument('--command', '-cmd', required=False, help='Command to execute')
    parser.add_argument('--upload', '-ul', required=False, help='File/folder to upload')
    parser.add_argument('--destination', '-dest', required=False, help='Destination to upload.')
    parser.add_argument('--download', '-dl', required=False, help='File/folder to download')
    parser.add_argument('--output', '-out', default=False, action='store_true')

    args = parser.parse_args()
    remote = RemoteRaspberry(args.host)

    if args.command:
        remote.run_command(command=args.command, show_output=args.output)
    elif args.upload:
        remote.upload(args.upload, args.destination)
    elif args.download:
        remote.download(args.download)

    remote.close()

