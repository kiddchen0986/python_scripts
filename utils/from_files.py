"""Module containing tools to extract relevant files from directory, and relevant information from files.>
"""
import json
import os
import re
import xml.etree.ElementTree as ET
from shutil import copyfile, rmtree

from utils import utils_common
from utils.utils_common import search_dict
from wrapper import wrapper_common, init_wrapper


def extract_tests_with(directory, *args, compare_key=True, **kwargs):
    """Extract all tests from the directory that contain the args and/or kwargs in their .json file, and copy them to a
    separate folder (filtered_logs) inside the directory.

    NOTE, uses the .json files (primarily designed for result.json). One should not use both args and kwargs at the
    same time; pick one. compare_key is only used together with args

    :param directory: path to a directory containing capture/log files
    :type directory: str
    :param args: arguments to be found in the json file
    :type args: str
    :param compare_key: if True, compare args with the key values, if False, the value (referring to the key-value \
    in a dict)
    :type compare_key: bool
    :param kwargs: arguments to be found in the json file, with corresponding value, ex '"Success" = "Fail"'
    :type kwargs: str
    """
    filtered_tests_directory = os.path.join(directory, "filtered_logs")

    if os.path.exists(filtered_tests_directory):
        rmtree(filtered_tests_directory)

    logs = retrieve_directory_content(directory, parse_json=False)
    tests = {}

    for id_, vals in logs.items():
        # Loop through all captures
        found_json = False

        for val in vals:
            # Loop through the files for that capture
            if ".json" in val:
                parsed_json = parse_json(vals[val])

                if len(args) is not 0:
                    # Keep all tests that have the desired arguments (args)
                    returned = search_dict(parsed_json, list(args), compare_key)
                    tests[id_] = vals
                    tests[id_].update(returned)
                    found_json = True

                if len(kwargs) is not 0:
                    returned_2 = search_dict(parsed_json, [key for key, val in kwargs.items()])

                    for key, value in kwargs.items():

                        if value in returned_2[key]:
                            # Keep all tests that have the desired arguments, and desired values (kwargs)
                            tests[id_] = vals
                            tests[id_].update(returned_2)
                            found_json = True
                            break

                if found_json:
                    break

    os.makedirs(filtered_tests_directory)
    for _, test in tests.items():
        for _, file_path in test.items():
            if isinstance(file_path, str):
                _, file_name = os.path.split(file_path)
                dst_path = os.path.join(filtered_tests_directory, file_name)
                copyfile(src=file_path, dst=dst_path)


def parse_xml(xml_file):
    """Parse an xml_file and return a dict of xml_file

    :param xml_file: path to the xml-file
    :type xml_file: str
    :return: dict of parsed xml file
    :rtype: dict
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    parsed = _parse_xml_rec(root)

    return parsed


def _parse_xml_rec(current_element):
    """The recursive function for parsing xml file. Returns a dict of tag, text, attributes and children

    :param current_element: the current tree element
    :type current_element: xml.etree.ElementTree.Element
    :return: dict of tag, text, attributes and children
    :rtype: dict
    """
    parsed_element = {"tag": current_element.tag,
                      "text": current_element.text,
                      "attr": current_element.attrib,
                      "children": []}

    for child in list(current_element):
        parsed_element["children"].append(_parse_xml_rec(child))

    return parsed_element


def parse_json(file_path):
    """Parse a json file.

    :param file_path: the json file to be parsed
    :type file_path: str
    :return: the parsed dict
    :rtype: dict
    """
    with open(file_path, encoding='utf-8') as json_file_:
        parsed_json = json.load(json_file_)

    return parsed_json


def parse_html(file_path):
    """Parse a html file.

    :param file_path: the html file to be parsed
    :type file_path: str
    :return: the parsed dict
    :rtype: dict
    """
    raise Exception("Not implemented")


def retrieve_directory_content(top, parse_json=True, custom_regex_pattern=None):
    """Organizes files in the directory and returns dict of dicts

    Takes a directory path, organizes the files using capture id. Each capture id receives separate dict, where the
    key to a file is the 'suffix' of the file. Returns a dict containing all capture_id dicts. Dict also contains one
    key 'not_matched' containing a list of all files that were not matched with regex.

    If parse_json is True, will try to parse json files and extract hwid, product_type and pixel_gain.

    If regex_pattern is provided, this pattern is used to parse the filename to distinguish a capture id. Else a
    standard pattern is used. The filenames can vary a lot for the logs, hence a custom regex_pattern may come in handy.
    The regex pattern must return two groups, group(1)

    :param top: path to a directory containing capture/log files
    :type top: str
    :param parse_json: if True, will parse .json files to look for info such as hwid, product_type etc
    :type parse_json: bool
    :param custom_regex_pattern: a regex pattern for parsing the capture id from the filename. Must return two groups; \
    group(1) returns the capture_id and group(2) the file_typ (e.g. checker_inv.png or testlog.json)
    :type custom_regex_pattern: str
    :return: Dict of dicts of file_paths. Key of top dict is the capture id (the prefix) and of the bottom is the \
    'suffix' of the file (eg. checker_inv). Or utils.utils_common.ErrorCode if fail.
    :rtype: dict of dict, or utils.utils_common.ErrorCode

    The file formats that are supported are:
    - 20170616-151119-574_bw_capacitancef.raw
    - 0721H6F8181A0A05_20170613-110919-976_log.txt
    - 00_48004480001468R02B29_painted.png
    - 23123_48004480101469C0274B_reset.png
    - W_4800448010146950C03C_checker_inv.png
    - 0311DAR1500D120D_testlog.json
    - 0311DAR1500D120D_inverted_checkerboard_image!64_176_1.raw
    """
    print("\tSearching for, matching and organizing files in the directory {}".format(top))
    logs = {"not_matched": []}
    if not os.path.isdir(top):
        return utils_common.ErrorCode.IS_NOT_DIRECTORY

    # Regex pattern that will match with the following file formats:
    #   - 20170616-151119-574_bw_capacitancef.raw
    #   - 0721H6F8181A0A05_20170613-110919-976_log.txt
    #   - 00_48004480001468R02B29_painted.png
    #   - 23123_48004480101469C0274B_reset.png
    #   - W_4800448010146950C03C_checker_inv.png
    #   - 0311DAR1500D120D_testlog.json
    #   - 0311DAR1500D120D_inverted_checkerboard_image!64_176_1.raw
    pattern = r'((([^_]*_)?(\d{8}-\d{6}-\d{3}))|([^_]+_[^_]+))_?(.*)'
    pattern_2 = r'([^_]+)_?(.*)'

    for root, dirs, files in os.walk(top):
        for file in files:

            if custom_regex_pattern is None:
                # Using 'standard' regex
                search_obj = re.match(pattern, file)
                if search_obj is None:
                    logs["not_matched"].append(file)
                    continue

                elif search_obj.group(6) == '' or "image!" in search_obj.group(6):
                    # For handling the files of format 0311DAR1500D120D_testlog.json and
                    # 0311DAR1500D120D_inverted_checkerboard_image!64_176_1.raw
                    search_obj = re.match(pattern_2, file)
                    id_ = search_obj.group(1)
                    file_name = search_obj.group(2)

                else:
                    id_ = search_obj.group(1)
                    file_name = search_obj.group(6)

            else:
                # Using the custom regex pattern. Must return provide capture_id from group(1) and
                # file_name from group(2)
                search_obj = re.match(custom_regex_pattern, file)
                if search_obj is None:
                    logs["not_matched"].append(file)
                    continue

                else:
                    id_ = search_obj.group(1)
                    file_name = search_obj.group(2)

            if id_ not in logs:
                # Add new dict for new capture_id
                logs[id_] = {"hwid": None,
                             "product_type": None,
                             "pixel_gain": None}

            # Add the file path to the corresponding capture dictionary
            logs[id_][file_name] = os.path.join(root, file)

            if parse_json:
                if ".json" in file_name:
                    # If json file, extract hwid and product_type
                    parameters = retrieve_test_parameters(logs[id_][file_name])
                    logs[id_]["hwid"] = parameters["hwid"]
                    logs[id_]["product_type"] = parameters["product_type"]
                    logs[id_]["pixel_gain"] = parameters["pixel_gain"]

    return logs


def retrieve_test_parameters(json_file, encoding="utf-8"):
    """Extracts test parameters such as hwid, product_type and pixel_gain from json file if available

    :param json_file: the json file containing hwid and product_type
    :type json_file: str
    :param encoding: the encoding of the file
    :type encoding: string
    :return: dict of parameters
    :rtype: dict
    """
    with open(json_file) as json_file_:
        try:
            parsed_json = json.load(json_file_, encoding=encoding)
        except UnicodeDecodeError as e:
            print("UnicodeDecodeError ({}) for {}: {}".format(e.encoding, e.object[e.start:e.end], e.reason))
            return None

    parameters = {"product_type": None,
                  "hwid": None,
                  "pixel_gain": None}

    try:
        parameters["product_type"] = parsed_json["Product"]
    except KeyError:
        pass

    if "TestReportItems" not in parsed_json:
        return parameters

    for test_report_items in parsed_json["TestReportItems"]:
        if "Hardware Id" == test_report_items["Name"]:
            try:
                parameters["hwid"] = test_report_items["Result"]["TestLog"]["Steps"]["measurement"]["Items"]["hwid"]
            except KeyError:
                pass

        if "Capacitance Test" == test_report_items["Name"]:
            try:
                parameters["pixel_gain"] = test_report_items["Result"]["TestLog"]["Steps"]["initialization"]["Items"]["pixel_gain"]
            except KeyError:
                pass
            break

    return parameters


def find_files(directory, suffix, *sub_strings, sub_directories=False):
    """Searches the directory for files with a certain file ending and with name containing the strings in sub_string

    :param directory: the directory in which files should be looked for
    :type directory: str
    :param suffix: file-ending
    :type suffix: str
    :param sub_strings: sub strings that should be found in the
    :type sub_strings: Tuple[str...]
    :param sub_directories: If True, also look in sub-directories
    :type sub_directories: bool
    :return: list of file paths
    :rtype: list of str
    """
    found_files = []

    if not os.path.isdir(directory):
        return utils_common.ErrorCode.IS_NOT_DIRECTORY

    for root, dirs, files in os.walk(directory):
        for file in files:

            if _match_file(file, suffix, [sub for sub in sub_strings]):
                found_files.append(os.path.join(root, file))

        if sub_directories:
            # Search sub directories
            for dir_ in dirs:
                found_files.extend(find_files(dir_, suffix, sub_strings, sub_directories))

    return found_files


def _match_file(file_name, suffix, sub_strings):
    """Returns True if file_name contains suffix and sub_strings, else False

    :param file_name: the file name
    :type file_name: str
    :param suffix: file-ending
    :type suffix: str
    :param sub_strings: sub strings that should be found in the
    :type sub_strings: list of str
    :return: True if match, else False
    :rtype: bool
    """
    for sub_string in sub_strings:
        pattern = "(" + sub_string + ")"
        search_object = re.search(pattern, file_name)

        if search_object is None:
            return False

    pattern = "." + suffix + "$"
    search_object = re.search(pattern, file_name)

    if search_object is None:
        return False
    else:
        return True


def retrieve_capacitance_settings(test_package):
    """Retrieves the capacitance_settings from product_type-associated CapacitanceSettingsXXX.xml file.

    :param test_package: dictionary containing config, result, error_code etc. Must contain product_type
    :type test_package: dictionary
    :return: test_package
    :rtype: dictionary
    """
    if "product_type" not in test_package:
        test_package["error_code"] = wrapper_common.ErrorCode.TEST_PACKAGE_DOES_NOT_INCLUDE_PRODUCT_TYPE
        return test_package

    if isinstance(test_package["product_type"], str):
        pattern = "PRODUCT_TYPE_FPC(\d{4})$"
        search_object = re.match(pattern, test_package["product_type"])

        if search_object is not None:
            test_package["code"] = search_object.group(1)
        else:
            test_package["error_code"] = wrapper_common.ErrorCode.TEST_PACKAGE_DOES_NOT_INCLUDE_PRODUCT_TYPE
            return test_package

    else:
        test_package["error_code"] = wrapper_common.ErrorCode.TEST_PACKAGE_DOES_NOT_INCLUDE_PRODUCT_TYPE

    if init_wrapper.CURRENT_MTT_DIRECTORY is wrapper_common.ErrorCode.MTT_NOT_INITIALIZED:
        test_package["error_code"] = wrapper_common.ErrorCode.MTT_NOT_INITIALIZED
        return test_package

    cap_setting_files = find_files(init_wrapper.CURRENT_MTT_DIRECTORY,
                                   'xml',
                                   "CapacitanceSettings",
                                   test_package["code"])

    if len(cap_setting_files) is not 1:
        test_package["error_code"] = utils_common.ErrorCode.NO_GOOD_FILE_MATCH
        return test_package

    parsed = parse_xml(cap_setting_files[0])["children"]
    test_package["capacitance_settings"] = {}

    for element in parsed:
        if len(element["children"]) is not 0:
            # If the element has children (probably only BlobConfig)
            test_package["capacitance_settings"][element["tag"]] = element["children"]
        else:
            # Convert string to boolean or number
            val = element["text"]
            if val == "true" or val == "True":
                val = True
            elif val == "false" or val == "False":
                val = False
            elif utils_common.is_number(val):
                val = float(val)

            test_package["capacitance_settings"][element["tag"]] = val

    return test_package
