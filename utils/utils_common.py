"""Common structs and functions used across the utils package."""
import os
import datetime
import re
from enum import Enum

TIME_DATE = None


def update_time_date_stamp():
    """Updates the global TIME_DATE variable to the current time_stamp and also returns its value

    :return: the current date & time of the format YEARMONTHDATE_HOUR:MINUTE
    :rtype: str
    """
    global TIME_DATE
    TIME_DATE = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return TIME_DATE


def parse_date_stamp(date_string):
    """Parse the date stamp from a string representation of a string

    Currently only supports the following format for parsing: "2014-12-08T17:59:31.4375961+07:00"

    :param date_string: string representation of date, of the following format "2014-12-08T17:59:31.4375961+07:00"
    :type date_string: str
    :return: DateTime obj
    :rtype: DateTime
    """
    return datetime.datetime.strptime(date_string[:-7], "%Y-%m-%dT%H:%M:%S.%f")


def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='#'):
    """Call in a loop to create terminal progress bar

    :param iteration: current iteration
    :type iteration: int
    :param total: total iterations
    :type total: int
    :param prefix: prefix string
    :type prefix: str
    :param suffix: suffix string
    :type suffix: str
    :param decimals: positive number of decimals in percent complete
    :type decimals: int
    :param length: character length of bar
    :type length: int
    :param fill: bar fill character
    :type fill: str

    Sample usage ::

        from time import sleep
        # A List of Items
        items = list(range(0, 57))
        l = len(items)

        # Initial call to print 0% progress
        print_progress_bar(0, l, prefix='Progress:', suffix='Complete', length=50)
        for i, item in enumerate(items):
            # Do stuff...
            sleep(0.1)
            # Update Progress Bar
            print_progress_bar(i + 1, l, prefix='Progress:', suffix='Complete', length=50)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()


class ErrorCode(Enum):
    """Python script specific error codes enum"""
    OK = 0
    IS_NOT_DIRECTORY = 1
    NO_GOOD_FILE_MATCH = 2


def is_number(s):
    """Check if string is number.

    :param s: number
    :type s: str
    :return: True if number
    :rtype: bool
    """
    try:
        float(s)
        return True
    except ValueError:
        return False


def product_type_string_format(product_type):
    """Retrieve 4 consecutive digits from product_type and add the prefix 'PRODUCT_TYPE_FPC'

    :param product_type: the product_type input
    :type product_type: str
    :return: full product_type string
    :rtype: str
    """
    search_pattern = r'\D*(\d{4})\D*'
    search_obj = re.search(search_pattern, product_type)
    print(search_obj.groups())
    if search_obj:
        return "PRODUCT_TYPE_FPC" + search_obj.group(1)
    return product_type


def get_test_name(container):
    """Retrieves the test_name from the container.

    IMPORTANT: currently only works for dict

    :param container: dictionary (eg test_package or test_sequence_package). Any dict containing one of the following \
    keys can be used: "test_sequence", "test_name", "native_function". KeyError is raised if this information is \
    not provided.
    :type container: dict
    :return: test_name
    :rtype: str
    """
    if "test_sequence" in container:
        test_name = container["test_sequence"]
    elif "test_name" in container:
        test_name = container["test_name"]
    elif "native_function" in container:
        test_name = container["native_function"]
    else:
        print("in else")
        raise KeyError("'Neither test_sequence', 'test_name' nor 'native_function' provided in the dict received."
                       " (Expected test_sequence_package or test_package.)")

    return test_name


def create_file_path(test_name_container, suffix, *pre_suffixes, sub_dir=None):
    """A csv file path is created.

     A new csv file path is created using the current date/time and test_name found in the test_name_container. If the
     container is not a str, the name is retrieved from the function get_test_name.

    :param test_name_container: some container containing the test name.
    :type test_name_container: str or e.g. dict
    :param suffix: the file ending
    :type suffix: str
    :param pre_suffixes: any number of extra suffixes before file ending
    :type pre_suffixes: str
    :param sub_dir: name of the sub_directory wanted
    :type sub_dir: str
    :return: file_path
    :rtype: str
    """
    current_wdr = os.getcwd()
    pattern = ".+?(?=python_scripts)"
    search_object = re.match(pattern, current_wdr)
    dir_path = os.path.join(search_object.group(0), "python_scripts", "i-o_files", "results")

    if isinstance(test_name_container, str):
        test_name = test_name_container
    else:
        test_name = get_test_name(test_name_container)

    suffix = re.sub(r'\.', '', suffix)
    before_suffix = ""

    for pre in pre_suffixes:
        before_suffix += "_" + pre

    if sub_dir is not None and isinstance(sub_dir, str):
        # Set the dir_path to the sub_dir
        dir_path = os.path.join(dir_path, "{}_{}".format(TIME_DATE, sub_dir))

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        file_name = "{}{}.{}".format(test_name, before_suffix, suffix)

    else:
        file_name = "{}_{}{}.{}".format(TIME_DATE, test_name, before_suffix, suffix)

    return os.path.join(dir_path, file_name)


def flatten_dict(d, keys=False, ret=None):
    """Flattens dicts to list

    Takes a dict, flattens it and returns a list of the values (if keys is False) or the keys (if keys is True).
    Nested dicts will also be flattened. Assumes that lists only contains elements of the same type (a list of dict
    only has dicts, not a str element).

    NOTE! The key to nested lists or dicts will be lost.

    :param d: the current dictionary
    :type d: dict
    :param keys: If True, keep the keys and drop the values. If False, keep the the values and drop the keys
    :type keys: bool
    :param ret: the flattened dict
    :type ret: list
    :return: the flattened dict
    :rtype: list
    """
    if ret is None:
        ret = []

    for k, v in sorted(d.items()):
        if isinstance(v, dict):
            flatten_dict(v, keys, ret)

        elif isinstance(v, list):
            if len(v) is not 0:

                if isinstance(v[0], dict):
                    for d_2 in v:
                        flatten_dict(d_2, keys, ret)

                else:
                    if keys:
                        ret.append(k)
                    else:
                        ret.append(v)

        else:
            if keys:
                ret.append(k)
            else:
                ret.append(v)

    return ret


def search_dict(d, needles, look_for_key=True):
    """Recursively search for values in a dict. Can also handle sub-dicts and sub-lists.

    When looking for key and there are multiple keys in the dict-tree with the same name, it is possible to be more
    precise about which key that is looked for in the tree. This can be done by specifying the 'parent' of the key in
    the same string, followed by 2 hashtag symbols (##), and finally the looked for key. For example, if
    'uniformity_level' which has the d, t and op value is to be extracted, but only 'd' is of interest, it is possible
    to write "uniformity_level##d". This can be done in several levels, i.e. by specifying another previous parent:
    "Items##uniformity_level##d". This allows the user to be more exact about the key's location in the tree.

    NOTE, the above-mentioned feature is only available for keys (not when looking for values) and only when the keys
    are of type str.

    :param d: the dict
    :type d: dict
    :param needles: the values that is searched for in the dict
    :type needles: list of str
    :param look_for_key: if true, will look for a key with the value 'needle', and returns its value. Else it will look
     for values with a value in 'needles' and return the key
    :type look_for_key: bool
    :return: dict of list of values or list of keys (depending on the parameter look_for_key)
    :rtype: dict
    """
    def find_specific_key(current, s_keys):
        """Internal function used to check whether the found keys have sub-keys that correspond with specification

        :param current: the current value
        :type current: should be a dict if the key exists at the specified position
        :param s_keys: list of remaining sub-keys
        :type s_keys: list of str
        :return the value found using the specified key
        """
        s_k = s_keys[0]
        if s_k == '':
            return None

        found = []
        for curr in current:

            try:
                curr = curr[s_k]
            except (TypeError, KeyError):
                continue

            if len(s_keys) > 1:
                find = find_specific_key([curr], s_keys[1:])

                if not find:
                    continue
                else:
                    found.extend(find)
            else:
                found.append(curr)

        return found

    if not look_for_key:
        # Simply return the results of search_dict_rec
        return search_dict_rec(d, needles, look_for_key)

    parent_keys = []
    all_keys = {}
    specified_location = False
    for n in needles:
        split = n.split("##")
        if len(split) > 1:
            specified_location = True

        all_keys[split[0]] = split[1:]
        parent_keys.append(split[0])

    if not specified_location:
        # Simply return the results of search_dict_rec
        return search_dict_rec(d, needles, look_for_key)

    search_result = search_dict_rec(d, parent_keys, look_for_key)
    filtered_search_result = {}

    for n in needles:
        key = n.split("##")[0]

        if not all_keys[key]:
            # If this key does not have a specified location, use the initial 'non-location-specific' result
            filtered_search_result[n] = search_result[key]
        else:
            filtered_search_result[n] = find_specific_key(search_result[key], all_keys[key])

    return filtered_search_result


def search_dict_rec(d, needles, look_for_key=True, _result=None):
    """Recursively search for values in a dict. Can also handle sub-dicts and sub-lists.

    :param d: the dict
    :type d: dict
    :param needles: the values that is searched for in the dict
    :type needles: list of str
    :param look_for_key: if true, will look for a key with the value 'needle', and returns its value. Else it will look
     for values with a value in 'needles' and return the key
    :type look_for_key: bool
    :param _result: the dict containing the results that have been found
    :type _result: dict
    :return: dict of list of values or list of keys (depending on the parameter look_for_key)
    :rtype: dict
    """
    # needles = [str(needle) for needle in needles]

    if _result is None:
        _result = dict((key, []) for key in needles)

    for key_, val_ in d.items():
        if look_for_key:
            if key_ in needles:
                _result[key_].append(val_)
        else:
            if isinstance(val_, dict):
                # The recursive call is done below
                pass
            elif isinstance(val_, list):
                # The recursive call is done below
                pass
            else:
                if str(val_) in needles:
                    _result[str(val_)].append(key_)

        if isinstance(val_, dict):
            search_dict_rec(val_, needles, look_for_key, _result)
        elif isinstance(val_, list):
            for val in val_:
                if isinstance(val, dict):
                    search_dict_rec(val, needles, look_for_key, _result)
                if str(val) in needles:
                    _result[str(val)].append(key_)

    return _result