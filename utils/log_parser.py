"""Utilities to parse entire directories of mtt logs"""

from utils.from_files import retrieve_directory_content, parse_json, parse_html
from utils.utils_common import parse_date_stamp, search_dict
from utils import histogram
from enum import Enum
import operator
from numbers import Number


class MTTLogs:

    class YieldType(Enum):
        """Enum Class used to tell which capture to choose from when there are multiple for the same unique sensor"""
        FIRST_PASS = 0
        FINAL_PASS = 1

    class SelectResults(Enum):
        """Enum Class to tell which logs to use when some have sensor_id and some do not"""
        WITH_SENSOR_ID = 0
        WITHOUT_SENSOR_ID = 1
        WITH_WITHOUT_SENSOR_ID_SEPARATELY = 2
        WITH_WITHOUT_SENSOR_ID_COMBINED = 3

    class LogType(Enum):
        """Enum Class to tell which kind of logs that are expected"""
        JSON = 0
        JSON_MQT2 = 1
        HTML = 2

    JSON_attributes = {"sensor_id": "SensorId",
                       "uniformity_level": "uniformity_level##d",
                       "signal_strength": "signal_strength##d",
                       "number_of_blob_pixels": "number_of_blob_pixels##d",
                       "snr_db": "snr_db",
                       "afd_plate_value0": "plate_value0##t",
                       "afd_plate_value1": "plate_value1##t",
                       "afd_plate_value2": "plate_value2##t",
                       "afd_plate_value3": "plate_value3##t",
                       "afd_analysis": "analysis##Items##approved",
                       "success": "Success"}

    JSON_MQT2_attributes = {"sensor_id": "SensorId",
                            "uniformity_level": "UniformityLevel",
                            "signal_strength": "SignalStrength",
                            "number_of_blob_pixels": "BlobCount",
                            "snr": "SnrDb",
                            "udr": "Udr",
                            "defective_pixels": "NumberOfDefectivePixels",
                            "success": "Success"}

    HTML_attributes = {}

    def __init__(self):
        """

        """
        self.directory = None
        self.log_type = None
        self.logs_with_sensor_id = {}           # __call__() must be called for this to be set
        self.logs_without_sensor_id = {}        # __call__() must be called for this to be set
        self.failed = {}                        # __call__() must be called for this to be set
        self.overview = {}                      # general_analysis() must be called for this to be set
        self.compiled_result_attributes = {}    # compile_result_attributes() must be called for this to be set

    def __call__(self, directory, log_type=LogType.JSON, custom_regex_pattern=None):
        """Parse the directory and organize all logs with respect to sensor_id.

        Two class attributes updated:
        - self.logs_with_sensor_id: dict of logs organized with respect to sensor_id (key: sensor_id. value: list of \
        dicts (each dict containing a set of captures)
        - self.logs_without_sensor_id: dict of logs organized with respect to capture_id (key: capture_id. value: dict \
        containing a set of captures
        - self.failed: dictionary of logs that failed to get organized due to different reasons. Each key is a different
        reason, with a sub-dict of logs. The different failures are:
            - 'failed_parse_capture_id': List of logs where capture id could not be parsed
            - 'failed_parse_result_logs': Dict of capture dicts that do not have a result log (result.json) file

        :param directory: top directory of logs
        :type directory: str
        :param log_type: which type of logs that are expected in this directory
        :type log_type: MTTLogs.LogType
        :param custom_regex_pattern: a regex pattern for parsing the capture id from the filename. Must return two \
        groups; group(1) returns the capture_id and group(2) the file_typ (e.g. checker_inv.png or testlog.json)
        :type custom_regex_pattern: str
        """
        if not directory and not self.directory:
            raise Exception("No directory provided")

        self.directory = directory
        self.log_type = log_type

        self.logs_with_sensor_id = {}
        self.logs_without_sensor_id = {}
        self.failed = {}
        self.overview = {}
        self.compiled_result_attributes = {}

        self.logs_with_sensor_id, self.logs_without_sensor_id, self.failed = self.parse_logs(directory,
                                                                                             custom_regex_pattern)

    def parse_logs(self, directory, custom_regex_pattern=None):
        """Organize a directory of logs into dictionary, where the top level key is a unique sensor_id

        Two dictionaries returned:
        1. dict of logs organized with respect to sensor_id (key: sensor_id. value: list of dicts (each dict containing
        a set of captures)
        2. dictionary of logs that failed to get organized due to different reasons. Each key is a different reason,
        with a sub-dict of logs. The different failures are:

        - 'failed_parse_capture_id': List of logs where capture id could not be parsed
        - 'failed_parse_result_logs': Dict of capture dicts that do not have a result log (result.json) file

        :param directory: top directory of logs
        :type directory: str
        :param custom_regex_pattern: a regex pattern for parsing the capture id from the filename. Must return two \
        groups; group(1) returns the capture_id and group(2) the file_typ (e.g. checker_inv.png or testlog.json)
        :type custom_regex_pattern: str
        :return: two dictionaries: 1. dictionary of organized logs where sensor_id is key, value is a list of dicts \
        containing logs for each capture. 2. dictionary of logs that failed to be parsed
        :rtype: dict, dict
        """
        dir_content = retrieve_directory_content(directory, parse_json=False, custom_regex_pattern=custom_regex_pattern)
        failed = {'failed_parse_capture_id': dir_content['not_matched'],
                  'failed_parse_result_logs': {}}

        # To avoid a massive rewrite of old code, simply removing code that is not wanted in this function
        unwanted_keys = ["hwid", "product_type", "pixel_gain"]

        # Logs organized in
        with_sensor_id = {}
        without_sensor_id = {}

        for capture_id, files in dir_content.items():
            if capture_id in ['not_matched']:
                continue

            for key in unwanted_keys:
                files.pop(key, None)

            if self.log_type in [MTTLogs.LogType.JSON, MTTLogs.LogType.JSON_MQT2]:
                result_logs = self._parse_result_logs(files, file_ending='.json')
            else:
                result_logs = self._parse_result_logs(files, file_ending='.html')

            if result_logs is None:
                failed['failed_parse_result_logs'][capture_id] = files
                continue

            else:
                if self.log_type is MTTLogs.LogType.JSON:
                    sensor_id_key = MTTLogs.JSON_attributes["sensor_id"]
                elif self.log_type is MTTLogs.LogType.JSON_MQT2:
                    sensor_id_key = MTTLogs.JSON_MQT2_attributes["sensor_id"]
                elif self.log_type is MTTLogs.LogType.HTML:
                    sensor_id_key = MTTLogs.JSON_MQT2_attributes["sensor_id"]

                search_result = MTTLogs.find_in_dict(result_logs, [sensor_id_key])
                if search_result["SensorId"]:
                    sensor_id = search_result["SensorId"][0]
                else:
                    sensor_id = None

            if not sensor_id:
                without_sensor_id[capture_id] = {'files': files,
                                                 'parsed_result_logs': result_logs,
                                                 'capture_id': capture_id,
                                                 'sensor_id': None}

            else:
                if sensor_id not in with_sensor_id:
                    with_sensor_id[sensor_id] = {capture_id: {'files': files,
                                                              'parsed_result_logs': result_logs,
                                                              'capture_id': capture_id,
                                                              'sensor_id': sensor_id}}
                else:
                    with_sensor_id[sensor_id][capture_id] = {'files': files,
                                                             'parsed_result_logs': result_logs,
                                                             'capture_id': capture_id,
                                                             'sensor_id': sensor_id}

        return with_sensor_id, without_sensor_id, failed

    @staticmethod
    def _parse_result_logs(logs, file_ending='.json'):
        """Parse the result file, which typically will be result.json file

        :param logs: logs for a specific capture
        :type logs: dict
        :param file_ending: the result file type which is to be parsed
        :type file_ending: str
        :return: parsed result file, i.e. .json filed parsed to dict
        :rtype: dict
        """
        for file, file_path in logs.items():
            if file.endswith(file_ending):
                if file_ending == '.json':
                    return parse_json(file_path)
                elif file_ending == '.html':
                    return parse_html(file_path)

        return None

    @staticmethod
    def find_in_dict(d, needles, look_for_key=True):
        """Recursively search for values in a dict

        :param d: the dict
        :type d: dict
        :param needles: the values that is searched for in the dict
        :type needles: list of str
        :param look_for_key: if true, will look for a key with the value 'needle', and returns its value. Else it will \
        look for values with a value in 'needles' and return the key
        :type look_for_key: bool
        :return: dict of list of values or list of keys (depending on the parameter look_for_key)
        :rtype: dict
        """
        return search_dict(d, needles, look_for_key)

    def general_analysis(self):
        """Do a general analysis of the data found in the logs dictionary

        Will calculate the number of unique sensors, the number of retests, the yield etc

        :return: dict of overview information
        :rtype: dict
        """
        if not self.logs_with_sensor_id and not self.logs_without_sensor_id:
            raise Warning("No logs to analyse.")

        overview = {'nbr_failed_parse_capture_id': len(self.failed['failed_parse_capture_id']),
                    'nbr_failed_parse_result_logs': len(self.failed['failed_parse_result_logs']),
                    'nbr_without_sensor_id': len(self.logs_without_sensor_id),
                    'nbr_unique_sensors': len(self.logs_with_sensor_id)}

        unique_tests_cnt = 0
        for sensor_id, captures in self.logs_with_sensor_id.items():

            unique_tests_cnt += len(captures)

        overview["nbr_with_sensor_id"] = unique_tests_cnt
        self.overview = overview
        return overview

    def compile_result_attributes(self, attributes=None, select_results=SelectResults.WITH_WITHOUT_SENSOR_ID_COMBINED,
                                  yield_type=YieldType.FIRST_PASS,
                                  analyse=False):
        """Extract specific parts of the test result from the parsed files, and compile them.

        The standard attributes that will be parsed and compiled are:
        ["uniformity_level", "signal_strength", "number_of_blob_pixels", "snr_db"]

        :param attributes: the attributes that are to be extracted and compiled from the parsed result logs
        :type attributes: list of str
        :param select_results: which logs to compile.
        :type select_results: SelectResults
        :param yield_type: Which capture to pick (first or last pass)
        :type yield_type: YieldType
        :param analyse: If the compiled result should be analysed or not
        :type analyse: bool
        :return: dict of compiled result attributes or of analysed result attributes
        :rtype: dict
        """
        def retrieve_attributes_and_organize(capt, comp_dict):
            """Finds the attributes in the current capture dict and organizes them in the compiled dict

            :param capt: the capture dict
            :type capt: dict
            :param comp_dict: the dict wherein all the results are compiled
            :type comp_dict: dict
            """
            results = MTTLogs._retrieve_result_attributes(capt, attributes)
            for k, res in results.items():
                if len(res) > 1:
                    # Adapt the attribute list to specify which one of the keys that is wanted, or handle in code
                    print("The key {} was found {} times in capture_id {}. The first one was chosen.".
                                  format(k, len(res), capt['capture_id']))

                if not res:
                    r = None
                else:
                    r = res[0]

                comp_dict[k].append(r)

        if not attributes:
            if self.log_type is MTTLogs.LogType.JSON:
                attributes = MTTLogs.JSON_attributes.values()

            elif self.log_type is MTTLogs.LogType.JSON_MQT2:
                attributes = MTTLogs.JSON_MQT2_attributes.values()

            elif self.log_type is MTTLogs.LogType.HTML:
                raise Exception("HTML attribute list not yet specified")

        with_sensor_id = {el: [] for el in attributes}
        without_sensor_id = {el: [] for el in attributes}

        if select_results is not MTTLogs.SelectResults.WITHOUT_SENSOR_ID:
            if not self.logs_with_sensor_id:
                print("MTTLogs.logs_with_sensor_id is None/Empty; no logs to parse.")

            for captures in self.logs_with_sensor_id.values():
                if len(captures) > 1:
                    capture = self._pick_capture(captures, yield_type)
                else:
                    capture = list(captures.values())[0]

                retrieve_attributes_and_organize(capture, with_sensor_id)

        if select_results is not MTTLogs.SelectResults.WITH_SENSOR_ID:
            if not self.logs_without_sensor_id:
                print("self.logs_without_sensor_id is None/Empty; no logs to parse")

            for capture in self.logs_without_sensor_id.values():
                retrieve_attributes_and_organize(capture, without_sensor_id)

        # Return depending on select_results
        if select_results is MTTLogs.SelectResults.WITH_SENSOR_ID:
            self.compiled_result_attributes = with_sensor_id

        elif select_results is MTTLogs.SelectResults.WITHOUT_SENSOR_ID:
            self.compiled_result_attributes = without_sensor_id

        elif select_results is MTTLogs.SelectResults.WITH_WITHOUT_SENSOR_ID_SEPARATELY:
            self.compiled_result_attributes = with_sensor_id, without_sensor_id

        elif select_results is MTTLogs.SelectResults.WITH_WITHOUT_SENSOR_ID_COMBINED:
            # Combine the two dicts
            for key, values in without_sensor_id.items():

                for val in values:
                    with_sensor_id[key].append(val)

            self.compiled_result_attributes = with_sensor_id

        if analyse:
            return self.analyse_compiled_result_attributes()

        else:
            return self.compiled_result_attributes

    def analyse_compiled_result_attributes(self, comp_res=None, plot=True):
        """Analyses the compiled result attributes.

        :param comp_res: the compiled result attributes. If not specified, will use self.compiled_result_attributes
        :type comp_res: dict
        :param plot: plot bar charts
        :type plot: bool
        :return: yield value, and number of non-None values vs None values for remaining attributes
        """
        if not comp_res:
            comp_res = self.compiled_result_attributes
        if not comp_res:
            raise Exception("MTTLogs.compiled_result_attributes and the provided comp_res is None/Empty.")

        analytics = {}

        for attribute, values in comp_res.items():
            if "nbr" not in analytics:
                analytics["nbr"] = len(values)

            if attribute is "Success":
                if len(values) is 0:
                    analytics["yield"] = 0
                else:
                    analytics["yield"] = values.count("Success") / len(values)

            else:
                pass

        return analytics

    @staticmethod
    def _retrieve_result_attributes(capture, attributes):
        """Look for specific attributes in the parsed_result_logs.

        Will use the find_in_dict method, i.e. return a dict of list of values. If there are multiple attributes with
        the same name, it is possible to be more precise about which one that is looked for in the tree. By specifying
        the 'parent' of the attribute beforehand in the same string, followed by 2 hashtag symbols (##) with the looked
        for attribute. For example, if 'uniformity_level' which has the d, t and op value is to be extracted, but only
        'd' is interesting, it is possible to write "uniformity_level##d". This can be done in several levels, i.e. by
        specifying another previous parent: "Items##uniformity_level##d". This allows the user to be more exact about
        the attributes location in the tree.

        :param capture: dict containing 'files' and 'parsed_result_logs'
        :type capture: dict
        :param attributes: the attributes that are to be extracted and compiled from the parsed result logs
        :type attributes: list of str
        :return: dict of the attributes
        """
        if 'parsed_result_logs' not in capture:
            raise Exception("This capture does not have the key 'parsed_result_logs'")

        return MTTLogs.find_in_dict(capture['parsed_result_logs'], attributes)

    @staticmethod
    def _pick_capture(captures, yield_type=YieldType.FIRST_PASS):
        """Pick only one capture, eg. pick first capture or final capture.

        For the standard use-case, all captures have the same sensor_id. Will look at time-stamp to determine which
        capture was done first. Returns one capture only.

        :param captures: dict of captures, where the key is the capture_id and the value is the dict containing 'files'
         and 'parsed_result_logs'
        :type captures: dict of dicts
        :param yield_type: Which capture to pick (first or last pass)
        :type yield_type: YieldType
        :return: a capture, i.e. a dict containing capture info
        :rtype: dict
        """
        date_stamp_and_capture = []
        # List of tuples (date, capture)        types: (DateTime, dict)
        # The capture_id is added as a key to the capture dict,
        # i.e. it has 3 keys ['files', 'parsed_result_logs', 'capture_id']

        for capture in captures.values():
            stamps = MTTLogs._retrieve_result_attributes(capture, ['DateTime'])['DateTime']

            if not stamps:
                return None
            else:
                # There are several time_stamps in each result_log; use the first
                date_string = stamps[0]
                date_stamp = parse_date_stamp(date_string)

                date_stamp_and_capture.append((date_stamp, capture))

        date_stamp_and_capture = sorted(date_stamp_and_capture, key=operator.itemgetter(0))

        if yield_type == MTTLogs.YieldType.FIRST_PASS:
            return date_stamp_and_capture[0][1]
        elif yield_type == MTTLogs.YieldType.FINAL_PASS:
            return date_stamp_and_capture[-1][1]
        else:
            raise Exception("{} not supported".format(yield_type))

    @staticmethod
    def histogram(values, attribute, show=True, min_=None, max_=None, new_figure=True, range_=None, save=False):
        """Plots a histogram for an array of numerical values.

        Loops through the array and checks that all values are numerical. If not, raises Exception. Counts None values
        and

        :param values: list of values
        :type values: list of nums
        :param attribute: name of the set of values
        :type attribute: str
        :param show: if the plot is to be shown or not
        :type show: bool
        :param min_: the parameter min value
        :type min_: number
        :param max_: the parameter max value
        :type max_: number
        :param new_figure: If true, the plot is put in a new figure
        :type new_figure: bool
        :param range\_: the x-range
        :type range\_: 2-element list
        :param save: if the plot is to be saved or not
        :type save: bool
        """
        none_cnt = 0
        numeric_vals = []
        for x in values:
            if x is None:
                none_cnt += 1
            elif not isinstance(x, Number):
                raise Exception("Non-numerical value found: {}".format(x))
            else:
                numeric_vals.append(x)

        if len(numeric_vals) < 1:
            raise Exception("Number of values less than 1")

        hist, bins = histogram.create(numeric_vals)

        if none_cnt > 0:
            text = "{} values were None ({}%) and not plotted".format(none_cnt, round(none_cnt/len(values), 2))
        else:
            text = None

        if range_:
            scale = 1
        else:
            scale = 3

        fig = histogram.plot(hist, bins, data_set_name=attribute,
                             title=attribute, text=text, scale=scale, range_=range_,
                             min_=min_, max_=max_, show=True)

        if save:
            histogram.write(fig, attribute)

    def sensors_with_multiple_captures(self):
        """Returns a list of dicts of all unique_sensors that have been tested more than once

        :return: dictionary of organized logs. sensor_id is key, value is a list of dicts containing logs for each capture
        :rtype: dict of lists
        """
        multiple_captures = {}
        for sensor_id, captures in self.logs_with_sensor_id.items():
            if len(captures) > 1:
                multiple_captures[sensor_id] = captures

        return multiple_captures


if __name__ == "__main__":
    mtt_logs = MTTLogs()
    directories = ["C:\\Hugo_documents\\logs\\1267", r"C:\Hugo_documents\logs\E2 FPC1291 log"]

    mtt_logs(directories[1], log_type=MTTLogs.LogType.JSON_MQT2)

    overview = mtt_logs.general_analysis()
    print("--OVERVIEW--")
    for info_header, info in overview.items():
        print(info_header, "; ", info)

    yield_type = MTTLogs.YieldType.FIRST_PASS
    select_results = MTTLogs.SelectResults.WITH_WITHOUT_SENSOR_ID_COMBINED

    compiled = mtt_logs.compile_result_attributes(select_results=select_results, yield_type=yield_type)
    analytics = mtt_logs.analyse_compiled_result_attributes(compiled)
    print("--ANALYTICS--", "Run:", yield_type, "Results:", select_results)
    for a, b in analytics.items():
        print(a, ": ", b)
