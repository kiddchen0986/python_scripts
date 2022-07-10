"""Run the capacitance test, by calculating the capacitance and then calculating blob"""
import argparse
import os
from enum import Enum

from utils import from_files, histogram, image, test_analyze
from utils import io_csv as csv
from utils.utils_common import ErrorCode
from utils.utils_common import update_time_date_stamp, print_progress_bar
from wrapper import init_wrapper
from wrapper import run_native_test
from wrapper.prodtestlib.prodtestlib_common import FPCErrorCode

libc = None


class Error(Enum):
    OK = 0
    PIXEL_GAIN_NONE = 1
    HWID_NONE = 2
    PRODUCT_TYPE = 2


def run_capacitance(white_image,
                    painted_image,
                    pixel_gain,
                    test_seq_pack,
                    max_pixel_gain=None,
                    companion_chip_type=None):
    """Run the capacitance test, by calculating the capacitance and then calculating blob.

    Add the test result to the test_sequence_package, even though it is only one result struct

    :param white_image: the white image file path
    :type white_image: str
    :param painted_image: the painted image file path
    :type painted_image: str
    :param pixel_gain: the pixel gain
    :type pixel_gain: number
    :param test_seq_pack: test_sequence_package containing test_sequence name, test_id, and list of test_packages
    :type test_seq_pack: dictionary
    :param max_pixel_gain: the max pixel gain
    :type max_pixel_gain: number
    :param companion_chip_type: the companion chip
    :type companion_chip_type: wrapper.fpc_c_core.fpc_sensor_info.CompanionChipType
    :return: test_sequence_package
    :rtype: dict
    """

    if "test_sequence" not in test_seq_pack:
        # Used for creating the output file
        test_seq_pack["test_sequence"] = "capacitance"

    if "test_packages" not in test_seq_pack:
        # Each native test produces a separate test_package added to the following list
        test_seq_pack["test_packages"] = []

    # Save the image file paths
    test_seq_pack["files"] = [white_image, painted_image]

    # Save relevant information
    test_seq_pack["pixel_gain"] = pixel_gain

    # Run capacitance test
    test_seq_pack["test_packages"].append(
        run_native_test.run_blob(libc,
                                 white_image,
                                 painted_image,
                                 pixel_gain,
                                 max_pixel_gain=max_pixel_gain,
                                 companion_chip_type=companion_chip_type))

    # Check if the test sequence passed and if there is an error
    test_seq_pack["pass"] = True
    test_seq_pack["error_code"] = []
    for tp in test_seq_pack["test_packages"]:

        if not getattr(tp["result"], "pass"):
            test_seq_pack["pass"] = False

        if tp["error_code"] is not FPCErrorCode.FPC_OK:
            test_seq_pack["error_code"].append(tp["error_code"])

    return test_seq_pack


def run(dir_path, pixel_gain=None, ceiling=None, floor=None):
    """Run capacitance test on all individual logs in the folder provided

    :param dir_path: path to the folder containing the images and log files
    :type dir_path: str
    :param pixel_gain: the pixel_gain
    :type pixel_gain: int
    :param ceiling: max capacitance value for capacitance_image (for post-test processing)
    :type ceiling: float
    :param floor: min capacitance value for capacitance_image (for post-test processing)
    :type floor: float
    :return: the csv file path
    :rtype: str
    """
    error = Error.OK

    # Create a new unique id time_stamp
    update_time_date_stamp()

    if floor is None:
        floor = 0.2

    if ceiling is None:
        ceiling = 0.9

    seq_packs = []
    analyze_container = {"missing_files": [],
                         "not_matched": None,
                         "without_pixel_gain": []}

    print("Run capacitance test")
    logs = from_files.retrieve_directory_content(dir_path)
    if logs is ErrorCode.IS_NOT_DIRECTORY:
        print("The directory {} is not a directory".format(dir_path))
        return None

    analyze_container["not_matched"] = logs["not_matched"]
    try:
        print("\t\tNot matched files: {}".format(analyze_container["not_matched"]))
    except UnicodeEncodeError:
        print("\t\t# of not matched files: {} (some file name/s contain undefined characters)".
              format(len(analyze_container["not_matched"])))

    white_poss = ["white.png", "White.png"]
    painted_poss = ["painted.png", "Painted.png"]

    print("\tRun the test")
    print_progress_bar(0, len(logs), "\t")
    cnt = 0
    for id_, vals in logs.items():
        cnt += 1
        print_progress_bar(cnt, len(logs), "\t")
        if id_ == "not_matched":
            # This contains the list of 'not' matched files
            continue

        error = Error.OK

        # Check that the capture contains all relevant files
        white_image, painted_image = None, None

        for key in white_poss:
            if key in vals:
                white_image = vals[key]
                break

        for key in painted_poss:
            if key in vals:
                painted_image = vals[key]
                break

        if any([image_ is None for image_ in [white_image, painted_image]]):
            # This capture does not contain all relevant files necessary to run capacitance test
            analyze_container["missing_files"].append(id_)
            continue

        if pixel_gain is None:
            pixel_gain_ = vals["pixel_gain"]
        else:
            pixel_gain_ = pixel_gain

        if pixel_gain_ is None:
            error = Error.PIXEL_GAIN_NONE
            analyze_container["without_pixel_gain"].append(id_)
            continue

        # Run the defective pixel test for each capture
        seq_packs.append(run_capacitance(white_image, painted_image, pixel_gain_, {"test_id": id_}))

    # Post-test
    if (len(analyze_container["missing_files"])) > 0:
        print("\t\t# of tests without all files necessary: {}".
              format(len(analyze_container["missing_files"])))
        # if this number is higher than expected, make sure that the parser can handle the file_name format for the
        # directory provided (in utils.from_files.retrieve_directory_content)

    if len(analyze_container["without_pixel_gain"]) > 0:
        print("\t\t# of tests without pixel_gain: {}".
              format(len(analyze_container["without_pixel_gain"])))

    if len(seq_packs) is 0:
        print("\tNo tests were executed...")
        return None
    else:
        print("\t\t# of tests executed: {}".format(len(seq_packs)))

    print("\tAnalyzing results...")
    analyze_container = test_analyze.calculate_yield(seq_packs, analyze_container)
    analyze_container = test_analyze.compile_errors(seq_packs, analyze_container)
    # Print yield
    print("\t\tYield = {}".format(analyze_container["yield"]))
    # Print errors
    print("\t\tCompiled number of errors = {}".format(analyze_container["nbr_errors"]))

    # Create histograms for the relevant results
    print("\tCreate histograms...")
    fps = histogram.create_from_test_seq_packs(seq_packs, scale=1)
    print("\t\t{} histograms created".format(len(fps)))

    # Create histograms with other scaling by using the scale code 0, 1, 2 or 3:
    # If 0: scale 0-255. If 1: use provided range if not None ("range", found in histogram). If 2: ±INTERVAL_SIZE/2
    # around the maximum value (INTERVAL_SIZE found in histogram.py). If 3: automatic scaling.
    #
    # Create histograms without combining figures, set combine_figs=False
    #
    # histogram.create_from_test_seq_packs(seq_packs, scale=3, combine_figs=False)

    # Save the capacitance_image_float with new ceiling/floor
    print("\tNormalizing capacitance images...")
    # The floor and ceiling value can be set to a custom value
    fp = image.save_normalized_cap_image_from_test_seq_packs(seq_packs, floor=floor, ceiling=ceiling)
    print("\t\tSaved to: {}".format(fp))

    # Initialize the csv file by passing any test_sequence_package of the correct format
    # (i.e. the last test_sequence_package like below)
    print("\tWrite results to csv file...")
    fp = csv.init_write_test_seq_pack(seq_packs[-1], dead_pixels_list=False)

    for seq_pack in seq_packs:
        # Write the results of the defective pixels test
        csv.write_test_seq_pack(seq_pack, fp, dead_pixels_list=False)

    if error is Error.OK:
        csv.write_top_of_file(analyze_container,
                              fp,
                              "Capacitance Test",
                              "", "",
                              "Directory: {}".format(dir_path))
    else:
        csv.write_top_of_file(analyze_container,
                              fp,
                              "Capacitance Test",
                              "", "",
                              "Directory: {}".format(dir_path),
                              "", "",
                              error)

    print("\t\tResults written to csv file: {}".format(fp))

    return fp


if __name__ == "__main__":
    # 'Hardcoded' directories
    # directories = ["C:\\Hugo_documents\\logs\\FP033_test300ea_MTT12.0\\something_37pcs"]
    directories = ["C:\\Hugo_documents\\logs\\1245"]

    # Parse user-input
    parser = argparse.ArgumentParser(description="Run the capacitance test on a directory of logs and images")
    parser.add_argument('-v', '--mtt_version',
                        type=float,
                        nargs=1,
                        help="the mtt_version to be loaded (if not specified, the newest version is used)")
    parser.add_argument('-d', '--dirs',
                        type=str,
                        nargs='+',
                        help="the directory for which the module should be run",
                        default=[])
    parser.add_argument('-sd', '--script_dirs',
                        action='store_true',
                        help="use the 'hardcoded' directories in the script")
    parser.add_argument('-p', '--pixel_gain',
                        nargs=1,
                        help="the pixel_gain used when not found in the logs",
                        default=None)
    parser.add_argument('--floor',
                        nargs=1,
                        type=float,
                        help="the minimum value when normalizing capacitance image",
                        default=None)
    parser.add_argument('--ceiling',
                        nargs=1,
                        type=float,
                        help="the maximum value when normalizing capacitance image",
                        default=None)
    args = parser.parse_args()

    if len(args.dirs) > 0:
        directories = args.dirs
    elif not args.script_dirs:
        parser.error("No action requested; add -d/--dirs [dir ...] or -sd/--script_dirs.")

    if args.pixel_gain is not None:
        pixel_gain = args.pixel_gain[0]
    else:
        pixel_gain = None

    if args.ceiling is not None:
        ceiling = args.ceiling[0]
    else:
        ceiling = None

    if args.floor is not None:
        floor = args.floor[0]
    else:
        floor = None

    if args.mtt_version is not None:
        version = args.mtt_version[0]
    else:
        version = None

    # Run the program
    libc = init_wrapper.load_mtt_version(version)
    failed_paths = []
    for dir_ in directories:
        if os.path.isdir(dir_):
            run(dir_, pixel_gain=pixel_gain, ceiling=ceiling, floor=floor)
        else:
            failed_paths.append(dir_)

    if len(failed_paths) > 0:
        print("The following directories do not exist: {}".format(failed_paths))

    # libc = init_wrapper.load_mtt_version(11.0)

    # fp = run("C:\\Hugo_documents\\logs\\FP033_test300ea_MTT12.0\\something_37pcs")
    # fp_3 = run("C:\\Hugo_documents\\logs\\amsterdam_1245_20160914\\SMIC_20160913", pixel_gain=3)
