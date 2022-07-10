from TestClass.TestLibrary import *

class fpc_blob_config_t(c.Structure):
    _fields_ = [
        ("blob_threshold", c.c_float),
        ("max_number_of_blob_pixels", c.c_uint32),
    ]

    def __str__(self):
        return "blob_threshold: " + str(self.blob_threshold) + "\n" + "max_number_of_blob_pixels: " + str(self.max_number_of_blob_pixels)

class fpc_blob_result_t(c.Structure):
    _fields_ = [
        ("number_of_blob_pixels", c.c_uint32),
        ("detection_image", c.POINTER(c.c_float)),
        ("blob_image", c.POINTER(c.c_uint8)),
        ("width", c.c_uint32),
        ("height", c.c_uint32),
        ("pass1", c.c_bool),
    ]