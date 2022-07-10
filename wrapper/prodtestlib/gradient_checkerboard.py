"""gradient_checkerboard.c python wrapper file for structs and functions, part of the prodtestlib.dll library."""

import ctypes as c
from utils.image import extract
from wrapper.fpc_c_core.fpc_sensor_info import ProductType, DeadPixelsInfo
from wrapper.prodtestlib.prodtestlib_common import FPCErrorCode
from wrapper.wrapper_common import CtypesEnum, ErrorCode
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


class GradientCheckerboardConfig(c.Structure):
    """Equivalent to prodtestlib.dll's fpc_gradient_checkerboard_config_t"""
    _fields_ = [
        # Sensor configurations
        ("area_height", c.c_uint),
        ("area_width", c.c_uint),
        ("pixel_count", c.c_uint),  # Number of pixels

        # Finger detect areas
        ("sub_area_height", c.c_uint),
        ("sub_area_width", c.c_uint),
        ("sub_area_nbr_rows", c.c_uint),
        ("sub_area_nbr_cols", c.c_uint),
        ("sub_areas_row", c.c_uint8 * MAX_NBR_SUB_AREA_ROWS),
        ("sub_areas_col", c.c_uint8 * MAX_NBR_SUB_AREA_COLS),

        # Test criteria
        ("max_deviation", c.c_uint),
        ("pixel_errors_upper_limit", c.c_uint),
        ("sub_areas_errors_upper_limit", c.c_uint),
        ("histogram_slot_length", c.c_uint),
        ("CB_type1_median_min", c.c_uint),
        ("CB_type1_median_max", c.c_uint),
        ("CB_type2_median_min", c.c_uint),
        ("CB_type2_median_max", c.c_uint),
        ("ICB_type1_median_min", c.c_uint),
        ("ICB_type1_median_max", c.c_uint),
        ("ICB_type2_median_min", c.c_uint),
        ("ICB_type2_median_max", c.c_uint),

        ("histogram_deviation", c.c_uint8)
    ]

    def __init__(self):
        # The arrays found in this struct have their corresponding size.
        # IMPORTANT: the name is the same as the array with the suffix '_SIZE'.
        # This is used in io_csv.retrieve_std_values_from_struct
        self.sub_areas_row_SIZE = MAX_NBR_SUB_AREA_ROWS
        self.sub_areas_col_SIZE = MAX_NBR_SUB_AREA_COLS
        # Initialize like normal
        super(GradientCheckerboardConfig, self).__init__()


class GradientCheckerboardResult(c.Structure):
    """Equivalent to prodtestlib.dll's fpc_gradient_checkerboard_result_t"""
    _fields_ = [
        ("pixel_errors", c.c_uint),                   # Total number of errors
        ("sub_area_errors", c.c_uint),                # Errors in sub areas
        ("type1_deviation_max", c.c_uint),            # Worst pixel diff vs median
        ("type2_deviation_max", c.c_uint),            # Worst pixel diff vs median
        ("type1_min_histogram_median", c.c_uint8),
        ("type2_min_histogram_median", c.c_uint8),
        ("type1_max_histogram_median", c.c_uint8),
        ("type2_max_histogram_median", c.c_uint8),

        # Test result
        ("result", c.c_uint),                 # result bits using fpc_checkerboard_error_type_t
        ("pass", c.c_bool),
    ]

    def __init__(self):
        # A dictionary used to know for which values a histogram is interesting. The min and max values can be added if
        # a min and/or max line is wanted in the histogram. If a value is interesting together with another value, the
        # other value can be added to the list 'combine_figs'
        self.histogram = {"type1_deviation_max": {"min": None,                              # no min/max
                                                  "max": None,
                                                  "range": [0, 25],
                                                  "combine_figs": ["type2_deviation_max"],
                                                  "combine_figs_name": "deviation_max",
                                                  },
                          "type2_deviation_max": {"min": None,                              # no min/max
                                                  "max": None,
                                                  "range": [0, 25],
                                                  "combine_figs": ["type1_deviation_max"],
                                                  "combine_figs_name": "deviation_max",
                                                  },
                          "type1_min_histogram_median": {"min": None,
                                                         "max": None,
                                                         "range": None,
                                                         "combine_figs": ["type2_min_histogram_median"],
                                                         "combine_figs_name": "min_histogram_median",
                                                         },
                          "type2_min_histogram_median": {"min": None,
                                                         "max": None,
                                                         "range": None,
                                                         "combine_figs": ["type1_min_histogram_median"],
                                                         "combine_figs_name": "min_histogram_median",
                                                         },
                          "type1_max_histogram_median": {"min": None,
                                                         "max": None,
                                                         "range": None,
                                                         "combine_figs": ["type2_max_histogram_median"],
                                                         "combine_figs_name": "max_histogram_median",
                                                         },
                          "type2_max_histogram_median": {"min": None,
                                                         "max": None,
                                                         "range": None,
                                                         "combine_figs": ["type1_max_histogram_median"],
                                                         "combine_figs_name": "max_histogram_median",
                                                         }}
        # Initialize like normal
        super(GradientCheckerboardResult, self).__init__()


class TestLevelT(CtypesEnum):
    """Equivalent to prodtestlib.dll's fpc_test_level_t"""
    FPC_TEST_LEVEL_MTS = 0
    FPC_TEST_LEVEL_ITS = 1


def init_gradient_checkerboard_test(libc, product_type, hwid, test_package=None):
    """Prepares a config struct of type fpc_gradient_checkerboard_config_t,
    using the prodtestlib.dll's init_gradient_checkerboard_test

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

    test_package["config"] = GradientCheckerboardConfig()
    # Convert string representation of hex to c.c_uint16
    hwid = c.c_uint16(int(hwid, 16))
    # Fetch prodtestlib.dll function
    init_test = libc.init_gradient_checkerboard_test
    # Assign the parameter types of the prodtestlib.dll function
    init_test.argtypes = [c.POINTER(GradientCheckerboardConfig), c.c_int, c.c_uint16]
    # Assign the return type of the prodtestlib.dll function
    init_test.restype = c.c_uint

    # Run the prodtestlib.dll function
    error_code = init_test(c.byref(test_package["config"]), c.c_int(ProductType[product_type].value), hwid)

    # Fill test_package with remaining information
    if "dead_pixels_list" not in test_package:
        test_package["dead_pixels_list"] = DeadPixelsInfo()

    test_package["native_function"] = init_gradient_checkerboard_test.__name__
    test_package["error_code"] = FPCErrorCode.reverse_lookup(error_code)

    return test_package


def init_gradient_checkerboard_test_based_on_testlevel(libc, product_type, hwid, test_level, test_package=None):
    """Prepares a config struct of type fpc_gradient_checkerboard_config_t,
    using the prodtestlib.dll's init_gradient_checkerboard_test_based_on_testlevel

    :param libc: the c-library object used to retrieve the c-functions
    :type libc: c-library object
    :param product_type: the product type code
    :type product_type: str
    :param hwid: the hardware id, hex
    :type hwid: str
    :param test_level: test level MTS or ITS
    :type test_level: TestLevelT
    :param test_package: dictionary containing config, result, error_code etc
    :type test_package: dictionary
    :return: test_package
    :rtype: dictionary
    """

    if test_package is None:
        test_package = {}

    test_package["config"] = GradientCheckerboardConfig()
    hwid = c.c_uint16(int(hwid, 16))
    init_test = libc.init_gradient_checkerboard_test_based_on_testlevel
    init_test.argtypes = [c.POINTER(GradientCheckerboardConfig), c.c_uint, c.c_uint16, c.c_uint]
    init_test.restype = c.c_uint

    error_code = init_test(c.byref(test_package["config"]), c.c_uint(ProductType[product_type].value), hwid, test_level)

    # Fill test_package with remaining information
    if "dead_pixels_list" not in test_package:
        test_package["dead_pixels_list"] = DeadPixelsInfo()

    test_package["native_function"] = init_gradient_checkerboard_test_based_on_testlevel.__name__
    test_package["error_code"] = FPCErrorCode.reverse_lookup(error_code)

    return test_package


def gradient_checkerboard_test(libc, image, select_test, test_package):
    """Runs the prodtestlib.dll's function gradient_checkerboard_test

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
    test_package["result"] = GradientCheckerboardResult()
    image_data = extract(image)

    # Fix histogram min/max values ICB_type1_median_min
    if select_test is FpcCheckerboardT.FPC_IMAGE_TEST_CHESS_INV:
        test_package["result"].histogram["type1_min_histogram_median"]["min"] = \
            test_package["config"].ICB_type1_median_min
        test_package["result"].histogram["type1_min_histogram_median"]["max"] = \
            test_package["config"].ICB_type1_median_max
        test_package["result"].histogram["type2_min_histogram_median"]["min"] = \
            test_package["config"].ICB_type2_median_min
        test_package["result"].histogram["type2_min_histogram_median"]["max"] = \
            test_package["config"].ICB_type2_median_max
        test_package["result"].histogram["type1_max_histogram_median"]["min"] = \
            test_package["config"].ICB_type1_median_min
        test_package["result"].histogram["type1_max_histogram_median"]["max"] = \
            test_package["config"].ICB_type1_median_max
        test_package["result"].histogram["type2_max_histogram_median"]["min"] = \
            test_package["config"].ICB_type2_median_min
        test_package["result"].histogram["type2_max_histogram_median"]["max"] = \
            test_package["config"].ICB_type2_median_max

    elif select_test is FpcCheckerboardT.FPC_IMAGE_TEST_CHESS:
        test_package["result"].histogram["type1_min_histogram_median"]["min"] = \
            test_package["config"].CB_type1_median_min
        test_package["result"].histogram["type1_min_histogram_median"]["max"] = \
            test_package["config"].CB_type1_median_max
        test_package["result"].histogram["type2_min_histogram_median"]["min"] = \
            test_package["config"].CB_type2_median_min
        test_package["result"].histogram["type2_min_histogram_median"]["max"] = \
            test_package["config"].CB_type2_median_max
        test_package["result"].histogram["type1_max_histogram_median"]["min"] = \
            test_package["config"].CB_type1_median_min
        test_package["result"].histogram["type1_max_histogram_median"]["max"] = \
            test_package["config"].CB_type1_median_max
        test_package["result"].histogram["type2_max_histogram_median"]["min"] = \
            test_package["config"].CB_type2_median_min
        test_package["result"].histogram["type2_max_histogram_median"]["max"] = \
            test_package["config"].CB_type2_median_max

    # If previous error, do not run test
    if not (test_package["error_code"] is FPCErrorCode.FPC_OK or ErrorCode.OK):
        return test_package

    # Retrieve test from prodtestlib and prepare it
    run_test = libc.gradient_checkerboard_test
    run_test.argtypes = [c.POINTER(c.c_uint8),
                         c.c_uint,
                         c.POINTER(GradientCheckerboardConfig),
                         c.POINTER(GradientCheckerboardResult),
                         c.POINTER(DeadPixelsInfo)]
    run_test.resttype = c.c_uint

    # Run test
    error_code = run_test(image_data["buffer_p"],
                          c.c_uint(select_test.value),
                          c.byref(test_package["config"]),
                          c.byref(test_package["result"]),
                          c.byref(test_package["dead_pixels_list"]))

    test_package["error_code"] = FPCErrorCode.reverse_lookup(error_code)
    test_package["native_function"] = gradient_checkerboard_test.__name__
    return test_package
