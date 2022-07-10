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
from bs4 import BeautifulSoup
from Parsers.analyze_excel_data import analyze_excel
import sys
from Parsers.LogParser import *
from Parsers.util import typeassert


@typeassert(log_path=str, log_pattern=str, report_file=str)
class LogParserCurrent(logParser):
    def _get_data_json(self, file):
        current_result = ['Deep Sleep Current Test', 'Active Current Test']
        testData = OrderedDict()
        try:
            with open(file, encoding='utf-8', mode='r') as fh:
                content = json.load(fh)
                testData['log'] = os.path.basename(file).split('_result')[0]
                testData['host_id'], testData['sensorid'] = get_host_sensor_id(content)
                for test in content['TestReportItems']:
                    for testCase in current_result:
                        if test["Name"] == testCase:
                            self.settings_dict[testCase + "_LowerLimit"] = \
                                test['Result']['TestLog']['Steps']['measurement']['Items']['settings'][
                                    'MeasurementsRails'][0]['LowerLimitInMilliAmp']
                            self.settings_dict[testCase + "_UpperLimit"] = \
                                test['Result']['TestLog']['Steps']['measurement']['Items']['settings'][
                                    'MeasurementsRails'][0]['UpperLimitInMilliAmp']
                            testData[testCase + "_Result"] = check_test_method_conclusion(test)
                            testData[testCase + "_LowerLimit"] = self.settings_dict[testCase + "_LowerLimit"]
                            if 'CurrentMeasurementResults' in \
                                    test['Result']['TestLog']['Steps']['measurement']['Items']['results']:
                                testData[testCase + "_Value"] = \
                                    test['Result']['TestLog']['Steps']['measurement']['Items']['results'][
                                        'CurrentMeasurementResults'][0]['CurrentValueInMilliAmp']
                            else:
                                testData[testCase + "_Value"] = \
                                    test['Result']['TestLog']['Steps']['measurement']['Items']['results'][
                                        'CurrentValueInMilliAmp']
                            testData[testCase + "_UpperLimit"] = self.settings_dict[testCase + "_UpperLimit"]

        except KeyError as e:
            logging.error('KeyError {} happens in {} {}, might be no test result, regard all nan'.format(e,
                                                                                                         self.__class__.__name__,
                                                                                                         file))
        except Exception as e:
            print("{}::{} Exception:".format(self.__class__.__name__, sys._getframe().f_code.co_name))
            print(e)

        return testData

    def _get_data_html(self, file):
        current_patterns = OrderedDict()
        current_patterns['Deep Sleep Current Test'] = r'Current at 3.3V = (.*)uA'
        current_patterns['Active Current Test'] = r'Current at 3.3V = (.*)mA'
        test_dict = OrderedDict()
        with open(file, encoding='utf-8', mode='r') as f:
            test_dict['log'] = os.path.basename(file).split('.')[0]
            try:
                soup = BeautifulSoup(f, 'lxml')
                text = soup.text
                test_dict['Session'], test_dict['sensorid'] = get_host_sensor_id(text)
                for testCase, value in current_patterns.items():
                    res = re.findall(value, text)
                    if len(res) > 0:
                        test_dict[testCase + "_Value"] = float(res[0].strip().split(' ')[0])
                        self.settings_dict[testCase + "_LowerLimit"] = float(res[0].strip().split(' ')[4])
                        self.settings_dict[testCase + "_UpperLimit"] = float(res[0].strip().split(' ')[6])

            except Exception as e:
                logging.error('Error {} happens in {} {}, might be no test result, regard all nan'.
                              format(e, self.__class__.__name__, file))
            finally:
                return test_dict

    def show_hist(self):
        if not os.path.exists(self.report_file):
            return
        my_config = config()
        current_result = ['Deep Sleep Current Test', 'Active Current Test']
        for item in current_result:
            result = analyze_excel(self.report_file).get_valid_data_by_key(item + "_Value")
            lower_limit = round(self.settings_dict[item + "_LowerLimit"]) - 3
            upper_limit = round(self.settings_dict[item + "_UpperLimit"]) + 3
            if item == 'Deep Sleep Current Test':
                unit = "[unit: uA]"
            else:
                unit = "[unit: mA]"
            for i in range(0, len(result)):
                if result[i] < lower_limit:
                    result[i] = lower_limit
                elif result[i] > upper_limit:
                    result[i] = upper_limit - 1

            frequencies = []
            for value in range(lower_limit, upper_limit):
                frequency = result.count(value)
                frequencies.append(frequency)

            hist = pygal.Bar(my_config)
            hist.add("{}".format(item), frequencies)
            hist.title = "{}_distribution, limit is ({}, {})".format(item,
                                                                     self.settings_dict[item + "_LowerLimit"],
                                                                     self.settings_dict[item + "_UpperLimit"])
            hist.x_title = "{}_Value {}".format(item, unit)
            hist.y_title = "number of current value"
            hist.x_labels = range(lower_limit, upper_limit)
            try:
                hist.render_to_file(os.path.splitext(self.report_file)[0] + "_{}".format(item) + ".svg")
            except Exception as e:
                print("{}::{} Exception:".format(self.__class__.__name__, sys._getframe().f_code.co_name))
                print(e)
