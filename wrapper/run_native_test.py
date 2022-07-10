"""Functions to initialize and run native test without changing standard configuration values.
To modify configurations copy the corresponding function and modify config like in the examples in the functions."""
from wrapper.prodtestlib import checkerboard, gradient_checkerboard, reset_pixel, capacitance
from wrapper.prodtestlib.common_checkerboard import FpcCheckerboardT
from wrapper.wrapper_common import ErrorCode


def run_checkerboard(libc,
                     image,
                     product_type,
                     hwid,
                     select_test=FpcCheckerboardT.FPC_IMAGE_TEST_CHESS,
                     test_package=None):
    """Run the checkerboard test

    Run the checkerboard test. If a test_package is not provided, a new one is created. Returns the test_package

    :param libc: the c-library object used to retrieve the c-functions
    :type libc: c-library object
    :param image: the checkerboard image file path
    :type image: str
    :param product_type: the product type
    :type product_type: str
    :param hwid: the hardware id
    :type hwid: str (hex)
    :param select_test: the test type
    :type select_test: FpcCheckerboardT
    :param test_package: dictionary containing config, result, error_code etc
    :type test_package: dictionary
    :return: test_package
    :rtype: dict
    """

    if test_package is None:
        test_package = {}

    if select_test is FpcCheckerboardT.FPC_IMAGE_TEST_CHESS_INV:
        test_name = "inverted_checkerboard"
    else:
        test_name = "checkerboard"

    test_package["test_name"] = test_name
    test_package["files"] = [image]
    test_package = checkerboard.init_checkerboard_test(libc, product_type, hwid, test_package)

    # The following examples show how to modify config values:
    # test_package["config"].max_deviation = 44
    # test_package["config"].pixel_errors_upper_limit = 2

    test_package = checkerboard.checkerboard_test(libc, image, select_test, test_package)

    return test_package


def run_gradient_checkerboard(libc,
                              image,
                              product_type,
                              hwid,
                              select_test=FpcCheckerboardT.FPC_IMAGE_TEST_CHESS,
                              test_package=None):
    """Run the gradient checkerboard test

    Run the gradient checkerboard test. If a test_package is not provided, a new one is created. Returns
    the test_package.

    :param libc: the c-library object used to retrieve the c-functions
    :type libc: c-library object
    :param image: the checkerboard image file path
    :type image: str
    :param product_type: the product type
    :type product_type: str
    :param hwid: the hardware id
    :type hwid: str (hex)
    :param select_test: the test type
    :type select_test: FpcCheckerboardT
    :param test_package: dictionary containing config, result, error_code etc
    :type test_package: dictionary
    :return: test_package
    :rtype: dict
    """

    if test_package is None:
        test_package = {}

    if select_test is FpcCheckerboardT.FPC_IMAGE_TEST_CHESS_INV:
        test_name = "inverted_gradient_checkerboard"
    else:
        test_name = "gradient_checkerboard"

    test_package["test_name"] = test_name
    test_package["files"] = [image]
    test_package = gradient_checkerboard.init_gradient_checkerboard_test(libc, product_type, hwid, test_package)

    # The following examples show how to modify config values:
    # test_package["config"].max_deviation = 44
    # test_package["config"].pixel_errors_upper_limit = 2

    if test_package["config"].area_height is 0 or test_package["config"].area_width is 0:
        test_package["error_code"] = ErrorCode.CONFIG_NOT_INITIALIZED
        test_package["result"] = gradient_checkerboard.GradientCheckerboardResult()
        return test_package

    test_package = gradient_checkerboard.gradient_checkerboard_test(libc, image, select_test, test_package)

    return test_package


def run_checkerboard_combined(libc,
                              image,
                              image_inverted,
                              product_type,
                              hwid,
                              test_package=None):
    """Run the combined checkerboard test

    Run the checkerboard test, for both the checkerboard image and the inverted checkerboard image. If a
    test_package is not provided, a new one is created. Returns the test_package

    :param libc: the c-library object used to retrieve the c-functions
    :type libc: c-library object
    :param image: the checkerboard image file path
    :type image: str
    :param image_inverted: the inverted checkerboard image file path
    :type image_inverted: str
    :param product_type: the product type
    :type product_type: str
    :param hwid: the hardware id
    :type hwid: str (hex)
    :param test_package: dictionary containing config, result, error_code etc
    :type test_package: dictionary
    :return: test_package
    :rtype: dict
    """

    if test_package is None:
        test_package = {}

    test_package["test_name"] = "checkerboard_combined"
    test_package["files"] = [image, image_inverted]
    test_package = checkerboard.init_checkerboard_test(libc, product_type, hwid, test_package)

    # The following examples show how to modify config values:
    # test_package["config"].max_deviation = 44
    # test_package["config"].pixel_errors_upper_limit = 2

    if test_package["config"].area_height is 0 or test_package["config"].area_width is 0:
        test_package["error_code"] = ErrorCode.CONFIG_NOT_INITIALIZED
        test_package["result"] = checkerboard.CheckerboardConfig()
        return test_package

    test_package = checkerboard.checkerboard_combined_test(libc, image, image_inverted, test_package)

    return test_package


def run_reset_pixel(libc, image, test_package=None):
    """Run the reset pixel test

    Run the reset pixel test. If a test_package is not provided, a new one is created.
    Returns the test_package

    :param libc: the c-library object used to retrieve the c-functions
    :type libc: c-library object
    :param image: the reset image file path
    :type image: str
    :param test_package: dictionary containing config, result, error_code etc
    :type test_package: dictionary
    :return: test_package
    :rtype: dict
    """

    if test_package is None:
        test_package = {}

    test_package["test_name"] = "reset_pixel"
    test_package["files"] = [image]
    test_package = reset_pixel.init_reset_pixel_test(libc, test_package)

    # The following examples show how to modify config values:
    # test_package["config"].lower_limit_from_median = 2
    # test_package["config"].higher_limit_from_median = 6

    if test_package["config"].lower_limit_from_median is 0 or test_package["config"].higher_limit_from_median is 0:
        test_package["error_code"] = ErrorCode.CONFIG_NOT_INITIALIZED
        test_package["result"] = reset_pixel.ResetPixelConfig()
        return test_package

    test_package = reset_pixel.reset_pixel_test(libc, image, test_package)

    return test_package


def calculate_capacitance(libc,
                          white_image,
                          painted_image,
                          pixel_gain,
                          test_package=None,
                          max_pixel_gain=None,
                          companion_chip_type=None):
    """Run the calculate_capacitance

    Run the calculate capacitance. If a test_package is not provided, a new one is created.
    Returns the test_package

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
    :rtype: dict
    """
    if test_package is None:
        test_package = {}

    test_package["test_name"] = "calculate_capacitance"
    test_package["files"] = [white_image, painted_image]

    test_package = capacitance.calculate_capacitance(libc,
                                                     white_image,
                                                     painted_image,
                                                     pixel_gain,
                                                     test_package,
                                                     max_pixel_gain,
                                                     companion_chip_type)

    test_package["result"] = test_package["capacitance_result"]

    return test_package


def run_blob(libc,
             white_image,
             painted_image,
             pixel_gain,
             test_package=None,
             max_pixel_gain=None,
             companion_chip_type=None):
    """Run the capacitance test

    Run the capacitance test. If a test_package is not provided, a new one is created.
    Returns the test_package

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
    :rtype: dict
    """
    if test_package is None:
        test_package = {}

    test_package["test_name"] = "blob"
    test_package["files"] = [white_image, painted_image]
    test_package = capacitance.init_blob_test(libc, test_package)

    # The following examples show how to modify config values:
    # test_package["config"].blob_threshold = (float)3.2e-6
    # test_package["config"].max_number_of_blob_pixels = 3

    test_package = capacitance.calculate_capacitance(libc,
                                                     white_image,
                                                     painted_image,
                                                     pixel_gain,
                                                     test_package,
                                                     max_pixel_gain,
                                                     companion_chip_type)

    test_package = capacitance.calculate_blob(libc, test_package)

    return test_package
