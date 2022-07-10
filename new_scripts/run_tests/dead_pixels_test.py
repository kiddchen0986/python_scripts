import argparse
from TestClass.DeadPixels import *
from TestClass.ImageConstant import *
from util import read_image


def SetupConfig(testLib, product, hwid):
    cb_config = fpc_checkerboard_config_t()

    status = testLib.init_checkerboard_test(c.byref(cb_config), product, hwid)

    if status != 0:
        print("init_checkerboard_test failed, error:", status)
        return None

    print("\n--------------------Setup cb_config--------------------------\n")
    print("max_deviation:", cb_config.max_deviation)
    print("pixel_errors_upper_limit:", cb_config.pixel_errors_upper_limit)
    print("sub_areas_errors_upper_limit:", cb_config.sub_areas_errors_upper_limit)
    print("CB_type1_median_min:", cb_config.CB_type1_median_min)
    print("CB_type1_median_max:", cb_config.CB_type1_median_max)
    print("CB_type2_median_min:", cb_config.CB_type2_median_min)
    print("CB_type2_median_max:", cb_config.CB_type2_median_max)
    print("ICB_type1_median_min:", cb_config.ICB_type1_median_min)
    print("ICB_type1_median_max:", cb_config.ICB_type1_median_max)
    print("ICB_type2_median_min:", cb_config.ICB_type2_median_min)
    print("ICB_type2_median_max:", cb_config.ICB_type2_median_max)

    return cb_config

def SetupGradientConfig(testLib, product, hwid, level):
    cb_gradient_config = fpc_gradient_checkerboard_config_t()

    status = testLib.init_gradient_checkerboard_test_based_on_test_level(c.byref(cb_gradient_config), product, hwid, level)

    if status != 0:
        print("init_gradient_checkerboard_test failed, error:", status)
        return None

    #cb_gradient_config.max_deviation = 25
    print("\n--------------------Setup cb_gradient_config--------------------------\n")
    print("max_deviation:", cb_gradient_config.max_deviation)
    print("pixel_errors_upper_limit:", cb_gradient_config.pixel_errors_upper_limit)
    print("sub_areas_errors_upper_limit:", cb_gradient_config.sub_areas_errors_upper_limit)
    print("histogram_slot_length:", cb_gradient_config.histogram_slot_length)
    print("CB_type1_median_min:", cb_gradient_config.CB_type1_median_min)
    print("CB_type1_median_max:", cb_gradient_config.CB_type1_median_max)
    print("CB_type2_median_min:", cb_gradient_config.CB_type2_median_min)
    print("CB_type2_median_max:", cb_gradient_config.CB_type2_median_max)
    print("ICB_type1_median_min:", cb_gradient_config.ICB_type1_median_min)
    print("ICB_type1_median_max:", cb_gradient_config.ICB_type1_median_max)
    print("ICB_type2_median_min:", cb_gradient_config.ICB_type2_median_min)
    print("ICB_type2_median_max:", cb_gradient_config.ICB_type2_median_max)

    return cb_gradient_config

def DeadPixelsGradient(testLib, image, select_test, cb_config):
    print("\n--------------------Running Gradient Dead Pixels {} Test--------------------------\n"
          .format("CB" if fpc_checkerboard_t.FPC_IMAGE_TEST_CHESS == select_test else "ICB"));

    result = fpc_gradient_checkerboard_result_t()
    dead_pixels_list = dead_pixels_info_t()
    dead_pixels_list.list_max_size = cb_config.pixel_count
    dead_pixels_list.is_initialized = 1
    w = 10
    dead_pixels_list.dead_pixels_index_list = (c.c_uint16 * cb_config.pixel_count)(0)

    status = testLib.gradient_checkerboard_test(image,
                                                select_test,
                                                c.byref(cb_config),
                                                c.byref(result),
                                                c.byref(dead_pixels_list))

    if status != 0:
        print("gradient_checkerboard_test failed, error:", status)

    print(result)
    return status

def DeadPixels(testLib, image, select_test, cb_config):
    print("\n--------------------Running Dead Pixels {} Test--------------------------\n"
          .format("CB" if fpc_checkerboard_t.FPC_IMAGE_TEST_CHESS == select_test else "ICB"));

    result = fpc_checkerboard_result_t()
    dead_pixels_list = dead_pixels_info_t()
    dead_pixels_list.list_max_size = cb_config.pixel_count
    dead_pixels_list.is_initialized = 1
    dead_pixels_list.dead_pixels_index_list = (c.c_uint16 * cb_config.pixel_count)(0)

    status = testLib.checkerboard_test(image,
                                       select_test,
                                       c.byref(cb_config),
                                       c.byref(result),
                                       c.byref(dead_pixels_list))

    print("pixel_errors", result.pixel_errors)
    print("sub_area_errors", result.sub_area_errors)
    print("type1_median", result.type1_median)
    print("type2_median", result.type2_median)
    print("type1_mean", result.type1_mean)
    print("type2_mean", result.type2_mean)
    print("type1_deviation_max", result.type1_deviation_max)
    print("type2_deviation_max", result.type2_deviation_max)
    print("pass", result.pass1)
    print("result", result.result)

    if status != 0:
        print("checkerboard_test failed, error:", status)

    return status

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("product", help="product type, like 1267", type=str)
    parser.add_argument("image", help="raw image", type=str)
    parser.add_argument("select_test", help="image type, CB or ICB", type=str)
    parser.add_argument("test_level", help="test limit level, MTS or ITS", type=str)
    parser.add_argument("hwid", help="hardware id, like 0x321", type=str)

    args = parser.parse_args()

    hwid = int(args.hwid, 16) if args.hwid.startswith("0x") else int(args.hwid)

    if args.test_level.lower() == "mts":
        test_level = TestLevelT.FPC_TEST_LEVEL_MTS
    elif args.test_level.lower() == "its":
        test_level = TestLevelT.FPC_TEST_LEVEL_ITS
    else:
        raise Exception("Only support MTS or ITS")

    if args.select_test == "CB":
        select_test = fpc_checkerboard_t.FPC_IMAGE_TEST_CHESS
    elif args.select_test == "ICB":
        select_test = fpc_checkerboard_t.FPC_IMAGE_TEST_CHESS_INV
    else:
        raise Exception("Only support CB or ICB")

    testLib = TestLib("DeadPixels")

    status = -1

    image = read_image(args.image)
    if image == None:
        raise Exception("Incorrect image")

    if args.product == "1035" or args.product == "1020" \
            or args.product == "1021" or args.product == "1025" \
            or args.product == "1140" or args.product == "1145" \
            or args.product == "1155" or args.product == "1245" \
            or args.product == "1320" or args.product == "1321":

        cb_config = SetupConfig(testLib, product_map[args.product], hwid)
        if cb_config is None:
            raise Exception("Cannot find correct test config")
        status = DeadPixels(testLib, image, int(select_test), cb_config)
    else:
        cb_config = SetupGradientConfig(testLib, product_map[args.product], hwid, int(test_level))
        if cb_config is None:
            raise Exception("Cannot find correct test config")
        status = DeadPixelsGradient(testLib, image, int(select_test), cb_config)

    #if status == 0:
    #    print("PASS")
    #else:
    #    print("FAIL")