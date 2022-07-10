"""checkerboard.c python wrapper file for structs and functions, part of the prodtestlib.dll library."""

import ctypes as c

from utils.image import extract
from wrapper.fpc_c_core.fpc_sensor_info import ProductType, DeadPixelsInfo
from wrapper.prodtestlib.prodtestlib_common import FPCErrorCode
from wrapper.wrapper_common import ErrorCode
from wrapper.prodtestlib.common_checkerboard import FpcCheckerboardT

"""ctypes types:
uint32_t    = c_uint32
uint16_t    = c_uint16
uint8_t     = c_uint8
bool        = c_bool
"""

MAX_NBR_ROWS = 256
MAX_NBR_COLS = 256
MAX_NBR_SUB_AREA_ROWS = 4
MAX_NBR_SUB_AREA_COLS = 4


class CheckerboardConfig(c.Structure):
    """Equivalent to prodtestlib.dll's fpc_checkerboard_config_t"""
    _fields_ = [
        # Sensor configurations
        ("area_height", c.c_uint32),
        ("area_width", c.c_uint32),
        ("pixel_count", c.c_uint32),  # Number of pixels

        # Finger detect areas
        ("sub_area_height", c.c_uint32),
        ("sub_area_width", c.c_uint32),
        ("sub_area_nbr_rows", c.c_uint32),
        ("sub_area_nbr_cols", c.c_uint32),
        ("sub_areas_row", c.c_uint8 * MAX_NBR_SUB_AREA_ROWS),
        ("sub_areas_col", c.c_uint8 * MAX_NBR_SUB_AREA_COLS),

        # Test criteria
        ("max_deviation", c.c_uint32),
        ("pixel_errors_upper_limit", c.c_uint32),
        ("sub_areas_errors_upper_limit", c.c_uint32),
        ("CB_type1_median_min", c.c_uint32),
        ("CB_type1_median_max", c.c_uint32),
        ("CB_type2_median_min", c.c_uint32),
        ("CB_type2_median_max", c.c_uint32),
        ("ICB_type1_median_min", c.c_uint32),
        ("ICB_type1_median_max", c.c_uint32),
        ("ICB_type2_median_min", c.c_uint32),
        ("ICB_type2_median_max", c.c_uint32)
    ]

    def __init__(self):
        # The arrays found in this struct have their corresponding size.
        # IMPORTANT: the name is the same as the array with the suffix '_SIZE'.
        # This is used in io_csv.retrieve_std_values_from_struct
        self.sub_areas_row_SIZE = MAX_NBR_SUB_AREA_ROWS
        self.sub_areas_col_SIZE = MAX_NBR_SUB_AREA_COLS
        # Initialize like normal
        super(CheckerboardConfig, self).__init__()


class CheckerboardResult(c.Structure):
    """Equivalent to prodtestlib.dll's fpc_checkerboard_result_t"""

    _fields_ = [
        ("pixel_errors", c.c_uint32),           # Total number of errors
        ("sub_area_errors", c.c_uint32),        # Errors in sub areas
        ("type1_median", c.c_uint32),           # The median of the type 1 values
        ("type2_median", c.c_uint32),           # The median of the type 2 values
        ("type1_mean", c.c_uint32),             # The mean of the type 1 values
        ("type2_mean", c.c_uint32),             # The mean of the type 2 values
        ("type1_deviation_max", c.c_uint32),    # Worst pixel diff vs median
        ("type2_deviation_max", c.c_uint32),    # Worst pixel diff vs median

        # Test result
        ("result", c.c_uint32),                 # result bits using fpc_checkerboard_error_type_t
        ("pass", c.c_bool),

        # Extended information
        ("pixel_errors_per_row", c.c_uint8 * MAX_NBR_ROWS),  # Sum of pixel errors per row
        ("pixel_errors_per_col", c.c_uint8 * MAX_NBR_COLS)   # Sum of pixel errors per column
    ]

    def __init__(self):
        # The arrays found in this struct have their corresponding size.
        # IMPORTANT: the name is the same as the array with the suffix '_SIZE'.
        # This is used in io_csv.retrieve_std_values_from_struct
        self.pixel_errors_per_row_SIZE = MAX_NBR_ROWS
        self.pixel_errors_per_col_SIZE = MAX_NBR_COLS

        # A dictionary used to know for which values a histogram is interesting. The min and max values can be added if
        # a min and/or max line is wanted in the histogram. If a value is interesting together with another value, the
        # other value can be added to the list 'combine_figs'
        self.histogram = {"type1_median": {"min": None,
                                           "max": None,
                                           "range": None,
                                           "combine_figs": ["type2_median"],
                                           "combine_figs_name": "median",
                                           },
                          "type2_median": {"min": None,
                                           "max": None,
                                           "range": None,
                                           "combine_figs": ["type1_median"],
                                           "combine_figs_name": "median",
                                           },
                          "type1_mean": {"min": None,                           # no min/max
                                         "max": None,
                                         "range": None,
                                         "combine_figs": ["type2_mean"],
                                         "combine_figs_name": "mean",
                                         },
                          "type2_mean": {"min": None,                           # no min/max
                                         "max": None,
                                         "range": None,
                                         "combine_figs": ["type1_mean"],
                                         "combine_figs_name": "mean",
                                         },
                          "type1_deviation_max": {"min": None,                  # no min/max
                                                  "max": None,
                                                  "range": None,
                                                  "combine_figs": ["type2_deviation_max"],
                                                  "combine_figs_name": "deviation_max",
                                                  "combine_figs_range": None
                                                  },
                          "type2_deviation_max": {"min": None,                  # no min/max
                                                  "max": None,
                                                  "range": None,
                                                  "combine_figs": ["type1_deviation_max"],
                                                  "combine_figs_name": "deviation_max",
                                                  }}

        # Initialize like normal
        super(CheckerboardResult, self).__init__()


def init_checkerboard_test(libc, product_type, hwid, test_package=None):
    """Prepares a config struct of type fpc_checkerboard_config_t

    :param libc: the c-library object used to retrieve the c-functions
    :type libc: c-library object
    :param product_type: the product type code
    :type product_type: str
    :param hwid: the hardware id, hex
    :type hwid: str
    :param test_package: dictionary containing config, result, error_code etc
    :type test_package: dictionary
    :return: test_package
    :rtype: dictionary
    """

    if test_package is None:
        test_package = {}

    test_package["config"] = CheckerboardConfig()
    # Convert string representation of hex to c.c_uint16
    hwid = c.c_uint16(int(hwid, 16))
    # Fetch prodtestlib.dll function
    init_test = libc.init_checkerboard_test
    # Assign the parameter types of the prodtestlib.dll function
    init_test.argtypes = [c.POINTER(CheckerboardConfig), c.c_uint32, c.c_uint16]
    # Assign the return type of the prodtestlib.dll function
    init_test.restype = c.c_uint

    # Run the prodtestlib.dll function
    error_code = init_test(c.byref(test_package["config"]), c.c_uint(ProductType[product_type].value), hwid)

    # Fill test_package with remaining information
    if "dead_pixels_list" not in test_package:
        test_package["dead_pixels_list"] = DeadPixelsInfo()

    test_package["native_function"] = init_checkerboard_test.__name__
    test_package["error_code"] = FPCErrorCode.reverse_lookup(error_code)

    return test_package


def checkerboard_test(libc, image, select_test, test_package):
    """Runs the prodtestlib.dll's function checkerboard_test

    :param libc: the c-library object used to retrieve the c-functions
    :type libc: c-library object
    :param image: the checkerboard image file path
    :type image: str
    :param select_test: the test type
    :type select_test: FpcCheckerboardT
    :param test_package: dictionary containing config, result, error_code etc
    :type test_package: dictionary
    :return: test_package
    :rtype: dictionary
    """
    # If image file path not added to test_package; add it
    if "files" not in test_package:
        test_package["files"] = [image]

    # Prepare components for test
    test_package["result"] = CheckerboardResult()
    image_data = extract(image)

    # Fix histogram min/max values
    if select_test is FpcCheckerboardT.FPC_IMAGE_TEST_CHESS_INV:
        test_package["result"].histogram["type1_median"]["min"] = test_package["config"].ICB_type1_median_min
        test_package["result"].histogram["type1_median"]["max"] = test_package["config"].ICB_type1_median_max
        test_package["result"].histogram["type2_median"]["min"] = test_package["config"].ICB_type2_median_min
        test_package["result"].histogram["type2_median"]["max"] = test_package["config"].ICB_type2_median_max
        test_package["result"].histogram["type1_mean"]["min"] = test_package["config"].ICB_type1_median_min
        test_package["result"].histogram["type1_mean"]["max"] = test_package["config"].ICB_type1_median_max
        test_package["result"].histogram["type2_mean"]["min"] = test_package["config"].ICB_type2_median_min
        test_package["result"].histogram["type2_mean"]["max"] = test_package["config"].ICB_type2_median_max
    elif select_test is FpcCheckerboardT.FPC_IMAGE_TEST_CHESS:
        test_package["result"].histogram["type1_median"]["min"] = test_package["config"].CB_type1_median_min
        test_package["result"].histogram["type1_median"]["max"] = test_package["config"].CB_type1_median_max
        test_package["result"].histogram["type2_median"]["min"] = test_package["config"].CB_type2_median_min
        test_package["result"].histogram["type2_median"]["max"] = test_package["config"].CB_type2_median_max
        test_package["result"].histogram["type1_mean"]["min"] = test_package["config"].CB_type1_median_min
        test_package["result"].histogram["type1_mean"]["max"] = test_package["config"].CB_type1_median_max
        test_package["result"].histogram["type2_mean"]["min"] = test_package["config"].CB_type2_median_min
        test_package["result"].histogram["type2_mean"]["max"] = test_package["config"].CB_type2_median_max

    # If previous error, do not run test
    if not (test_package["error_code"] is FPCErrorCode.FPC_OK or test_package["error_code"] is ErrorCode.OK):
        return test_package

    # Retrieve test from prodtestlib and prepare it
    run_test = libc.checkerboard_test
    # Assign the parameter types of the prodtestlib.dll function
    run_test.argtypes = [c.POINTER(c.c_uint8),
                         c.c_uint32,
                         c.POINTER(CheckerboardConfig),
                         c.POINTER(CheckerboardResult),
                         c.POINTER(DeadPixelsInfo)]
    # Assign the return type of the prodtestlib.dll function
    run_test.resttype = c.c_uint

    # Run test
    error_code = run_test(image_data["buffer_p"],
                          c.c_uint(select_test.value),
                          c.byref(test_package["config"]),
                          c.byref(test_package["result"]),
                          c.byref(test_package["dead_pixels_list"]))

    test_package["error_code"] = FPCErrorCode.reverse_lookup(error_code)
    test_package["native_function"] = checkerboard_test.__name__
    return test_package


def checkerboard_combined_test(libc, image, image_inverted, test_package):
    """Runs the prodtestlib function checkerboard_combined_test

    :param libc: the c-library object used to retrieve the c-functions
    :type libc: c-library object
    :param image: the checkerboard image file path
    :type image: str
    :param image_inverted: the inverted checkerboard image file path
    :type image_inverted: str
    :param test_package: dictionary containing config, result, error_code etc
    :type test_package: dictionary
    :return: test_package
    :rtype: dictionary
    """

    # If image file path not added to test_package; add it
    if "files" not in test_package:
        test_package["files"] = [image]

    # Prepare components for test
    test_package["result"] = CheckerboardResult()
    result_inverted = CheckerboardResult()
    image_data = extract(image)
    image_inverted_data = extract(image_inverted)

    # If previous error, do not run test
    if not (test_package["error_code"] is FPCErrorCode.FPC_OK or test_package["error_code"] is ErrorCode.OK):
        return test_package

    # Retrieve test from prodtestlib and prepare it
    run_test = libc.checkerboard_combined_test
    # Assign the parameter types of the prodtestlib.dll function
    run_test.argtypes = [c.POINTER(c.c_uint8),
                         c.POINTER(c.c_uint8),
                         c.POINTER(DeadPixelsInfo),
                         c.c_uint16,
                         c.POINTER(CheckerboardConfig),
                         c.POINTER(CheckerboardResult),
                         c.POINTER(CheckerboardResult)]
    # Assign the return type of the prodtestlib.dll function
    run_test.resttype = c.c_uint

    # Run test
    error_code = run_test(image_data["buffer_p"],
                          image_inverted_data["buffer_p"],
                          c.byref(test_package["dead_pixels_list"]),
                          c.c_uint16(),
                          c.byref(test_package["config"]),
                          c.byref(test_package["result"]),
                          c.byref(result_inverted))

    test_package["error_code"] = FPCErrorCode.reverse_lookup(error_code)
    test_package["native_function"] = checkerboard_combined_test.__name__
    return test_package
