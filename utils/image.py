"""Module used to interpret image files, primarily extracting bit information.

Should work for:
.png
.bmp
.fmi (not yet)
"""
from scipy import misc
import os
import ctypes as c
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from utils.utils_common import create_file_path, print_progress_bar

__docformat__ = 'reStructuredText'

"""ctypes types:
c_uint              = uint32_t
c_ushort            = uint16_t
c_char or c_uint8   = uint8_t
c_bool              = bool
"""


RED_GREEN_CMAP = None


def init_red_green_cmap():
    """Initialize and prepare the red_green colour map"""
    cdict = {'red':     ((0.0, 0.0, 0.0),
                         (1.0, 1.0, 1.0)),

             'green':   ((0.0, 1.0, 1.0),
                         (1.0, 0.0, 0.0)),

             'blue':    ((0.0, 0.0, 0.0),
                         (1.0, 0.0, 0.0))}

    global RED_GREEN_CMAP
    RED_GREEN_CMAP = LinearSegmentedColormap("red_green", cdict)
    plt.register_cmap(cmap=RED_GREEN_CMAP)


def extract_standard_img_format(file, bits=8):
    """Extracts image data for files of standard format .png, .bmp

    :param file: the image file path
    :type file: str
    :param bits: size of pixels
    :type bits: int
    :return: dictionary containing image information
    :rtype: dictionary
    """
    if bits is 8:
        # 8-bit pixel, black and white
        image = misc.imread(file, mode='L')
    elif bits is 32:
        # 32-bit signed integer pixels
        image = misc.imread(file, mode='I')

    image_data = {"width": image.shape[1],
                  "height": image.shape[0],
                  "capacity": image.shape[0]*image.shape[1],
                  "ndarray": image,
                  "buffer": np.ctypeslib.as_ctypes(image)}
    image_data["buffer_p"] = c.POINTER(c.c_uint8)(image_data["buffer"])

    return image_data


def extract_fmi_img_format(file):
    """Extracts image data for files of .fmi format

    :param file: the .fmi image file path
    :type file: str
    :return: dictionary containing image information
    :rtype: dictionary
    """
    print(".fmi support not yet implemented")
    return []


def extract_not_supportet_format(file):
    """Tried to extract image data for a file of an unsupported format

    :param file: the image file path
    :type file: str
    :return: None
    """
    print("The '{}' format is not supported".format(os.path.splitext(file)[1]))

    return []


def extract(file):
    """Finds the correct extraction function depending on file type

    :param file: the image file path
    :type file: str
    :return: dictionary containing image information
    :rtype: dictionary
    """
    file_name, file_extension = os.path.splitext(file)
    formats = {".png": extract_standard_img_format,
               ".bmp": extract_standard_img_format,
               ".fmi": extract_fmi_img_format}
    return formats.get(file_extension, extract_not_supportet_format)(file)


def save_normalized_cap_image_from_test_seq_packs(test_seq_packs, ceiling, floor):
    """Save the capacitance_images to image files, after they have been normalized according to ceiling & floor

    :param test_seq_packs: list of test_sequence_packages
    :type test_seq_packs: list of dict
    :param ceiling: the maximum value; values above this will receive '255'
    :type ceiling: float
    :param floor: the minimum value; values above this will receive '0'
    :type floor: float
    :return: file path to the folder where the images have been saved
    :rtype: str
    """
    if len(test_seq_packs) > 0:
        test_sequence_name = test_seq_packs[0]["test_sequence"]

        width = test_seq_packs[0]["test_packages"][0]["white_image_data"]["width"]
        height = test_seq_packs[0]["test_packages"][0]["white_image_data"]["height"]

        print_progress_bar(0, len(test_seq_packs), "\t")
        for i, seq_pack in enumerate(test_seq_packs):
            print_progress_bar(i + 1, len(test_seq_packs), "\t")
            title = "{}_{}".format(test_sequence_name, seq_pack["test_id"])
            file_path = create_file_path(title,
                                         '.png',
                                         "normalized_capacitance",
                                         sub_dir="normalized_capacitance")

            save_normalized(seq_pack["test_packages"][0]["capacitance_result"].capacitance_image_float_array,
                            width,
                            height,
                            ceiling,
                            floor,
                            file_path)

        return os.path.dirname(file_path)


def save_normalized(array, width, height, ceiling, floor, file_path):
    """Save the data as an image file, after normalizing the array using the ceiling and floor variables. The image is
    colormapped.

    :param array: the image data
    :type array: ndarray
    :param width: width of the image
    :type width: int
    :param height: height of the image
    :type height: int
    :param ceiling: the maximum value; values above this will receive '255'
    :type ceiling: float
    :param floor: the minimum value; values above this will receive '0'
    :type floor: float
    :param file_path:
    :return: file_path, where the image is saved
    :rtype: str
    """
    plt.cla()
    plt.clf()
    plt.close()

    global RED_GREEN_CMAP
    if RED_GREEN_CMAP is None:
        init_red_green_cmap()

    img_array = misc.bytescale(array, cmin=floor, cmax=ceiling)
    img_array.shape = (height, width)
    # img = plt.imshow(img_array, interpolation="nearest", cmap=RED_GREEN_CMAP)
    # plt.show()

    plt.imsave(file_path, img_array, cmap=plt.get_cmap("red_green"))

    return file_path


# if __name__ == "__main__":
#    file = "CheckerboardImage.png"
#    buffer = extract(file)
