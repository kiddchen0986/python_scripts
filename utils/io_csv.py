"""Module used to read and write csv files"""
import csv
import os
from wrapper.fpc_c_core.fpc_sensor_info import DeadPixelsInfo
from wrapper.prodtestlib.checkerboard import CheckerboardResult, checkerboard_combined_test
from wrapper.prodtestlib.capacitance import BlobResult, CapacitanceResult
from wrapper.prodtestlib.prodtestlib_common import FPCErrorCode
from utils.utils_common import create_file_path
from wrapper.wrapper_common import ErrorCode

# Following list values are used in the init_write_test_seq_pack and the write_test_seq_pack, for formatting
result_keys = ["result", "capacitance_result", "blob_result"]
config_keys = ["config", "pxl_ctrl_info"]
result_headers_if_available = ["product_type", "hwid", "pixel_gain"]


def retrieve_std_values_from_struct(struct):
    """Translates any non-standard data types to standard types found in a struct

    For instance, the result_struct is to be written to csv file, there is a pixel_error_per_row array that
    automatically can't be translated to a writeable value to be written to a cell. This function loops through that
    array and adds all the values of that array to a writeable list.

    NOTE: can only standardize arrays. Knows if the value is an array if the struct also contains an attribute with the
    same name but with the suffix '_size'. Important to add this attribute to structs if developer wishes to
    'standardize' an array.

    :param struct: the struct to be 'standardized'
    :type struct: eg CheckerboardConfig, or CheckerboardResult
    :return: list of standardized values
    :rtype: list
    """
    row = []
    for attr, _ in struct._fields_:
        # Loop through the attributes of the struct

        if attr + "_SIZE" in struct.__dict__.keys():
            # If struct has an attribute with the same name as attr but with the suffix '_SIZE', it is presumed to be
            # an array.

            element = []
            for i in range(getattr(struct, attr + "_SIZE")):
                # The array is looped and its values are added to the list
                element.append(getattr(struct, attr)[i])

            if isinstance(struct, DeadPixelsInfo) and attr == "dead_pixels_index_list":
                # Remove all 0's
                element = [val for val in element if val is not 0]

            if isinstance(struct, CheckerboardResult) and attr in ["pixel_errors_per_row", "pixel_errors_per_col"]:
                # Remove all 0's
                element = [(i, val) for i, val in enumerate(element) if val is not 0]
                # element = ["r_{}: {}".format(i, val) for i, val in enumerate(element) if val is not 0]

            if isinstance(struct, BlobResult) and attr in ["blob_image"]:
                # Remove all 0's
                element = [(i, val) for i, val in enumerate(element) if val is not 0]
                # element = ["r_{}: {}".format(i, val) for i, val in enumerate(element) if val is not 0]

            if isinstance(struct, BlobResult) and attr is "detection_image":
                # Only add interesting values
                blob_threshold = 3.5e-6
                element = [(i, val) for i, val in enumerate(element) if val > blob_threshold]
                # element = ["r_{}: {}".format(i, val) for i, val in enumerate(element) if val is not 0]

            if isinstance(struct, CapacitanceResult) and attr in ["capacitance_image", "capacitance_image_float"]:
                # Add empty cell instead
                element = "-"

        else:
            element = getattr(struct, attr)

        # Add element to row
        row.append(element)

    return row


def init_write_test_seq_pack(test_seq_pack, file_path=None, dead_pixels_list=True):
    """Prepares a csv file for test_sequence_packages with config settings and headers

    Write the config settings at the top as well as prepares the result headers. Ignores any other information in the
    file, simply adding to the bottom of the file

    :param test_seq_pack: test_sequence_package containing test_sequence name, test_id, and list of test_packages
    :type test_seq_pack: dictionary
    :param file_path: path to the existing or not existing csv file
    :type file_path: str
    :param dead_pixels_list: whether the dead_pixels_list is to be written or not
    :type dead_pixels_list: bool
    :return: the path to the .csv file
    :rtype: str
    """

    if file_path is None:
        file_path = create_file_path(test_seq_pack, ".csv")

    intro = ["types_order: "]
    config_title = ["Config"]
    config_headers = []
    config_values = []
    result_title = ["Result"]
    result_headers = ["test_id", "file_paths", "pass", "error_code"]

    for extra_header in result_headers_if_available:
        if extra_header in test_seq_pack:
            # If the attribute is in the test_package, add it to the .csv file
            result_headers.append(extra_header)

    # Use to align test_type at start of type parameters/results
    config_test_type = []
    result_test_type = [""]*len(result_headers)

    if dead_pixels_list:
        # Add the dead_pixel_list attribute to headers
        dpl_headers = [param for param, _ in test_seq_pack["test_packages"][-1]["dead_pixels_list"]._fields_]
        result_headers.extend(dpl_headers)

        # Add a marker at the corresponding column where dead_pixel_list attributes start
        result_test_type.append("dead_pixels_list")

        # Add emtpy cells to prepare for next type test_package marker
        result_test_type.extend([""] * (len(dpl_headers) - 1))

    for tp in test_seq_pack["test_packages"]:
        # Loop through the test_packages
        if "test_name" in tp:
            test_name = tp["test_name"]
        else:
            test_name = tp["native_function"]

        # Get the parameter names and config values
        keys = sorted(list(tp))
        for key in keys:

            if key in config_keys:
                tp_config_headers = [param for param, _ in tp[key]._fields_]
                config_headers.extend(tp_config_headers)

                config_values.extend(retrieve_std_values_from_struct(tp[key]))

                # Add a marker at the corresponding column where the new test_type/test_type_struct starts
                config_test_type.append(test_name + "." + type(tp[key]).__name__)

                # Add emtpy cells to prepare for next test_package marker
                config_test_type.extend([""] * (len(tp_config_headers) - 1))

        # Get the result headers
        for key in keys:
            if key in result_keys:
                tp_result_headers = [param for param, _ in tp[key]._fields_]
                result_headers.extend(tp_result_headers)
                result_headers.append("error_code")

                # Add a marker at the corresponding column where the new test_type/test_type_struct starts
                result_test_type.append(test_name + "." + type(tp[key]).__name__)

                # Add emtpy cells to prepare for next test_package marker
                result_test_type.extend([""] * (len(tp_result_headers) - 1))

        # Add the types
        intro.append(test_name)

    rows = [intro,
            [],
            config_title,
            config_test_type,
            config_headers,
            config_values,
            [],
            result_title,
            result_test_type,
            result_headers]

    # Write the rows to the file
    with open(file_path, 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';')
        csv_writer.writerows(rows)

    return file_path


def write_test_seq_pack(test_seq_pack, file_path=None, dead_pixels_list=True):
    """Write the test_sequence_package to csv file

    NOTE: there is no check that it is the same test_packages with the same result structs as in the result header
    in the file. It is up to the test_sequence designer to check this.

    If the file_path is not specified, a new csv file is created and initialized. If the file is specified
    the results are merely added to the file; the previous information in the file is NOT overwritten.

    :param test_seq_pack: test_sequence_package containing test_sequence name, test_id, and list of test_packages
    :type test_seq_pack: dictionary
    :param file_path: path to the existing or not existing csv file
    :type file_path: str
    :param dead_pixels_list: whether the dead_pixels_list is to be written or not
    :type dead_pixels_list: bool
    :return: the path to the .csv file
    :rtype: str
    """
    if file_path is None:
        file_path = create_file_path(test_seq_pack, ".csv")

    initialize = False
    # Check if file exists
    if not os.path.isfile(file_path):
        initialize = True

    if initialize:
        init_write_test_seq_pack(test_seq_pack, file_path, dead_pixels_list)

    # Add test_id, files and the test sequence pass/fail to the row
    try:
        error_code = test_seq_pack["error_code"]
        if error_code is []:
            error_code = ErrorCode.OK
    except KeyError:
        error_code = ErrorCode.OK
    finally:
        result_values = [test_seq_pack["test_id"],
                         " ".join(test_seq_pack["files"]),
                         test_seq_pack["pass"],
                         error_code]

    for extra_header in result_headers_if_available:
        if extra_header in test_seq_pack:
            # If the attribute is in the test_package, add it to the .csv file
            result_values.append(test_seq_pack[extra_header])

    if dead_pixels_list:
        # Add dead_pixels_list values to the row
        result_values.extend(retrieve_std_values_from_struct(test_seq_pack["test_packages"][-1]["dead_pixels_list"]))
        # result_values.extend([getattr(test_seq_pack["test_packages"][-1]["dead_pixels_list"], param)
        #                       for param, _ in test_seq_pack["test_packages"][-1]["dead_pixels_list"]._fields_])

    for tp in test_seq_pack["test_packages"]:
        # Loop through the test_packages, adding the result values to the row
        tp_result_headers = []
        keys = sorted(list(tp))
        for key in keys:

            if key in result_keys:
                result_values.extend(retrieve_std_values_from_struct(tp[key]))
                try:
                    error_code = tp["error_code"]
                except KeyError:
                    error_code = ErrorCode.OK
                finally:
                    result_values.append(error_code)

    # Write the row to the csv file
    with open(file_path, 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';')
        csv_writer.writerow(result_values)

    return file_path


def write_top_of_file(headers_values, file_path, *title):
    """Takes a dict, where the key values are the headers and the values are the values, and writes to the top of the
    .csv file. Also adds empty row afterwards.

    Unfortunately it is not possible to insert new values at a specific row/column of the .csv file without reading all
    the old values and writing a new .csv file with the inserted values in the data.

    :param headers_values: dict of header-value pairs
    :type headers_values: dict
    :param file_path: path to the existing or not existing csv file
    :type file_path: str
    :param title: a potential title/header for the newly added values
    :type title: none or several values to be added to the 'title'-row
    :return: the path to the .csv file
    :rtype: str
    """
    if not os.path.isfile(file_path):
        print("Error! This is not a file: {}".format(file_path))
        return

    data = []

    # Read all previous data
    with open(file_path, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')

        for row in csv_reader:
            data.append(row)
        # try:
        #     data.extend(csv_reader)
        # except _csv.Error:
        #     print(csv_reader)

    # Get the new values
    headers, values = [], []
    for header, value in headers_values.items():
        headers.append(header)

        if isinstance(value, list):
            # Remove any chinese unknown characters before writing
            cnt = 1     # Limit the number of elements to 20 (csv files can only have so many characters in a cell)
            encoded = '{} elements: ['.format(len(value))
            for item in value:
                encoded += str(item.encode('ascii', 'ignore')) + ', '
                if cnt > 20:
                    value = encoded[:-2] + ' ...]'
                    break

                cnt += 1
                value = encoded[:-2] + ']'

        values.append(value)

    # Add the new values
    data.insert(0, headers)
    data.insert(1, values)
    data.insert(2, [""])        # Empty row

    title_row = [val for val in title]
    if len(title_row) > 0:
        data.insert(0, title_row)

    # Write the data with the appended values
    with open(file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';')
        csv_writer.writerows(data)

    return file_path


def write_row(values, file_path):
    """Write a row of values to a csv_file

    If the file has not yet been created, it will be created. Ignores any UnicodeEncodeErrors.

    :param values: A list of values
    :type values: list of elements
    :param file_path: path to the csv file
    :type file_path: str
    :return: the path to the .csv file
    :rtype: str
    """
    with open(file_path, 'a', newline='', encoding='utf-8', errors='ignore') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';')
        csv_writer.writerow(values)

    return file_path


def write_rows(values, file_path):
    """Write several rows of values to a csv_file

    If the file has not yet been created, it will be created. Ignores any UnicodeEncodeErrors.

    :param values: A list of list of values
    :type values: list of list of elements
    :param file_path: path to the csv file
    :type file_path: str
    :return: the path to the .csv file
    :rtype: str
    """
    with open(file_path, 'a', newline='', encoding='utf-8', errors='ignore') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';')
        csv_writer.writerows(values)

    return file_path


def read_file(file_path, headers=None, beg=None, end=-1):
    """Read the contents of .csv file by row, return in list of dictionaries.

    Specify which row number to be interpreted as header, or provide list of header values. The length of a list of
    headers will automatically tell how many cells to be read per row. If headers is None, first row of the .csv file
    will be interpreted as header values. Each row will be a separate dict in the returned list.

    :param file_path: path to the existing or not existing csv file
    :type file_path: str
    :param headers: key value in dict, either row number or
    :type headers: int or list
    :param beg: first row to read
    :type beg: int
    :param end: last row to read
    :type end: int
    :return: list of dicts, key is header and value is the cell value
    :rtype: list of dicts
    """
    if not os.path.isfile(file_path):
        print("Error! This is not a file: {}".format(file_path))
        return

    data = []
    row_nbr = 1

    # If row number is provided
    if isinstance(headers, int):
        row_nbr = headers
        headers = None

    if not headers:
        # If none or if list is empty
        headers = []

        # Read header values
        with open(file_path, 'r', newline='') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')

            for i, row in enumerate(csv_reader):
                if i == row_nbr - 1:
                    headers = row

    if not beg:
        beg = row_nbr + 1

    # Read sheet by row and save to data
    with open(file_path, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')

        for i, row in enumerate(csv_reader):
            if i > beg - 2 and i != end:
                data.append(dict(zip(headers, row[:len(headers) - 1])))

    return data