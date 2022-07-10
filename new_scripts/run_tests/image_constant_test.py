import argparse
import sys
from TestClass.ImageConstant import *
from TestClass.DeadPixels import *
from util import read_image


def image_constant(testLib, image, sensor):
    print("\n--------------------fpc_image_constant_config_t--------------------------\n")
    config = fpc_image_constant_config_t()
    status = testLib.init_image_constant_test(c.byref(config), sensor)
    if status != 0:
        print("init_image_constant_test fail")
        return status

    print(config)

    dead_pixels_list = dead_pixels_info_t()
    dead_pixels_list.list_max_size = config.area_height * config.area_width
    dead_pixels_list.is_initialized = 1
    pixel = config.area_height * config.area_width
    dead_pixels_list.dead_pixels_index_list = (c.c_uint16 * pixel)(0)
    print("\n--------------------Running Image Constant test--------------------------\n")
    result = fpc_image_constant_result_t()
    status = testLib.image_constant_test(image, c.byref(config), c.byref(result), c.byref(dead_pixels_list))

    if status != 0:
        print("image_constant_test error", status)

    print(result)
    return result.pass1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("sensor", help="product type, like 1260", type=str)
    parser.add_argument("image", help="raw image", type=str)
    parser.add_argument("test_level", help="test limit level, MTS or ITS", type=str, default="MTS")

    args = parser.parse_args()
    sensor = sensor_map[args.sensor]
    image = read_image(args.image)

    testLib = TestLib("ImageConstant")

    status = image_constant(testLib, image, sensor)

    if status is False:
        print("Image constant test fail")
    else:
        print("Image constant test pass")