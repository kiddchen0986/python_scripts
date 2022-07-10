# -*- coding: utf-8 -*-
"""
Usage:
save_deviation_images(directory_name)

This creates deviation images with a X amplification level

Input is a directory with checkerboard images. A sub folder
will be created for each type with the amplification level

@author: tomas.kohn
"""

import numpy as np
import scipy.misc as misc
import os

directory_name = r"C:\doc\SB-28\Biel_Crystal_DOE\DOE TEST LOG\C"

def clamp(raw_value, min_value, max_value):
    clamped_value = max(min_value, min(raw_value, max_value))
    return clamped_value


def calculate_cb_median(cb_image):
    width = cb_image.shape[0]
    height = cb_image.shape[1]
    type1_pixels = []
    type2_pixels = []

    for row in range(0, height):
        even_row = (row % 2 == 0)
        for column in range(0, width):
            even_column = (column % 2 == 0)
            if even_column ^ even_row: # type 2
                type2_pixels.append( cb_image[column, row] )
            else: # type 1
                type1_pixels.append( cb_image[column, row] )        

    type1_median = np.median(type1_pixels)
    type2_median = np.median(type2_pixels)

    return (type1_median, type2_median)

def get_amplified_cb_image(cb_image, type1_median, type2_median, amplify_factor):
    width = cb_image.shape[0]
    heigth = cb_image.shape[1]
    amplified_image = np.zeros((width,heigth),'u1')

    deviation_list = []
    deviation = 0
    for row in range(0, heigth):
        evenRow = (row % 2 == 0)
        for column in range(0, width):
            evenColumn = (column % 2 == 0)
            if evenColumn ^ evenRow: # type 2
                deviation = cb_image[column, row] - type2_median
                deviation_list.append(deviation)
                image_pixel = 128+deviation*amplify_factor
                amplified_image[column, row] = image_pixel
            else: # type 1
                deviation = cb_image[column, row] - type1_median
                deviation_list.append(deviation)
                image_pixel = 128+deviation*amplify_factor
                amplified_image[column, row] = image_pixel

    return (amplified_image, deviation_list)

def create_and_save_amplified_image(image_path, folder_prefix):
    amplification_level = 5
    print_debug_info = True
    im = misc.imread(image_path, "L")
    type1_median, type2_median = calculate_cb_median(im)
    
    amplified_image, deviation_list = get_amplified_cb_image(im, type1_median, type2_median, amplification_level)

    if print_debug_info:
        print("Median type1: "+str(type1_median))
        print("Median type2: "+str(type2_median))
        i = 0
        for deviation in deviation_list:
            if deviation > 7:
                print(image_path+" = ["+str(i)+"] "+str(deviation))
            i = i +1

    original_filename = os.path.basename(image_path)
    new_path_name = directory_name+"\\"+folder_prefix+"_"+str(amplification_level)
    if not os.path.exists(new_path_name):
        os.makedirs(new_path_name)

    full_path_to_save = new_path_name+"\\"+original_filename+"_"+str(amplification_level)+".png"
    misc.imsave(full_path_to_save, amplified_image)

def save_deviation_images(path_for_images):
    print("Directory: "+directory_name)

    for root, dirs, files in os.walk(directory_name):
        for filename in files:
            full_path = root+"\\"+filename
            if os.path.isfile(full_path) and full_path.endswith(".png"):
                if full_path.endswith("ImageConstantImage.png"):
                    create_and_save_amplified_image(full_path, "const")
                elif full_path.endswith("ImageDriveImages.png"):
                    create_and_save_amplified_image(full_path, "drive")
                elif full_path.endswith("SwingingCheckerboardImage.png") or full_path.endswith("SwingingInvertedCheckerboardImage.png"):
                    create_and_save_amplified_image(full_path, "swingcb")
                elif full_path.endswith("CheckerboardImage.png") or full_path.endswith("InvertedCheckerboardImage.png"):
                    create_and_save_amplified_image(full_path, "cb")

save_deviation_images(directory_name)

