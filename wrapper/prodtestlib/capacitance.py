"""Module that wraps the functions and structs in the prodtestlib.dll file capacitance.c"""
import ctypes as c
import numpy as np
from utils.image import extract
from utils.from_files import retrieve_capacitance_settings
from wrapper.fpc_c_core.fpc_sensor_info import DeadPixelsInfo, CompanionChipType
from wrapper.prodtestlib.prodtestlib_common import FPCErrorCode
from wrapper.wrapper_common import ErrorCode

"""ctypes types:
uint32_t    = c_uint32
uint16_t    = c_uint16
uint8_t     = c_uint8
bool        = c_bool
"""


class PxlCtrlInfo(c.Structure):
    """Equivalent to prodtestlib.dll's fpc_pxl_ctrl_info_t"""
    _fields_ = [
        ("pixel_gain", c.c_uint8),
        ("max_pixel_gain", c.c_uint8)
    ]


class CapacitanceResult(c.Structure):
    """Equivalent to prodtestlib.dll's fpc_capacitance_result_t"""
    uint8_ptr = c.POINTER(c.c_uint8)
    float_ptr = c.POINTER(c.c_float)

    _fields_ = [
        ("min", c.c_double),
        ("min5", c.c_double),
        ("median", c.c_double),
        ("max5", c.c_double),
        ("max", c.c_double),
        ("vdd_tx", c.c_double),
        ("uniformity_level", c.c_double),
        ("signal_strength", c.c_double),
        ("capacitance_size", c.c_uint32),       # How large the capacitance to measure is, usually the image_size
        ("capacitance_image", uint8_ptr),
        ("capacitance_image_float", float_ptr)
    ]

    def __init__(self, capacity):
        # The arrays found in this struct have their corresponding size.
        # IMPORTANT: the name is the same as the array with the suffix '_SIZE'.
        # This is used in io_csv.retrieve_std_values_from_struct
        self.capacitance_image_SIZE = capacity
        self.capacitance_image_float_SIZE = capacity

        # A dictionary used to know for which values a histogram is interesting. The min and max values can be added if
        # a min and/or max line is wanted in the histogram. If a value is interesting together with another value, the
        # other value can be added to the list 'combine_figs'
        self.histogram = {"signal_strength": {"min": None,
                                              "max": None,
                                              "range": [0, 1.4],
                                              "combine_figs": [],
                                              "combine_figs_name": None,    # no combined figures interesting
                                              },
                          "uniformity_level": {"min": None,
                                               "max": None,
                                               "range": [0.05, 0.15],
                                               "combine_figs": [],
                                               "combine_figs_name": None}}  # no combined figures interesting

        # Initialize like normal
        super(CapacitanceResult, self).__init__()

        self.capacitance_image_array = np.zeros(self.capacitance_image_SIZE, dtype=np.uint8)
        self.capacitance_image_float_array = np.zeros(self.capacitance_image_float_SIZE, dtype=np.float32)
        self.capacitance_image = self.capacitance_image_array.ctypes.data_as(self.uint8_ptr)
        self.capacitance_image_float = self.capacitance_image_float_array.ctypes.data_as(self.float_ptr)


class BlobConfig(c.Structure):
    """Equivalent to prodtestlib.dll's fpc_blob_config_t"""
    _fields_ = [
        ("blob_threshold", c.c_float),
        ("max_number_of_blob_pixels", c.c_uint32)  # Higher than this will will fail the test
    ]


class BlobResult(c.Structure):
    """Equivalent to prodtestlib.dll's fpc_blob_result_t"""
    _fields_ = [
        ("number_of_blob_pixels", c.c_uint32),
        ("detection_image", c.POINTER(c.c_float)),
        ("blob_image", c.POINTER(c.c_uint8)),
        ("width", c.c_uint32),
        ("height", c.c_uint32),
        ("pass", c.c_bool)
    ]

    def __init__(self, capacity):
        # The arrays found in this struct have their corresponding size.
        # IMPORTANT: the name is the same as the array with the suffix '_SIZE'.
        # This is used in io_csv.retrieve_std_values_from_struct
        self.detection_image_SIZE = capacity
        self.blob_image_SIZE = capacity

        # A dictionary used to know for which values a histogram is interesting. The min and max values can be added if
        # a min and/or max line is wanted in the histogram. If a value is interesting together with another value, the
        # other value can be added to the list 'combine_figs'
        self.histogram = {"number_of_blob_pixels": {"min": None,
                                                    "max": None,
                                                    "range": [0, 30],
                                                    "combine_figs": [],
                                                    "combine_figs_name": None}}    # no combined figures interesting

        # Initialize like normal
        super(BlobResult, self).__init__()

        self.detection_image_array = np.zeros(self.detection_image_SIZE, dtype=np.float32)
        self.blob_image_array = np.zeros(self.blob_image_SIZE, dtype=np.uint8)
        self.detection_image = self.detection_image_array.ctypes.data_as(c.POINTER(c.c_float))
        self.blob_image = self.blob_image_array.ctypes.data_as(c.POINTER(c.c_uint8))


def does_module_pass(capacitance_result, test_package):
    """Equivalent to TestCapacitanceBase.cs function DoesModulePass(). Calculates whether the calculated capacitance
    has passed.

    :param capacitance_result: the capacitance result object
    :type capacitance_result: CapacitanceResult
    :param test_package: dictionary containing at least "product_type"
    :type test_package: dictionary
    :return: True if passes, else False
    :rtype: bool
    """
    # The function retrieve_capacitance_settings expects the key "product_type" in test_package
    test_package = retrieve_capacitance_settings(test_package)
    signal_strength = round(capacitance_result["signal_strength"], 3)

    if test_package["capacitance_settings"]["EnableSignalStrength"]:
        return test_package["capacitance_settings"]["MinSignalStrength"] < signal_strength \
               < test_package["capacitance_settings"]["MaxSignalStrength"] \
               and capacitance_result["uniformity_level"] < test_package["capacitance_settings"]["MaxUniformityLevel"]

    return capacitance_result["uniformity_level"] < test_package["capacitance_settings"]["MaxUniformityLevel"]


def calculate_capacitance(libc,
                          white_image,
                          painted_image,
                          pixel_gain,
                          test_package,
                          max_pixel_gain=None,
                          companion_chip_type=None):
    """Runs the prodtestlib.dll's function calculate_capacitance

    :param libc: the c-library object used to retrieve the c-functions
    :type libc: c-library object
    :param white_image: the white image file path
    :type white_image: str
    :param painted_image: the painted image file path
    :type painted_image: str
    :param pixel_gain: the pixel gain
    :type pixel_gain: number
    :param test_package: dictionary containing config, result, error_code etc
    :type test_package: dictionary
    :param max_pixel_gain: the max pixel gain
    :type max_pixel_gain: number
    :param companion_chip_type: the companion chip
    :type companion_chip_type: wrapper.fpc_c_core.fpc_sensor_info.CompanionChipType
    :return: test_package
    :rtype: dictionary
    """
    # If image file path not added to test_package; add it
    if "files" not in test_package:
        test_package["files"] = [white_image, painted_image]

    if isinstance(pixel_gain, str):
        pixel_gain = int(float(pixel_gain))

    # For non-provided values, assume values
    if max_pixel_gain is None:
        if pixel_gain > 3:
            max_pixel_gain = 7
        else:
            max_pixel_gain = 3

    if companion_chip_type is None:
        companion_chip_type = CompanionChipType.FPC2060

    # Prepare components for test
    test_package["white_image_data"] = extract(white_image)
    test_package["painted_image_data"] = extract(painted_image)
    test_package["capacitance_result"] = CapacitanceResult(test_package["white_image_data"]["capacity"])
    test_package["pxl_ctrl_info"] = PxlCtrlInfo(pixel_gain=pixel_gain, max_pixel_gain=max_pixel_gain)

    # If previous error, do not run test
    if not (test_package["error_code"] is FPCErrorCode.FPC_OK or test_package["error_code"] is None):
        return test_package

    # Retrieve test from prodtestlib and prepare it
    run_test = libc.calculate_capacitance

    # Assign the parameter types of the prodtestlib.dll function
    run_test.argtypes = [c.POINTER(c.c_uint8),
                         c.POINTER(c.c_uint8),
                         c.c_uint,
                         PxlCtrlInfo,
                         c.c_int32,
                         c.POINTER(CapacitanceResult)]
    # Assign the return type of the prodtestlib.dll function
    run_test.resttype = c.c_uint

    # Run test
    error_code = run_test(test_package["white_image_data"]["buffer_p"],
                          test_package["painted_image_data"]["buffer_p"],
                          companion_chip_type.value,
                          test_package["pxl_ctrl_info"],
                          c.c_int32(test_package["white_image_data"]["capacity"]),
                          c.byref(test_package["capacitance_result"]))

    test_package["error_code"] = FPCErrorCode.reverse_lookup(error_code)
    test_package["native_function"] = calculate_capacitance.__name__
    return test_package


def calculate_capacitance2():
    """NOT YET IMPLEMENTED

    :return:
    """
    pass


def init_blob_test(libc, test_package=None):
    """Prepares a config struct of type fpc_blob_config_t and calculates capacitance

    :param libc: the c-library object used to retrieve the c-functions
    :type libc: c-library object
    :param test_package: dictionary containing config, result, error_code etc
    :type test_package: dictionary
    :return: test_package
    :rtype: dictionary
    """
    if test_package is None:
        test_package = {}

    test_package["config"] = BlobConfig()
    # Fetch prodtestlib.dll function
    init_test = libc.init_blob_test
    # Assign the parameter types of the prodtestlib.dll function
    init_test.argtypes = [c.POINTER(BlobConfig)]
    # Assign the return type of the prodtestlib.dll function
    init_test.restype = c.c_uint

    # Run the prodtestlib.dll function
    error_code = init_test(c.byref(test_package["config"]))

    # Fill test_package with remaining information
    if "dead_pixels_list" not in test_package:
        test_package["dead_pixels_list"] = DeadPixelsInfo()

    test_package["native_function"] = init_blob_test.__name__
    test_package["error_code"] = FPCErrorCode.reverse_lookup(error_code)

    return test_package


def calculate_blob(libc, test_package):
    """Runs the prodtestlib.dll'sfunction calculate_blob. test_package needs "config" and "capacitance_result" for this
    to work, i.e. init_blob_test and calculate_capacitance must be run first.

    :param libc: the c-library object used to retrieve the c-functions
    :type libc: c-library object
    :param test_package: dictionary containing config, result, error_code etc. MUST HAVE config and capacitance_result
    :type test_package: dictionary
    :return: test_package
    :rtype: dictionary
    """
    # Prepare components for test
    test_package["result"] = BlobResult(test_package["white_image_data"]["capacity"])

    # If previous error, do not run test
    if not (test_package["error_code"] is FPCErrorCode.FPC_OK or test_package["error_code"] is ErrorCode.OK):
        return test_package

    # Fetch prodtestlib.dll function
    run_test = libc.calculate_blob
    # Assign the parameter types of the prodtestlib.dll function
    run_test.argtypes = [c.POINTER(c.c_float),
                         c.c_uint32,
                         c.c_uint32,
                         c.POINTER(BlobConfig),
                         c.POINTER(BlobResult),
                         c.POINTER(DeadPixelsInfo)]
    # Assign the return type of the prodtestlib.dll function
    run_test.restype = c.c_uint

    # Run the prodtestlib.dll function
    error_code = run_test(test_package["capacitance_result"].capacitance_image_float,
                          test_package["white_image_data"]["width"],
                          test_package["white_image_data"]["height"],
                          c.byref(test_package["config"]),
                          c.byref(test_package["result"]),
                          c.byref(test_package["dead_pixels_list"]))

    test_package["native_function"] = calculate_blob.__name__
    test_package["error_code"] = FPCErrorCode.reverse_lookup(error_code)

    return test_package
