from TestClass.Blob import *
from TestClass.DeadPixels import *
from array import array
import argparse
import os
import pandas as pd
from util import read_image


def blob_detect(testLib, image, width, height, blob_threshold = 3.5e-6, save = False):
    raw = read_image(image)

    blob_config = fpc_blob_config_t()
    status = testLib.init_blob_test(c.byref(blob_config))
    blob_config.blob_threshold = blob_threshold

    #print("--------------fpc_blob_config_t---------------")
    #print(blob_config)

    dead_pixels_list = dead_pixels_info_t()
    dead_pixels_list.list_max_size = 100
    dead_pixels_list.is_initialized = 1

    pixel_count = width * height

    dead_pixels_list.dead_pixels_index_list = (c.c_uint16 * pixel_count)(0)

    result = fpc_blob_result_t()
    result.blob_image = (c.c_uint8 * pixel_count)(0)
    result.detection_image = (c.c_float * pixel_count)(0)

    status = testLib.calculate_blob(raw, width, height, c.byref(blob_config), c.byref(result), c.byref(dead_pixels_list))
    #print("--------------Run calculate_blob---------------")
    #print("\tblob threshold", blob_threshold, ", \tnumber_of_blob_pixels", result.number_of_blob_pixels)

    blob_image = bytes(c.cast(result.blob_image, c.POINTER(c.c_uint8))[0:pixel_count])
    detection_image = array('f', c.cast(result.detection_image, c.POINTER(c.c_float))[0:pixel_count])

    if save:
        image_name = image.split('\\')[-1]
        with open('./out/blob_' + str(blob_config.blob_threshold)[:4] + '_' + image_name + '!' + str(width) + '_' + str(height) + '_1.raw', 'wb') as f:
            f.write(blob_image)

        with open('./out/detection_' + str(blob_config.blob_threshold)[:4] + '_' + image_name, 'wb') as f:
            detection_image.tofile(f)

    return result.number_of_blob_pixels#, result.pass1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="raw image", type=str)
    parser.add_argument("width", help="image width", type=int)
    parser.add_argument("height", help="image height", type=int)
    parser.add_argument("csv", help="output csv file", type=str)
    parser.add_argument('-save', help = 'save blob and detection images', type=bool, default=False)

    args = parser.parse_args()

    testLib = TestLib("Blob")

    result = []
    thresholds = [3.5e-6, 3.25e-6, 3.0e-6, 2.75e-6, 2.5e-6, 2.25e-6, 2.0e-6, 1.5e-6, 0.5e-6]
    for file in os.listdir(args.path):
        if file.endswith('_4.raw'):
            print('Run', file)
            blob_result = [file]
            for threshold in thresholds:
                #print('\tblob threshold', threshold)
                blob_result.append(blob_detect(testLib, os.path.join(args.path, file), args.width, args.height, threshold, args.save))

            result.append(blob_result)

    thresholds.insert(0, 'raw')
    df = pd.DataFrame(result, columns=thresholds)
    print(df)
    df.to_csv(args.csv, encoding='utf-8', index=True)
    print('Finish')
