"""Count the number of defective pixels

Counts the number of unique defective pixels by running checkerboard_test, gradient_checkerboard and
reset_pixel.
"""
import argparse
import os

from utils import from_files, histogram, test_analyze
from utils import io_csv as csv
from utils.utils_common import ErrorCode
from utils.utils_common import update_time_date_stamp, print_progress_bar
from wrapper import init_wrapper
from wrapper.prodtestlib.common_checkerboard import FpcCheckerboardT
from wrapper.prodtestlib.prodtestlib_common import FPCErrorCode
from wrapper.run_native_test import run_gradient_checkerboard, run_reset_pixel

libc = None


def run_defective_pixels_gradient(check_image,
                                  inv_check_image,
                                  reset_image,
                                  product_type,
                                  hwid,
                                  test_seq_pack):
    """Run the defective pixels test sequence; checkerboard, inverted checkerboard and reset pixel

    Run the three native tests sequentially, checkerboard, inverted checkerboard and reset pixel. Add them to the dict
    test_sequence_package and calculate whether the test sequence passes or fails.

    :param check_image: the checkerboard image file path
    :type check_image: str
    :param inv_check_image: the inverted checkerboard image file path
    :type inv_check_image: str
    :param reset_image: the reset image file path
    :type reset_image: str
    :param product_type: the product type
    :type product_type: str
    :param hwid: the hardware id
    :type hwid: str (hex)
    :param test_seq_pack: test_sequence_package containing test_sequence name, test_id, and list of test_packages
    :type test_seq_pack: dictionary
    :return: test_sequence_package
    :rtype: dict
    """

    if "test_sequence" not in test_seq_pack:
        # Used for creating the output file
        test_seq_pack["test_sequence"] = "defective_pixel"

    if "test_packages" not in test_seq_pack:
        # Each native test produces a separate test_package added to the following list
        test_seq_pack["test_packages"] = []

    # Save the image file paths
    test_seq_pack["files"] = [check_image, inv_check_image, reset_image]

    # Save relevant information
    test_seq_pack["product_type"] = product_type
    test_seq_pack["hwid"] = hwid

    # Run the checkerboard test
    test_seq_pack["test_packages"].append(
        run_gradient_checkerboard(libc, check_image, product_type, hwid))

    # Run the inverted checkerboard test
    test_seq_pack["test_packages"].append(
        run_gradient_checkerboard(libc,
                                  inv_check_image,
                                  product_type,
                                  hwid,
                                  FpcCheckerboardT.FPC_IMAGE_TEST_CHESS_INV,
                                  # Send a copy of previous test_package to pass
                                  #  dead_pixels_list to next native function
                                  test_seq_pack["test_packages"][-1].copy()))

    # Run the reset pixel test
    test_seq_pack["test_packages"].append(
        run_reset_pixel(libc,
                        reset_image,
                        # Send a copy of previous test_package to pass
                        #  dead_pixels_list to next native function
                        test_seq_pack["test_packages"][-1].copy()))

    # Check if the test sequence passed and if there is an error
    test_seq_pack["pass"] = True
    test_seq_pack["error_code"] = []
    for tp in test_seq_pack["test_packages"]:

        if not getattr(tp["result"], "pass"):
            test_seq_pack["pass"] = False

        if tp["error_code"] is not FPCErrorCode.FPC_OK:
            test_seq_pack["error_code"].append(tp["error_code"])

    if test_seq_pack["pass"]:
        # Check if the total number of dead pixels has not passed dead_pixels_max
        if test_seq_pack["test_packages"][-1]["dead_pixels_list"].num_dead_pixels > test_seq_pack["dead_pixels_max"]:
            test_seq_pack["pass"] = False

    return test_seq_pack


def run(dir_path, product_type_=None, hwid_=None):
    """Run defective_pixels_gradient test on all individual logs in the folder provided

    :param dir_path: path to the folder containing the images and log files
    :type dir_path: str
    :param product_type_: the product type
    :type product_type_: str
    :param hwid_: the hardware id
    :type hwid_: str (hex)
    :return: the csv file path
    :rtype: str
    """
    # Create a new unique id time_stamp
    update_time_date_stamp()

    seq_packs = []
    analyze_container = {"missing_files": [],
                         "not_matched": None,
                         "no_hwid": [],
                         "no_product_type": []}

    print("Run defective_pixel_gradient_test...")
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

    checker_poss = ["checker.png", "CheckerboardImage.png"]
    checker_inv_poss = ["checker_inv.png", "InvertedCheckerboardImage.png"]
    reset_poss = ["reset.png", "ResetImage.png"]

    print("\tRun the test")
    print_progress_bar(0, len(logs), "\t")
    cnt = 0
    for id_, vals in logs.items():
        cnt += 1
        print_progress_bar(0 + cnt, len(logs), "\t")
        if id_ == "not_matched":
            # This contains the list of 'not' matched files
            continue

        # Check that the capture contains all relevant files and information
        checker_image, checker_inv_image, reset_image = None, None, None

        for key in checker_poss:
            if key in vals:
                checker_image = vals[key]
                break

        for key in checker_inv_poss:
            if key in vals:
                checker_inv_image = vals[key]
                break

        for key in reset_poss:
            if key in vals:
                reset_image = vals[key]
                break

        hwid = vals["hwid"]
        product_type = vals["product_type"]

        if hwid is None:
            if hwid_ is None:
                analyze_container["no_hwid"].append(id_)
                continue
            else:
                hwid = hwid_

        if product_type is None:
            if product_type_ is None:
                analyze_container["no_product_type"].append(id_)
                continue
            else:
                product_type = product_type_

        if any([element is None for element in [checker_image, checker_inv_image, reset_image]]):
            # This capture does not contain all relevant files necessary to run defective pixel
            analyze_container["missing_files"].append(id_)
            continue

        # Run the defective pixel test for each capture
        seq_packs.append(run_defective_pixels_gradient(checker_image,
                                                       checker_inv_image,
                                                       reset_image,
                                                       product_type,
                                                       hwid,
                                                       {"test_id": id_,
                                                        "dead_pixels_max": 8}))

    # Post-test
    if (len(analyze_container["missing_files"])) > 0:
        print("\t\t# of tests without all files necessary: {}".
              format(len(analyze_container["missing_files"])))
        # if this number is higher than expected, make sure that the parser can handle the file_name format for the
        # directory provided (in utils.from_files.retrieve_directory_content)

    if len(analyze_container["no_hwid"]) > 0:
        print("\t\t# of tests without hwid: {}".
              format(len(analyze_container["no_hwid"])))

    if len(analyze_container["no_product_type"]) > 0:
        print("\t\t# of tests without product_type: {}".
              format(len(analyze_container["no_product_type"])))

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

    print("\tCreate histograms...")
    # Create histograms for the relevant results
    fps = histogram.create_from_test_seq_packs(seq_packs)
    print("\t\t{} histograms created".format(len(fps)))

    # Create histograms with other scaling by using the scale code 0, 1, 2 or 3:
    # If 0: scale 0-255. If 1: use provided range if not None ("range", found in histogram). If 2: ±INTERVAL_SIZE/2
    # around the maximum value (INTERVAL_SIZE found in histogram.py). If 3: automatic scaling.
    #
    # Create histograms without combining figures, set combine_figs=False
    #
    # histogram.create_from_test_seq_packs(seq_packs, scale=3, combine_figs=False)

    # Initialize the csv file by passing any test_sequence_package of the correct format
    # (i.e. the last test_sequence_package like below)
    print("\tWrite results to csv file...")
    fp = csv.init_write_test_seq_pack(seq_packs[-1])

    for seq_pack in seq_packs:
        # Write the results of the defective pixels test
        csv.write_test_seq_pack(seq_pack, fp)

    csv.write_top_of_file(analyze_container, fp, "Defective pixel gradient test", "", "", "Directory: {}"
                          .format(dir_path))

    print("\t\tResults written to csv file: {}".format(fp))

    return fp

if __name__ == "__main__":
    # 'Hardcoded' directories
    directories = ["C:\\Hugo_documents\\logs\\1245_TSMC+SMIC\\SMIC_20160913"]

    # Parse user-input
    parser = argparse.ArgumentParser(description="Run the defective_pixels_gradient test on a directory of "
                                                 "logs and images")
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
    parser.add_argument('--hwid',
                        nargs=1,
                        help="the hwid used when not found in the logs")
    parser.add_argument('--product_type',
                        nargs=1,
                        help="the product_type used when not found in the logs")
    args = parser.parse_args()

    if len(args.dirs) > 0:
        directories = args.dirs
    elif not args.script_dirs:
        parser.error("No action requested; add -d/--dirs [dir ...] or -sd/--script_dirs.")

    if args.product_type is not None:
        product_type = args.product_type[0]
    else:
        product_type = None

    if args.hwid is not None:
        hwid = args.hwid[0]
    else:
        hwid = None

    if args.mtt_version is not None:
        version = args.mtt_version[0]
    else:
        version = None

    # Run the program
    libc = init_wrapper.load_mtt_version(version)
    failed_paths = []
    for dir_ in directories:
        if os.path.isdir(dir_):
            run(dir_, product_type, hwid)
        else:
            failed_paths.append(dir_)

    if len(failed_paths) > 0:
        print("The following directories do not exist: {}".format(failed_paths))

    # fp_1 = run("C:\\Hugo Documents\\logs\\8.1\\MKMO6OE", "PRODUCT_TYPE_FPC1245", "0x1401")
    # fp_2 = run("C:\\Hugo Documents\\MTT 11.0\\MKN4JQF", "PRODUCT_TYPE_FPC1245", "0x140B")
    # fp_3 = run("C:\\Hugo Documents\\logs\\amsterdam_1245_20160914\\SMIC_20160913", "PRODUCT_TYPE_FPC1245", "0x140B")
    # fp_4 = run("C:\\Hugo Documents\\logs\\amsterdam_1245_20160914\\TSMC_20160913", "PRODUCT_TYPE_FPC1245", "0x1401")
    # fp_5 = run("C:\\Hugo Documents\\logs\\1245_TSMC+SMIC\\SMIC_20160913", "PRODUCT_TYPE_FPC1245", "0x140B")
    # fp_5 = run("C:\\Hugo Documents\\logs\\1245_TSMC+SMIC\\SMIC_20160913")
    # fp_4 = run("C:\\Hugo Documents\\logs\\1245_TSMC+SMIC\\TSMC_20160913", "PRODUCT_TYPE_FPC1245", "0x1401")