import os
import time
MAX_RETRIES = 10


class ADB(object):

    def __init__(self, remote_computer=None):
        self.remote_computer = remote_computer

    def __run_command(self, type, command, retry=True, show_output=True, timeout=None):
        command = type + ' ' + command
        code, out, err = self.remote_computer.run_command(command=command, show_output=show_output, timeout=timeout)

        retry_nbr = 0
        while code != 0 and retry:
            retry_nbr += 1
            code, out, err = self.remote_computer.run_command(command=command, show_output=show_output)
            if code != 0 and retry_nbr < MAX_RETRIES:
                self.remote_computer.run_command(command="adb kill-server", show_output=show_output)
                self.remote_computer.run_command(command="adb start-server", show_output=show_output)
                self.wait_for_device()
            if retry_nbr >= MAX_RETRIES:
                break

        if code > 0:
            print("Command failed: " + err)
            raise Exception(err)

        return code, out, err

    def run_adb_command(self, command, retry=True, show_output=True, timeout=None):
        # Check if in fastboot, if yes run fastboot reboot
        _, out, _ = self.run_fastboot_command("devices", show_output=False)
        lines = out.splitlines()

        if lines and 'fastboot' in lines[0]:
            self.run_fastboot_command('reboot')

        self.wait_for_device()
        return self.__run_command('adb', command, retry, show_output, timeout)

    def run_fastboot_command(self, command, retry=True, show_output=True, timeout=None):
        return self.__run_command('fastboot', command, retry, show_output, timeout)

    def wait_for_device(self, timeout=240):
        code, out, err = self.remote_computer.run_command("timeout %i adb wait-for-device" % timeout, show_output=False)
        if code != 0:
            raise Exception("[ADB] Device failed to start in time")
        return code, out, err

    def wait_for_system(self, timeout=240):
        code, out, err = self.remote_computer.run_command("adb shell getprop sys.boot_completed", show_output=False)
        count = 0
        while "1" not in out:
            code, out, err = self.remote_computer.run_command("adb shell getprop sys.boot_completed", show_output=False)
            time.sleep(5)
            count += 5
            if count > timeout:
                print("System failed to start in time, terminating")
                print(out + err)
                return 1, out, err
        return code, out, err

    def reboot_device(self):
        _, out, _ = self.run_fastboot_command("devices", show_output=False)
        lines = out.splitlines()

        if lines and 'fastboot' in lines[0]:
            self.run_fastboot_command('reboot')
        else:
            self.run_adb_command('reboot')

        return self.wait_for_device()

    def root_device(self):
        self.run_adb_command("root")
        self.run_adb_command("remount")
        self.wait_for_device()

    def get_serial_no(self):
        code, out, err = self.remote_computer.run_command(command="adb get-serialno")

        if 'unknown' in out + err or 'no devices/emulators found' in out + err:
            code = -1

        return code

    def adb_push(self, source, destination):
        self.wait_for_device()
        rpi_destination = os.path.basename(os.path.normpath(source))
        self.remote_computer.upload(source, "android/{}".format(rpi_destination))
        rpi_source_folder = "android/{}".format(os.path.basename(os.path.normpath(source)))
        return self.run_adb_command("push {} {}".format(rpi_source_folder, destination), timeout=360)

    def install_app(self, app_file, args=""):
        """Install an app <file>"""
        self.wait_for_device()
        attempts = 0
        while attempts < 5:
            self.wait_for_device()
            self.remote_computer.upload(app_file, "android/" + os.path.split(app_file)[1])
            try:
                return self.run_adb_command("install -t {} android/{}".format(args, os.path.split(app_file)[1]),
                                    timeout=360)
            except Exception as _:
                print("Failed to install app, retry")
                self.run_adb_command("kill-server")
                self.wait_for_device()
                self.run_adb_command("reboot")
                self.wait_for_device()
                self.root_device()
                attempts += 1
