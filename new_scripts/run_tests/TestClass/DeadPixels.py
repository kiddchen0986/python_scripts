from enum import IntEnum
from TestClass.TestLibrary import *

MAX_NBR_ROWS = 256
MAX_NBR_COLS = 256

class fpc_checkerboard_config_t(c.Structure):
    _fields_ = [
        ("area_height", c.c_uint32),
        ("area_width", c.c_uint32),
        ("pixel_count", c.c_uint32),
        ("sub_area_height", c.c_uint32),
        ("sub_area_width", c.c_uint32),
        ("sub_area_nbr_rows", c.c_uint32),
        ("sub_area_nbr_cols", c.c_uint32),
        ("sub_areas_row", c.c_uint8 * MAX_NBR_SUB_AREA_ROWS),
        ("sub_areas_col", c.c_uint8 * MAX_NBR_SUB_AREA_COLS),
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
        ("ICB_type2_median_max", c.c_uint32),
    ]

class fpc_gradient_checkerboard_config_t(c.Structure):
    _fields_ = [
        ("area_height", c.c_uint32),
        ("area_width", c.c_uint32),
        ("pixel_count", c.c_uint32),
        ("sub_area_height", c.c_uint32),
        ("sub_area_width", c.c_uint32),
        ("sub_area_nbr_rows", c.c_uint32),
        ("sub_area_nbr_cols", c.c_uint32),
        ("sub_areas_row", c.c_uint8 * MAX_NBR_SUB_AREA_ROWS),
        ("sub_areas_col", c.c_uint8 * MAX_NBR_SUB_AREA_COLS),
        ("max_deviation", c.c_uint32),
        ("pixel_errors_upper_limit", c.c_uint32),
        ("sub_areas_errors_upper_limit", c.c_uint32),
        ("histogram_slot_length", c.c_uint32),
        ("CB_type1_median_min", c.c_uint32),
        ("CB_type1_median_max", c.c_uint32),
        ("CB_type2_median_min", c.c_uint32),
        ("CB_type2_median_max", c.c_uint32),
        ("ICB_type1_median_min", c.c_uint32),
        ("ICB_type1_median_max", c.c_uint32),
        ("ICB_type2_median_min", c.c_uint32),
        ("ICB_type2_median_max", c.c_uint32),
        ("histogram_deviation", c.c_uint8)
    ]

class fpc_checkerboard_result_t(c.Structure):
    _fields_ = [
        ("pixel_errors", c.c_uint32),
        ("sub_area_errors", c.c_uint32),
        ("type1_median", c.c_uint32),
        ("type2_median", c.c_uint32),
        ("type1_mean", c.c_uint32),
        ("type2_mean", c.c_uint32),
        ("type1_deviation_max", c.c_uint32),
        ("type2_deviation_max", c.c_uint32),
        ("result", c.c_uint32),
        ("pass1", c.c_bool),
        ("pixel_errors_per_row", c.c_uint8 * MAX_NBR_ROWS),
        ("pixel_errors_per_col", c.c_uint8 * MAX_NBR_COLS)
    ]

class fpc_gradient_checkerboard_result_t(c.Structure):
    _fields_ = [
        ("pixel_errors", c.c_uint32),
        ("sub_area_errors", c.c_uint32),
        ("type1_deviation_max", c.c_uint32),
        ("type2_deviation_max", c.c_uint32),
        ("type1_min_histogram_median", c.c_uint8),
        ("type2_min_histogram_median", c.c_uint8),
        ("type1_max_histogram_median", c.c_uint8),
        ("type2_max_histogram_median", c.c_uint8),
        ("result", c.c_uint32),
        ("pass1", c.c_bool)
    ]

    def __str__(self):
        return "pixel_errors: " + str(self.pixel_errors) + "\ntype1_deviation_max: " + str(self.type1_deviation_max) + \
                "\ntype2_deviation_max: " + str(self.type2_deviation_max) + \
                "\ntype1_min_histogram_median: " + str(self.type1_min_histogram_median) + \
                "\ntype1_max_histogram_median: " + str(self.type1_max_histogram_median) + \
                "\ntype2_min_histogram_median: " + str(self.type2_min_histogram_median) + \
                "\ntype2_max_histogram_median: " + str(self.type2_max_histogram_median) + \
                "\nresult: " + str(self.result) + \
                "\npass: " + str(self.pass1)

class dead_pixels_info_t(c.Structure):
    _fields_ = [
        ("num_dead_pixels", c.c_uint16),
        ("dead_pixels_index_list", c.POINTER(c.c_uint16)),
        ("list_max_size", c.c_uint16),
        ("is_initialized", c.c_int32),
    ]

class fpc_checkerboard_t(IntEnum):
    """Equivalent to prodtestlib.dll's fpc_test_level_t"""
    FPC_IMAGE_TEST_CHESS = 3,
    FPC_IMAGE_TEST_CHESS_INV = 4,
    FPC_IMAGE_TEST_WHITE = 5,
    FPC_IMAGE_TEST_BLACK = 6,


class TestLevelT(IntEnum):
    """Equivalent to prodtestlib.dll's fpc_test_level_t"""
    FPC_TEST_LEVEL_MTS = 0
    FPC_TEST_LEVEL_ITS = 1