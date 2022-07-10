import numpy as np
import matplotlib.pyplot as plt
import png
import ctypes
import sys
from matplotlib import style
import fnmatch
import os

style.use('ggplot')

type2_medians = []

def gen_find(log_pattern:str, log_path:str):
    for path, _, file_list in os.walk(log_path):
        for name in fnmatch.filter(file_list, log_pattern):
            yield os.path.join(path, name)

def analyze_checkerboard_image(path):
    if path.split('.')[-1] == 'png':
        png_reader = png.Reader(filename=path)
        w, h, pixels, metadata = png_reader.read_flat()
        np_pixels = np.array(pixels)

    elif path.split('.')[-1] == 'raw':
        np_pixels = np.fromfile(path, dtype=ctypes.c_ubyte)

    histo = plt.hist(np_pixels, bins=np_pixels.max() - np_pixels.min(),
                             range=(np_pixels.min(), np_pixels.max()))

    count_and_vals = sorted(zip(histo[0], histo[1], histo[2]), reverse = True)

    plt.text(count_and_vals[0][1], count_and_vals[0][2].get_height(), (count_and_vals[0][1], count_and_vals[0][0]))
    plt.text(count_and_vals[1][1], count_and_vals[1][2].get_height(), (count_and_vals[1][1], count_and_vals[1][0]))

    plt.xticks(range(np_pixels.min(), np_pixels.max(), 20))
    plt.xlabel('pixel')
    plt.ylabel('count')

    plt.show()

if __name__ == '__main__':
    try:
        analyze_checkerboard_image(sys.argv[1])

    except IndexError as e:
        print('python analyze_checkerboard_image.py <checkerboard_image_path>')