import numpy as np
import matplotlib.pyplot as plt
import png
import ctypes
import sys

def analyze_checkerboard_image(path):
    if path.split('.')[-1] == 'png':
        png_reader = png.Reader(filename=path)
        w, h, pixels, metadata = png_reader.read_flat()
        np_pixels = np.array(pixels)

    elif path.split('.')[-1] == 'raw':
        np_pixels = np.fromfile(path, dtype=ctypes.c_ubyte)

    _, _, patches = plt.hist(np_pixels, bins=np_pixels.max() - np_pixels.min(),
                             range=(np_pixels.min(), np_pixels.max()))

    max_bin_1 = max((p.get_height(), p.get_x()) for p in patches if p.get_x() < 128)
    max_bin_2 = max((p.get_height(), p.get_x()) for p in patches if p.get_x() >= 128)
    print('max type1 bin {}, pixel {}'.format(max_bin_1[0], max_bin_1[1]))
    print('max type2 bin {}, pixel {}'.format(max_bin_2[0], max_bin_2[1]))
    plt.show()

if __name__ == '__main__':
    try:
        analyze_checkerboard_image(sys.argv[1])
    except IndexError as e:
        print('python analyze_checkerboard_image.py <checkerboard_image_path>')