#
# Copyright (c) 2018 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#

import os
import ctypes as c

class Mqt2TestSettings(c.Structure):
    """Python structure equivalent of mqt_analysis_settings_t in ctl_rerun_test_analysis.dll"""

    _fields_ = [
        ("cropping_left", c.c_uint16),
        ("cropping_top", c.c_uint16),
        ("cropping_right", c.c_uint16),
        ("cropping_bottom", c.c_uint16),

        ("blob_threshold", c.c_float),
        ("blob_limit", c.c_uint32),

        ("snr_preset", c.c_uint8),
        ("snr_limit", c.c_float),

        ("udr_limit", c.c_float),

        ("fixed_pattern_enabled", c.c_bool),
        ("fixed_pattern_threshold", c.c_float),
        ("fixed_pattern_limit", c.c_uint32),

        ("is_static_mqt", c.c_bool)]

    def __init__(self):
        # Initialize like normal
        super(Mqt2TestSettings, self).__init__()

        self.cropping_left = 4
        self.cropping_top = 4
        self.cropping_right = 4
        self.cropping_bottom = 4

        self.blob_threshold = 1.1e-6
        self.blob_limit = 7

        self.snr_preset = 5
        self.snr_limit = 8.0

        self.udr_limit = 0.25

        self.fixed_pattern_enabled = False
        self.fixed_pattern_threshold = 0.0
        self.fixed_pattern_limit = 0

        self.is_static_mqt = False

    def set_mqt_test_criteria(self,
                              crop_left,
                              crop_top,
                              crop_right,
                              crop_bottom,
                              bl_thresh,
                              bl_limit,
                              snr_pre,
                              snr_limit,
                              udr_limit,
                              fixed_p_enabled,
                              fixed_p_threshold,
                              fixed_p_limit,
                              is_static):

        self.cropping_left = crop_left
        self.cropping_top = crop_top
        self.cropping_right = crop_right
        self.cropping_bottom = crop_bottom

        self.blob_threshold = bl_thresh
        self.blob_limit = bl_limit

        self.snr_preset = snr_pre
        self.snr_limit = snr_limit

        self.udr_limit = udr_limit

        self.fixed_pattern_enabled = fixed_p_enabled
        self.fixed_pattern_threshold = fixed_p_threshold
        self.fixed_pattern_limit = fixed_p_limit

        self.is_static_mqt = is_static


class ReRunMqt2:
    """Python object for running MQT2 from ctl_rerun_test_analysis.dll"""

    def __init__(self, lib_file_path):
        self.lib_file_path = lib_file_path
        current_wdr = os.getcwd()
        directory, file = os.path.split(self.lib_file_path)
        os.chdir(directory)
        self.ctl_dll = c.CDLL(file)
        os.chdir(current_wdr)
        print("Loaded dll: {}".format(self.lib_file_path))

    def __call__(self,
                 product_type,
                 hw_id,
                 settings_list,
                 in_file,
                 out_folder,
                 internal=False):

        #in_file = b'C:\\jira\\cet-97\\snr_8-9_bad_image\\002324E162FD_OF0503-234049-00000_ZebraImages.fmi'
        #output_dir = b'C:\python_scripts\wrapper\out_fmi_rerun'

        settings = Mqt2TestSettings()
        settings.set_mqt_test_criteria(settings_list[0], settings_list[1],
                                       settings_list[2], settings_list[3],
                                       settings_list[4], settings_list[5],
                                       settings_list[6], settings_list[7],
                                       settings_list[8], settings_list[9],
                                       settings_list[10], settings_list[11],
                                       settings_list[12])

        mqt2_analysis = self.ctl_dll.ctl_mqt2_analysis

        mqt2_analysis.restype = c.c_uint32
        fmi_path_b = c.create_string_buffer(in_file)
        out_dir_b = c.create_string_buffer(out_folder)

        if internal == False:
            mqt2_analysis = self.ctl_dll.ctl_mqt2_analysis
            mqt2_analysis.argtypes = [c.c_int, c.c_uint16, Mqt2TestSettings,\
                                      c.c_char_p, c.c_char_p]
            return mqt2_analysis(c.c_int(product_type), c.c_uint16(hw_id),\
                                 settings, fmi_path_b, out_dir_b)

        elif internal == True:
            mqt2_analysis = self.ctl_dll.ctl_mqt2_analysis_extended
            mqt2_analysis.argtypes = [c.c_int, c.c_uint16, Mqt2TestSettings,\
                                      c.c_char_p, c.c_char_p, c.c_uint32]

            return mqt2_analysis(c.c_int(product_type), c.c_uint16(hw_id),\
                                 settings, fmi_path_b, out_dir_b,\
                                 c.c_uint32(0x95240000))