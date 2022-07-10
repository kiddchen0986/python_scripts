from TestClass.TestLibrary import *

class fpc_image_constant_config_t(c.Structure):
    _fields_ = [
        ("area_height", c.c_uint32),
        ("area_width", c.c_uint32),
        ("sub_area_height", c.c_uint32),
        ("sub_area_width", c.c_uint32),
        ("sub_area_nbr_rows", c.c_uint32),
        ("sub_area_nbr_cols", c.c_uint32),
        ("sub_areas_row", c.c_uint8 * MAX_NBR_SUB_AREA_ROWS),
        ("sub_areas_col", c.c_uint8 * MAX_NBR_SUB_AREA_COLS),
        ("pixel_errors_upper_limit", c.c_uint32),
        ("median_lower_limit", c.c_uint32),
        ("median_upper_limit", c.c_uint32),
        ("max_median_deviation", c.c_uint32)
    ]

class fpc_image_constant_result_t(c.Structure):
    _fields_ = [
        ("image_constant_medians", c.POINTER(c.c_uint8)),
        ("number_of_medians", c.c_uint32),
        ("pixel_errors", c.c_uint32),
        ("sub_area_errors", c.c_uint32),
        ("pass1", c.c_bool)
    ]

    def __str__(self):
        image_constant_medians = [self.image_constant_medians[i] for i in range(self.number_of_medians)]
        return  "number_of_medians: " + str(self.number_of_medians) + '\n' + \
                "pixel_errors: " + str(self.pixel_errors) + '\n' + \
                "sub_area_errors: " + str(self.sub_area_errors) + '\n' + \
                "image_constant_medians: " + str(image_constant_medians)
