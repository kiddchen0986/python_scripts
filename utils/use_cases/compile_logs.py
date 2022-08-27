"""Compile the information found in a directory of logs
"""
import sys, os
from utils import from_files, utils_common, io_csv
import argparse


def run(directory):
    """Takes a directory of logs, extracts the .json file information and compiles in a .csv file

    NOTE: this script assumes that all .json files in the given directory have the same format.
    AND: keys to nested dicts will be lost.

    :param directory: the directory of ctl-logs
    :type directory: str
    :return: file path to the .csv file
    """
    utils_common.update_time_date_stamp()

    csv_fp = utils_common.create_file_path(os.path.split(directory)[1],
                                           ".csv",
                                           "_compiled_logs")

    logs = from_files.retrieve_directory_content(directory, parse_json=False)

    flat_header = []
    flat = []

    for id_, paths in logs.items():
        if id_ == "not_matched":
            continue

        for val in paths:
            # Loop through the files for that capture
            if ".json" in val:

                parsed = from_files.parse_json(paths[val])
                flat.append(utils_common.flatten_dict(parsed))

                if not flat_header:
                    flat_header = utils_common.flatten_dict(parsed, keys=True)

    if not flat_header:
        sys.exit("No header values were extracted for the .csv file")
    else:
        io_csv.write_row(flat_header, csv_fp)
        io_csv.write_rows(flat, csv_fp)

    return csv_fp


if __name__ == "__main__":
    # 'Hardcoded' directories
    directories = ["K:\\Users\\varvara.gioti\\CTL2 logs\\20170725_MTT12-RC2_CTL-2_Compare (1)"
                   "\\20170725_MTT12-RC2_CTL-2_Compare\\CTL_2.0_RC3"]

    # Parse user-input
    parser = argparse.ArgumentParser(description="Compile the information found in a directory of CTL logs, "
                                                 "into a .csv file.")
    parser.add_argument('-d', '--dirs',
                        type=str,
                        nargs='+',
                        help="the directory for which the module should be run",
                        default=[])
    parser.add_argument('-sd', '--script_dirs',
                        action='store_true',
                        help="use the 'hardcoded' directories in the script")
    args = parser.parse_args()

    if len(args.dirs) > 0:
        directories = args.dirs
    elif not args.script_dirs:
        parser.error("No action requested; add -d/--dirs [dir ...] or -sd/--script_dirs.")

    # Run the program
    failed_paths = []
    fps = []
    for dir_ in directories:
        if os.path.isdir(dir_):
            fps.append(run(dir_))
        else:
            failed_paths.append(dir_)

    print("Written to: {}".format(fps))
