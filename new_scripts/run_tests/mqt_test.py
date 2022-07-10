#
# Copyright (c) 2018 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#

from TestClass import MQT
import fnmatch
import os
import ctypes as c
from functools import partial
import matplotlib.pyplot as plt
import json
from collections import OrderedDict
import pandas as pd
import argparse
import time
import logging
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.ERROR)

def gen_find(log_pattern:str, log_path:str):
    for path, _, file_list in os.walk(log_path):
        for name in fnmatch.filter(file_list, log_pattern):
            yield os.path.join(path, name)

# FPC Product type information
product_dict = {
    '1080':         0,
    '1020':         1,
    '1021':         2,
    '1025':         3,
    '1225':         4,
    '1022':         5,
    '1035':         6,
    '1235':         7,
    '1140':         8,
    '1145':         9,
    '1245':        10,
    '1260':        13,
    '1265':        14,
    '1268':        15,
    '1028':        16,
    '1075':        17,
    '1320':        18,
    '1321':        19,
    '1263':        20,
    '1262':        21,
    '1266':        22,
    '1264':        23,
    '1272':        24,
    #'1228':        25, no one is using it
    '1267':        26,
    '1291_S':      30,
    '1291_G175':   31,
    '1291':        31,
    '1291_G250':   33,
    '1291_Z120':   34,
    '1228_G175':   36,
    '1228':        36,
    '1228_Z':      37,
    '1272_G175':   38,
    '1272_Z':      39,
    '1261_S':      40,
    '1229_G175':   41,
    '1229':        41,
    '1511_S':      42,
    '1024':        43,
    '1229_G175_SS': 44,
    '1511_G175' : 45,
    '1511_G145' : 47
    }

def find_fmi(root_dir):
    filelist = []
    for path, subdirs, files in os.walk(root_dir):
        for name in files:
               if fnmatch.fnmatch(name, '*.fmi'):
                   filelist.append(os.path.join(path, name).encode())
    filelist.sort()
    return filelist

def load_library(dll_path):
    current_wdr = os.getcwd()
    directory, file = os.path.split(dll_path)
    if directory:
        os.chdir(directory)
    ctl_dll = c.CDLL(file)
    if directory:
        os.chdir(current_wdr)

    return ctl_dll

def run_function(in_file, ctl_dll, hw_id, product_type, settings_list, out_folder, internal):
    settings = MQT.Mqt2TestSettings()
    settings.set_mqt_test_criteria(settings_list[0], settings_list[1],
                                   settings_list[2], settings_list[3],
                                   settings_list[4], settings_list[5],
                                   settings_list[6], settings_list[7],
                                   settings_list[8], settings_list[9],
                                   settings_list[10], settings_list[11],
                                   #settings_list[12], settings_list[13],
                                   #settings_list[14], settings_list[15],
                                   settings_list[12])

    fmi_path_b = c.create_string_buffer(in_file)
    out_dir_b = c.create_string_buffer(out_folder)

    if internal:
        print('Run internal analysis')
        mqt2_analysis = ctl_dll.ctl_mqt2_analysis_extended
        mqt2_analysis.restype = c.c_uint32
        mqt2_analysis.argtypes = [c.c_int, c.c_uint16, MQT.Mqt2TestSettings, \
                                  c.c_char_p, c.c_char_p, c.c_uint32]

        return mqt2_analysis(c.c_int(product_type), c.c_uint16(hw_id), \
                             settings, fmi_path_b, out_dir_b, \
                             c.c_uint32(0x95240000))
    else:
        mqt2_analysis = ctl_dll.ctl_mqt2_analysis
        mqt2_analysis.restype = c.c_uint32
        mqt2_analysis.argtypes = [c.c_int, c.c_uint16, MQT.Mqt2TestSettings, \
                                  c.c_char_p, c.c_char_p]
        return mqt2_analysis(c.c_int(product_type), c.c_uint16(hw_id), \
                             settings, fmi_path_b, out_dir_b)

internal_result = []
def generate_report(output_path):
    files = gen_find("*.json", output_path)
    for file in files:
        with open(file, encoding='utf-8', mode='r') as fh:
            print("Print file name:" + file)
            content = json.load(fh)
            test_data = OrderedDict()
            for test in content['sequence']:
                if test['name'] == 'read_analysis_input':
                    print("Print fmi file name:" + test['fmi_file_name'])
                    test_data['fmi_name'] = test['fmi_file_name']
                if test['name'] == 'module_quality' and ('zebra_image_re-analyze_result' in test['measurement']['result']):
                    test_data['zebra_image_re-analyze_result'] = test['measurement']['result']['zebra_image_re-analyze_result']
                    if 'snr_db' in test['analysis']['result']['snr']:
                        test_data['snr_db'] = test['analysis']['result']['snr']['snr_db']
                    else:
                        test_data['snr_db'] = -1

                    if 'fixed_pattern' in test['analysis']['result'] and 'fixed_pattern_pixels' in test['analysis']['result']['fixed_pattern']:
                        test_data['fixed_pattern_pixels'] = test['analysis']['result']['fixed_pattern'][
                            'fixed_pattern_pixels']
                    else:
                        test_data['fixed_pattern_pixels'] = -1
                    if('restricted' in test):
                        test_data['signal_power'] = test['restricted']['values']['value0']
                        test_data['contrast_strength'] = test['restricted']['values']['value1']
                        test_data['noise_fp'] = test['restricted']['values']['value2']
                        test_data['noise_thermal'] = test['restricted']['values']['value3']
                        test_data['noise_thermal_lp_x'] = test['restricted']['values']['value4']
                        test_data['noise_thermal_lp_y'] = test['restricted']['values']['value5']
                        test_data['saturation_fraction'] = test['restricted']['values']['value6']
                        test_data['low_pass_fraction'] = test['restricted']['values']['value7']
                        test_data['high_freq_noise_fraction'] = test['restricted']['values']['value8']
                        test_data['best_angle'] = test['restricted']['values']['value9']
                        test_data['displacement'] = test['restricted']['values']['value10']
                        test_data['displacement_error'] = test['restricted']['values']['value11']
                        test_data['displacement_fit_error'] = test['restricted']['values']['value12']
                        test_data['displacement_curvature'] = test['restricted']['values']['value13']
                        test_data['displacement_rel_curvature'] = test['restricted']['values']['value14']
                        test_data['displacement_max_error'] = test['restricted']['values']['value15']
                        test_data['noise_thermal_lp_x/noise_thermal_lp_y'] = test_data['noise_thermal_lp_x'] / test_data[
                        'noise_thermal_lp_y']
            if (test_data):
                internal_result.append(test_data)

    df = pd.DataFrame(internal_result)
    df.to_excel(os.path.join(output_path, os.path.basename(output_path) + '_summary.xls'), encoding='utf-8')
    '''fig, axes = plt.subplots(nrows=2, ncols=2)
    ax0, ax1, ax2, ax3 = axes.flatten()

    ax0.hist(df['noise_thermal_lp_x'], bins=20, label='noise_thermal_lp_x')
    ax0.set_title('noise_thermal_lp_x')

    ax1.hist(df['noise_thermal_lp_y'], bins=20, label='noise_thermal_lp_y')
    ax1.set_title('noise_thermal_lp_y')

    ax2.hist(df['noise_thermal_lp_x/noise_thermal_lp_y'], bins=20, label='noise_thermal_lp_x/noise_thermal_lp_y')
    ax2.set_title('noise_thermal_lp_x/noise_thermal_lp_y')
    '''
    plt.hist(df['snr_db'], bins=50, label='snr_db', color='r', alpha=0.5)
    plt.hist(df['fixed_pattern_pixels'], bins=50, label='fixed_pattern_pixels', color='b', alpha=0.5)
    plt.legend(loc='best')
    plt.savefig(os.path.join(output_path, os.path.basename(output_path) + '_hist.png'))
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--dll", help="Directory of ctl_rerun_test_analysis.dll, default is ctl_rerun_test_analysis.dll", type=str, default='ctl_rerun_test_analysis.dll')
    parser.add_argument("input", help="Directory of MQT log", type=str)
    parser.add_argument("output", help="Directory of output", type=str)
    parser.add_argument("hwid", help="hardware id, like 0x612, can be found in MTT HardwareID test log", type=str)
    parser.add_argument('product', help='product type like 1229', type=str)
    parser.add_argument('limit_preset', help='MQT limit preset, can be found in MTT json log', type=int)
    parser.add_argument('snr_crop', help='crop pixels of snr test', type=int)
    #parser.add_argument('fp_crop', help='crop pixels of fixed pattern test', type=int)
    parser.add_argument('fp_threshold', help='threshold of fixed pattern test', type=float)

    args = parser.parse_args()

    product_type = 0
    try:
        product_type = product_dict[args.product]
    except KeyError as e:
        logging.error('Product type {} is not supported!'.format(e))
        exit(-1)

    # Path to DLL. This dll needs to be built inside MTT.
    dll_dir = args.dll

    # Test settings
    '''
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
    fp_cropping_left,
    fp_cropping_top,
    fp_cropping_right,
    fp_cropping_bottom,
    is_static
    '''

    settings_list = [args.snr_crop, args.snr_crop, args.snr_crop, args.snr_crop,
                     3.5e-6, 8,
                     args.limit_preset, 15,
                     0.25,
                     True, args.fp_threshold, 10, #args.fp_crop, args.fp_crop, args.fp_crop, args.fp_crop,
                     True]

    output_dir = args.output
    root_dir = args.input
    output_folder = '_'.join(['rerun', str(args.limit_preset), str(args.snr_crop),
                              #str(args.fp_crop), str(args.fp_threshold),
                              str(time.time())])
    output_dir = os.path.join(output_dir, output_folder)

    hw_id = int(args.hwid, 16) if args.hwid.startswith("0x") else int(args.hwid)

    filelist = find_fmi(root_dir)
    ctl_dll = load_library(dll_dir)

    test_mqt2_partial = partial(run_function, ctl_dll = ctl_dll, product_type=product_type, hw_id=hw_id, settings_list=settings_list,
                                out_folder=output_dir.encode(), internal=True)

    with ThreadPoolExecutor() as pool:
        pool.map(test_mqt2_partial, filelist)

    generate_report(output_dir)


