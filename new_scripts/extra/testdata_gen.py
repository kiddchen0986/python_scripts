# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#
import json
import os
import sys
import argparse


def json_load(path, filename, data_type):
    if data_type not in filename:
        print("Error: please check the 2nd argument is testsettings.json, 3rd is tesetlimits.json!")
        sys.exit(0)

    try:
        with open(os.path.join(path, data_type, filename)) as f_obj:
            settings = json.load(f_obj)
    except FileNotFoundError:
        print("Error: file {} is not found, please check file or path is correct!")
    else:
        return settings


def get_valid_test_settings(test_settings_json_data):
    register_groups = ['groupName', 'comment', 'registers', ]
    test_settings_valid_data = test_settings_json_data.get("root").get("doc").get("data").get('registerGroups')

    if type(test_settings_valid_data) is list:
        for test_settings in test_settings_valid_data:
            for key in list(test_settings.keys()):
                if key not in register_groups:
                    test_settings.pop(key)
                if test_settings['groupName'] == "#current_consumption_active_hp":
                    test_settings['groupName'] = "#active_hp"
                    test_settings['comment'] = "active_hp settings for the sensor"
                if test_settings['groupName'] == "#current_consumption_deep_sleep":
                    test_settings['groupName'] = "#deep_sleep"
                    test_settings['comment'] = "deep sleep settings for the sensor"

    return test_settings_json_data


def separate_checkboard_limits(limits_valid_data):
    groups = ['enabled', 'maxDeviation', 'pixelErrorsUpperLimit', 'subAreasErrorsUpperLimit', 'histogramDeviation',
              'medianDeltaLimit']
    checkboard_types = ['swingingCheckerboard', 'swingingInvertedCheckerboard']
    data = limits_valid_data.get('gradientCheckerboard')

    flag_1 = False
    flag_2 = False
    if type(data) is dict:
        for key in list(data.keys()):
            swing_data = {}
            if key == "maxDeviation_usl_typ":
                data.pop(key)
            if key in checkboard_types:
                swing_data[key] = limits_valid_data['gradientCheckerboard'].pop(key)
                if not flag_1 and key == "swingingCheckerboard":
                    limits_valid_data[key] = {}
                    for group in groups:
                        limits_valid_data[key][group] = limits_valid_data['gradientCheckerboard'].get(group)
                        if limits_valid_data['gradientCheckerboard'].get(group) is None:
                            limits_valid_data[key][group] = False
                    limits_valid_data[key][key[8:].lower()] = swing_data[key]
                    flag_1 = True

                if not flag_2 and key == 'swingingInvertedCheckerboard':
                    limits_valid_data['swingingCheckerboard']['invertedCheckerboard'] = swing_data[key]
                    flag_2 = True


def get_valid_test_limts(limits_json_data):
    vector_types = ['gradientCheckerboard', 'swingingCheckerboard', 'imageConstant', 'imageDrive', 'moduleQuality2']
    limits_data_temp = limits_json_data.get("root").get("doc").get("testLimits")

    if type(limits_data_temp) is dict:
        for key in list(limits_data_temp.keys()):
            if key not in vector_types:
                limits_data_temp.pop(key)

    # separate gradientCheckerboard into gradientCheckerboard and swingingCheckerboard
    separate_checkboard_limits(limits_data_temp)

    # Ensure that these vector types are in the right order
    limits_valid_data = {}
    for vector_type in vector_types:
        limits_valid_data[vector_type] = limits_data_temp[vector_type]

    return limits_valid_data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help=r"pt_doc\deliveries_mts input path", type=str)
    parser.add_argument("settings_filename", help=r"settings file name in deliveries_mts\settings", type=str)
    parser.add_argument("limits_filename", help=r"file name of limits in deliveries_mts\limits", type=str)

    args = parser.parse_args()
    path = args.path
    settings_filename = args.settings_filename
    limits_filename = args.limits_filename

    print("1. check settings_filename and limits_filename are consistent......")
    if settings_filename[:-17] != limits_filename[:-15]:
        print("Error: please check if settings_filename and limits_filename is consistent!")
        sys.exit(0)

    print("2. Getting json data from {}......".format(settings_filename))
    test_settings_json_data = json_load(path, settings_filename, "settings")

    print("3. Getting json data from {}......".format(limits_filename))
    limits_json_data = json_load(path, limits_filename, "limits")

    print("4. Generating json file {}testdata.json......".format(settings_filename[:-17]))
    get_test_settings = get_valid_test_settings(test_settings_json_data)
    get_test_limits = get_valid_test_limts(limits_json_data)

    if test_settings_json_data.get("root").get("doc").get("data"):
        test_settings_json_data['root']['doc']["testLimits"] = get_test_limits

        filename = os.path.join(args.path, settings_filename[:-17] + "testdata.json")
        with open(filename, 'w') as f:
            json.dump(test_settings_json_data, f, indent=4, sort_keys=False)
    print('Finished')
