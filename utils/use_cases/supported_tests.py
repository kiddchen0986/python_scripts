"""Check which tests that are supported for a sensor"""
import os
import sys
import re
from utils import from_files
from wrapper import init_wrapper
import argparse


def run(sensor, v=None):
    """Checks which tests that are supported for that specific sensor, in that specific MTT version

    :param sensor: the sensor name
    :type sensor: str
    :param v: the MTT version
    :type v: float
    """
    sequencer_files_directory = os.path.join(init_wrapper.retrieve_path_to_mtt_version(v), "SequencerFiles")
    print("sequencer_files_directory: {}".format(sequencer_files_directory))

    pattern = r'(\d{4})'
    search_obj = re.search(pattern, sensor)

    if search_obj is None:
        sys.exit("Could not parse the parameter sensor value: {} (expected 4 consecutive digits)".format(sensor))

    file_name = "FPC{}_sequence.xml".format(search_obj.group(0))
    file_path = os.path.join(sequencer_files_directory, file_name)

    if not os.path.isfile(file_path):
        sys.exit("Could not find file: {}".format(file_path))

    parsed = from_files.parse_xml(file_path)
    for test in parsed["children"]:
        print(test["attr"])


if __name__ == "__main__":
    # Parse user-input
    parser = argparse.ArgumentParser(description="Retrieve which tests are supported for a sensor")
    parser.add_argument('sensor',
                        metavar='S',
                        type=str,
                        help="the sensor")
    parser.add_argument('-v', '--mtt_version',
                        type=float,
                        nargs=1,
                        help="the mtt_version to be loaded (if not specified, the newest version is used)",
                        )
    args = parser.parse_args()

    if args.mtt_version is not None:
        version = args.mtt_version[0]
    else:
        version = None

    # Run the program
    run(args.sensor, version)
