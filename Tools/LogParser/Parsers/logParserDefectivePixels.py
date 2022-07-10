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
from Parsers.json_settings import parse_json_settings
import sys
from Parsers.LogParser import *


@typeassert(log_path=str, log_pattern=str, report_file=str)
class logParserDefectivePixels(logParser):
    # item format: [name, result key, low limit key，, upp limit key]
    data_columns = [
        ['cb_type1_min_histogram_median', 'type1_min_histogram_median', 'CbType1MedianMin', ''],
        ['cb_type1_max_histogram_median', 'type1_max_histogram_median', '', 'CbType1MedianMax'],
        ['cb_type1_deviation_max', 'type1_deviation_max', '', ''],
        ['cb_type2_min_histogram_median', 'type2_min_histogram_median', 'CbType2MedianMin', ''],
        ['cb_type2_max_histogram_median', 'type2_max_histogram_median', '', 'CbType2MedianMax'],
        ['cb_type2_deviation_max', 'type2_deviation_max',  '', ''],
        ['cb_pixel_errors', 'pixel_errors', '', 'MaxPixelErrors'],
        ['icb_type1_min_histogram_median', 'type1_min_histogram_median', 'IcbType1MedianMin', ''],
        ['icb_type1_max_histogram_median', 'type1_max_histogram_median', '', 'IcbType1MedianMax'],
        ['icb_type1_deviation_max', 'type1_deviation_max', '', ''],
        ['icb_type2_min_histogram_median', 'type2_min_histogram_median',  'IcbType2MedianMin', ''],
        ['icb_type2_max_histogram_median', 'type2_max_histogram_median', '', 'IcbType2MedianMax'],
        ['icb_type2_deviation_max', 'type2_deviation_max', '', ''],
        ['icb_pixel_errors', 'pixel_errors', '', 'MaxPixelErrors'],

        ['swing_cb_type1_min_histogram_median', 'type1_min_histogram_median', 'CbType1MedianMin', ''],
        ['swing_cb_type1_max_histogram_median', 'type1_max_histogram_median', '', 'CbType1MedianMax'],
        ['swing_cb_type1_deviation_max', 'type1_deviation_max', '', ''],
        ['swing_cb_type2_min_histogram_median', 'type2_min_histogram_median', 'CbType2MedianMin', ''],
        ['swing_cb_type2_max_histogram_median', 'type2_max_histogram_median', '', 'CbType2MedianMax'],
        ['swing_cb_type2_deviation_max', 'type2_deviation_max', '', ''],
        ['swing_cb_pixel_errors', 'pixel_errors', '', ''],

        ['swing_icb_type1_min_histogram_median', 'type1_min_histogram_median', 'IcbType1MedianMin', ''],
        ['swing_icb_type1_max_histogram_median', 'type1_deviation_max', '', 'IcbType1MedianMax'],
        ['swing_icb_type1_deviation_max', 'type1_deviation_max', '', ''],
        ['swing_icb_type2_min_histogram_median', 'type2_min_histogram_median', 'IcbType2MedianMin', ''],
        ['swing_icb_type2_max_histogram_median', 'type2_max_histogram_median', '', 'IcbType2MedianMax'],
        ['swing_icb_type2_deviation_max', 'type2_deviation_max', '', ''],
        ['swing_icb_pixel_errors', 'pixel_errors', '', 'MaxPixelErrors'],
    ]

    settings = {'cb_type1_min_histogram_median': 'CbType1MedianMin',
                'cb_type1_max_histogram_median': 'CbType1MedianMax',
                'cb_type2_min_histogram_median': 'CbType2MedianMin',
                'cb_type2_max_histogram_median': 'CbType2MedianMax',
                'cb_pixel_errors': 'MaxPixelErrors',
                'icb_type1_min_histogram_median': 'IcbType1MedianMin',
                'icb_type1_max_histogram_median': 'IcbType1MedianMax',
                'icb_type2_min_histogram_median': 'IcbType2MedianMin',
                'icb_type2_max_histogram_median': 'IcbType2MedianMax',
                'icb_pixel_errors': 'MaxPixelErrors'}

    def _get_data_json(self, file):
        with open(file, encoding='utf-8', mode='r') as f:
            test_dict = OrderedDict()
            test_dict['log'] = os.path.basename(file).split('_result.')[0]
            try:
                json_dict = json.load(f)
                test_dict['host_id'], test_dict['sensorid'] = get_host_sensor_id(json_dict)
                for report in json_dict['TestReportItems']:
                    if report['Result']['TestName'] == 'TestCtlDefectivePixels':
                        test_dict['defective_pixels_result'] = check_test_method_conclusion(report)
                        if 'DeadPixelsAnalysisSettings' in \
                                report['Result']['TestLog']['Steps']['measurement']['Items']['settings']['Analysis'
                                ]['DeadPixelsAnalysisSettings'] \
                                and report['Result']['TestLog']['Steps']['measurement']['Items'][
                            'settings']['Analysis']['DeadPixelsAnalysisSettings']['Enabled']:
                            for key, value in self.settings.items():
                                self.settings_dict[key] = \
                                    report['Result']['TestLog']['Steps']['measurement']['Items']['settings'][
                                        'Analysis']['DeadPixelsAnalysisSettings'][value]
                        if 'DefPixelsAnalysisDeadPixelsResult' in \
                                parse_json_settings(report)['analysis_result'] and \
                                report['Result']['TestLog']['Steps']['measurement']['Items']['settings'][
                                    'Analysis']['DeadPixelsAnalysisSettings']['Enabled']:
                            for item in self.data_columns:
                                if item[2] != '' and (item[0].startswith('cb') or item[0].startswith('icb')):
                                    test_dict[item[0] + '_low'] = report['Result']['TestLog']['Steps'][
                                        'measurement']['Items']['settings']['Analysis'][
                                        'DeadPixelsAnalysisSettings'][item[2]]
                                if item[0].startswith('cb'):
                                    test_dict[item[0]] = parse_json_settings(report)['analysis_result'][
                                        'DefPixelsAnalysisDeadPixelsResult']['CheckerboardResult'][item[1]]
                                elif item[0].startswith('icb'):
                                    test_dict[item[0]] = \
                                        parse_json_settings(report)['analysis_result'][
                                            'DefPixelsAnalysisDeadPixelsResult']['InvertedCheckerboardResult'][item[1]]
                                if item[3] != '' and (item[0].startswith('cb') or item[0].startswith('icb')):
                                    test_dict[item[0] + '_upp'] = report['Result']['TestLog']['Steps'][
                                        'measurement']['Items']['settings']['Analysis'][
                                        'DeadPixelsAnalysisSettings'][item[3]]

                        if 'SwingingDefPixelsAnalysisDeadPixelsResult' in \
                                parse_json_settings(report)['analysis_result'] and \
                                report['Result']['TestLog']['Steps']['measurement']['Items']['settings'][
                                    'Analysis']['SwingingPixelsAnalysisSettings']['Enabled']:
                            for item in self.data_columns:
                                if item[2] != '' and (item[0].startswith('swing_cb') or item[0].startswith('swing_icb')):
                                    test_dict[item[0] + '_low'] = report['Result']['TestLog']['Steps'][
                                        'measurement']['Items']['settings']['Analysis'][
                                        'SwingingPixelsAnalysisSettings'][item[2]]
                                if item[0].startswith('swing_cb'):
                                    test_dict[item[0]] = \
                                        parse_json_settings(report)['analysis_result'][
                                            'SwingingDefPixelsAnalysisDeadPixelsResult']['CheckerboardResult'][item[1]]
                                elif item[0].startswith('swing_icb'):
                                    test_dict[item[0]] = \
                                        parse_json_settings(report)['analysis_result'][
                                            'SwingingDefPixelsAnalysisDeadPixelsResult']['InvertedCheckerboardResult'][
                                            item[1]]
                                if item[3] != '' and (item[0].startswith('swing_cb') or item[0].startswith('swing_icb')):
                                    test_dict[item[0] + '_upp'] = report['Result']['TestLog']['Steps'][
                                        'measurement']['Items']['settings']['Analysis'][
                                        'SwingingPixelsAnalysisSettings'][item[3]]
                        break
                    elif report['Result']['TestName'] == 'TestCtlDeadPixels':
                        test_dict['dead_pixels_result'] = check_test_method_conclusion(report)
                        for key, value in self.settings.items():
                            self.settings_dict[key] = \
                                report['Result']['TestLog']['Steps']['measurement'][
                                'Items']['settings']['Analysis'][value]
                        for item in self.data_columns:
                            if item[0].startswith('cb'):
                                test_dict[item[0]] = parse_json_settings(report)\
                                    ['analysis_result']['CheckerboardResult'][item[1]]
                            elif item[0].startswith('icb'):
                                test_dict[item[0]] = parse_json_settings(report)\
                                    ['analysis_result']['InvertedCheckerboardResult'][item[1]]

                    elif report['Result']['TestName'] == 'TestDeadPixelsProdTestLibGradient':
                        test_dict['dead_pixels_result'] = check_test_method_conclusion(report)
                        for i in self.data_columns[:10]:
                            test_dict[i[0]] = report['Result']['TestLog']['Steps']['analysis']['Items'][i[0]]

                        break

                return test_dict

            except KeyError as e:
                logging.error('KeyError {} happens in {} {}, might be no test result, regard all nan'.format(e, self.__class__.__name__, file))
            except Exception as error:
                logging.error('UnknowError {} happens in {} {},'.format(error, self.__class__.__name__, file))
            finally:
                return test_dict

    def _get_data_html(self, file):
        ctl_defective_patterns = OrderedDict()
        ctl_defective_patterns['sensorid'] = r'Sensor ID: (.*)'
        ctl_defective_patterns['defective_pixels_result'] = r'Test Ctl Defective Pixels: (.*)'
        ctl_defective_patterns['type1_median'] = r'Type1 median, min (.*) max (.*) \(Limit: > (.*) and < (.*)\)'
        ctl_defective_patterns['type2_median'] = r'Type2 median, min (.*) max (.*) \(Limit: > (.*) and < (.*)\)'
        ctl_defective_patterns['number_dead_pixels'] = r'Number of dead pixels: (.*) \(Limit: < (.*)\)'

        with open(file, encoding='utf-8', mode='r') as f:
            test_dict = OrderedDict()
            test_dict['log'] = os.path.basename(file).split('.')[0]
            test_dict['host_id'] = 'N/A'
            try:
                soup = BeautifulSoup(f, 'lxml')
                text = soup.text
                for key, value in ctl_defective_patterns.items():
                    res = re.findall(value, text)
                    if res:
                        if key == 'defective_pixels_result':
                            test_dict[key] = 1 if res[0] == 'Pass' else 0
                        elif key == 'sensorid':
                            test_dict['sensorid'] = res[0]
                        elif key == 'type1_median':
                            test_dict['cb_type1_min_histogram_median'] = int(res[0][0])
                            test_dict['cb_type1_max_histogram_median'] = int(res[0][1])
                            test_dict['icb_type1_min_histogram_median'] = int(res[1][0])
                            test_dict['icb_type1_max_histogram_median'] = int(res[1][1])
                            test_dict['swing_cb_type1_min_histogram_median'] = int(res[2][0])
                            test_dict['swing_cb_type1_max_histogram_median'] = int(res[2][1])
                            test_dict['swing_icb_type1_min_histogram_median'] = int(res[3][0])
                            test_dict['swing_icb_type1_max_histogram_median'] = int(res[3][1])
                        elif key == 'type2_median':
                            test_dict['cb_type2_min_histogram_median'] = int(res[0][0])
                            test_dict['cb_type2_max_histogram_median'] = int(res[0][1])
                            test_dict['icb_type2_min_histogram_median'] = int(res[1][0])
                            test_dict['icb_type2_max_histogram_median'] = int(res[1][1])
                            test_dict['swing_cb_type2_min_histogram_median'] = int(res[2][0])
                            test_dict['swing_cb_type2_max_histogram_median'] = int(res[2][1])
                            test_dict['swing_icb_type2_min_histogram_median'] = int(res[3][0])
                            test_dict['swing_icb_type2_max_histogram_median'] = int(res[3][1])
                        elif key == 'number_dead_pixels':
                            test_dict['cb_pixel_errors'] = int(res[0][0])
                            test_dict['icb_pixel_errors'] = int(res[1][0])
                            test_dict['swing_cb_pixel_errors'] = int(res[2][0])
                            test_dict['swing_icb_pixel_errors'] = int(res[3][0])

            except Exception as e:
                logging.error(file, sys.exc_info())
            finally:
                return test_dict

    def show_hist(self):
        my_config = config()
        hist1 = pygal.Bar(my_config)
        hist2 = pygal.Bar(my_config)
        hist3 = pygal.Bar(my_config)

        result = {}
        cb_median_range = []
        icb_median_range = []
        pixelerrors_range = []

        cb_key_settings = {}
        icb_key_settings = {}
        error_key_settings = {}
        value_range = []
        for key, value in self.settings_dict.items():
            value_range.append(value)
            if key.find("type1") >= 0:
                cb_median_range.append(analyze_excel(self.report_file).get_defective_pixels_column()[key])
                cb_key_settings[analyze_excel(self.report_file).get_defective_pixels_column()[key]] = key
            if key.find("type2") >= 0:
                icb_median_range.append(analyze_excel(self.report_file).get_defective_pixels_column()[key])
                icb_key_settings[analyze_excel(self.report_file).get_defective_pixels_column()[key]] = key
            if key.find("errors") >= 0:
                pixelerrors_range.append(analyze_excel(self.report_file).get_defective_pixels_column()[key])
                error_key_settings[analyze_excel(self.report_file).get_defective_pixels_column()[key]] = key

        for i in cb_median_range:
            result[i] = analyze_excel(self.report_file).get_valid_data(i)

            frequencies = []
            for value in range(value_range[0] - 3, value_range[1] + 3):
                frequency = result[i].count(value)
                frequencies.append(frequency)

            hist1.add('{type}'.format(type=cb_key_settings[i]), frequencies)

        for i in icb_median_range:
            result[i] = analyze_excel(self.report_file).get_valid_data(i)

            frequencies = []
            for value in range(value_range[2] - 3, value_range[3] + 3):
                frequency = result[i].count(value)
                frequencies.append(frequency)

            hist2.add('{type}'.format(type=icb_key_settings[i]), frequencies)

        for i in pixelerrors_range:
            result[i] = analyze_excel(self.report_file).get_valid_data(i)

            frequencies = []
            for value in range(0, value_range[4] + 3):
                frequency = result[i].count(value)
                frequencies.append(frequency)

            hist3.add('{type}'.format(type=error_key_settings[i]), frequencies)

        hist1.title = "Type1 defective pixels distribution, limit is ({}, {})".format(value_range[0], value_range[1])
        hist1.x_title = "pixels value"
        hist1.y_title = "number of pixels"
        hist1.x_labels = range(value_range[0] - 3, value_range[1] + 3)
        hist1.render_to_file(os.path.splitext(self.report_file)[0] + "_type1.svg")

        hist2.title = "Type2 defective pixels distribution, limit is ({}, {})".format(value_range[2], value_range[3])
        hist2.x_title = "pixels value"
        hist2.y_title = "number of pixels"
        hist2.x_labels = range(value_range[2] - 3, value_range[3] + 3)
        hist2.render_to_file(os.path.splitext(self.report_file)[0]+ "_type2.svg")

        hist3.title = "defective pixels error, limit < {}".format(value_range[4])
        hist3.x_title = "pixels errors"
        hist3.y_title = "number of errors"
        hist3.x_labels = range(0, value_range[4] + 3)
        try:
            hist3.render_to_file(os.path.splitext(self.report_file)[0] + "_errors.svg")
        except Exception as e:
            print("{}::{} Exception:".format(self.__class__.__name__, sys._getframe().f_code.co_name))
            print(e)
