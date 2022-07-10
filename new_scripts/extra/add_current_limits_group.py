from collections import OrderedDict
import json
import os
from bs4 import BeautifulSoup
import re
import logging
import sys


path = r"C:\Users\kidd.chen\OneDrive - Fingerprint Cards AB\Skrivbordet\temp\test"
xml_path = r"C:\WorkSpace\mtt\dev\dev2\production_test_package_capacitive\TestsModuleInstrument\Settings"

currentConsumption = {
    "rails": "Rail_VDDH_3_3V",
    "samples": 0,
    "deep_sleep": {
        "low": 0.0,
        "high": 0.0
    },
    "active_hp": {
        "low": 0.0,
        "high": 0.0
    }
}

test_limits_group = ["gradientCheckerboard", "swingingCheckerboard", "imageConstant", "currentConsumption", "imageDrive", "moduleQuality2", "afdCal"]


def sort_test_limits_group(test_dict):
    test_temp = OrderedDict()
    test = test_dict["root"]["doc"]["testLimits"]
    for i in test_limits_group:
        for key in test.keys():
            if key == i:
                test_temp[i] = test[key]
    test.clear()
    test = test_temp
    test_dict["root"]["doc"]["testLimits"] = test
    return test_dict


def update_json_file(path, product_type, currentConsumption):
    for file in os.listdir(path):
        with open(os.path.join(path, file), mode="r+") as fr:
            json_dict = json.load(fr)
            if "testLimits" in json_dict["root"]["doc"] and product_type.lower() in \
                    json_dict["root"]["doc"]['header']['productConfig'][0]['value'].lower().replace("_", "-"):
                if "currentConsumption" not in json_dict["root"]["doc"]["testLimits"]:
                    json_dict["root"]["doc"]["testLimits"]["currentConsumption"] = currentConsumption
                    sort_test_limits_group(json_dict)
                    with open(os.path.join(path, file), mode="w") as fw:
                        json.dump(json_dict, fw, indent=4)


test_limits_data = {}
def get_data_html(xml_path, file_name):
    current_consumption_patterns = OrderedDict()
    current_consumption_patterns['Rail'] = r'<Rail>(.*)</Rail>'
    current_consumption_patterns['MeasurementMode'] = r'<MeasurementMode>(.*)</MeasurementMode>'
    current_consumption_patterns['LowerLimitInMilliAmp'] = r'<LowerLimitInMilliAmp>(.*)</LowerLimitInMilliAmp>'
    current_consumption_patterns['UpperLimitInMilliAmp'] = r'<UpperLimitInMilliAmp>(.*)</UpperLimitInMilliAmp>'

    global test_limits_data
    for file in file_name:
        test_dict = OrderedDict()
        if "Active" in file or "DeepSleep" in file:
            with open(os.path.join(xml_path, file), encoding='utf-8', mode='r') as f:
                for line in f.readlines():
                    try:
                        for key, value in current_consumption_patterns.items():
                            res = re.findall(value, line)
                            if res:
                                if key == "Rail":
                                    test_dict[key] = str(res[0])
                                if "Active" in file:
                                    if key == "LowerLimitInMilliAmp":
                                        test_dict["Active_LowerLimitInMilliAmp"] = res[0]
                                    elif key == "UpperLimitInMilliAmp":
                                        test_dict["Active_UpperLimitInMilliAmp"] = res[0]
                                elif "DeepSleep" in file:
                                    if key == "LowerLimitInMilliAmp":
                                        test_dict["DeepSleep_LowerLimitInMilliAmp"] = res[0]
                                    elif key == "UpperLimitInMilliAmp":
                                        test_dict["DeepSleep_UpperLimitInMilliAmp"] = res[0]

                    except Exception as ex:
                        logging.error(file, sys.exc_info())
            if test_limits_data:
                test_limits_data.update(test_dict)
            else:
                test_limits_data = test_dict
    return test_limits_data


def update_test_limit_value(test_limits):
    '''
    update test limit value by using test data parsing from TestsModule.Instrument
    '''
    current_consumption_temp = OrderedDict()
    current_consumption_temp['deep_sleep'] = {}
    current_consumption_temp['active_hp'] = {}

    current_consumption_temp['rails'] = test_limits["Rail"]
    current_consumption_temp["deep_sleep"]["low"] = float(test_limits["DeepSleep_LowerLimitInMilliAmp"])
    current_consumption_temp["deep_sleep"]["high"] = float(test_limits["DeepSleep_UpperLimitInMilliAmp"])
    current_consumption_temp["active_hp"]["low"] = float(test_limits["Active_LowerLimitInMilliAmp"])
    current_consumption_temp["active_hp"]["high"] = float(test_limits["Active_UpperLimitInMilliAmp"])
    current_consumption_temp["samples"] = 20

    return current_consumption_temp


def add_current_test_limit_group(xml_path):
    global currentConsumption

    # get all product types that had configured .xml files in TestsModule.Instrument
    product_types = []
    for file in os.listdir(xml_path):
        if "Active" in file or "DeepSleep" in file:
            product_types.append(file.split("_")[-1].split(".")[0])

    # get test limits data for every product type
    for product_type in set(product_types):
        file_name = []
        for file in os.listdir(xml_path):
            if "Active" in file or "DeepSleep" in file:
                if product_type == file.split("_")[-1].split(".")[0]:
                    file_name.append(file)

        if len(file_name) == 2:
            test_limits = get_data_html(xml_path, file_name)

            # get current limits by using test data parsing from TestsModule.Instrument
            currentConsumption.update(update_test_limit_value(test_limits))

            # copy current limits to json files of sensor_settings
            update_json_file(path, product_type, currentConsumption)


if __name__ == "__main__":
    '''
    refer to CET-1147, auto parsing the test limit data from test settings xml in TestsModule.Instrument,
    and then insert to test limit group of testdata json in sensor_settings
    '''
    add_current_test_limit_group(xml_path)
