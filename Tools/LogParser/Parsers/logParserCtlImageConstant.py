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
import sys
from bs4 import BeautifulSoup
from Parsers.analyze_excel_data import analyze_excel
from Parsers.LogParser import *
from Parsers.json_settings import parse_json_settings


@typeassert(log_path=str, log_pattern=str, report_file=str)
class logParserCtlImageConstant(logParser):

    def _get_data_txt(self, file):
        log_data_list = OrderedDict()
        log_data_list['log'] = os.path.basename(file).split('_log.')[0]
        with open(file, encoding='utf-8', mode='r') as f:
            text = f.read()

            log_data_list['image_constant_result'] = 1 if 'Image constant test passed' in text else 0

            if 'Image constant result...' in text:
                ic_medians = re.findall(r'  Image constant medians: (.*)', text)
                medians = ic_medians[0].split(',')
                for i, v in enumerate(medians):
                    log_data_list['median_' + str(i)] = int(v)

            return log_data_list

    def _get_data_html(self, file):
        ctl_defective_patterns = OrderedDict()
        ctl_defective_patterns['image_constant_result'] = r'Image constant test (.*)'
        ctl_defective_patterns['image_constant_medians'] = r'Image constant medians: (.*)'
        # ctl_defective_patterns['image_constant_medians'] = r'Image constant medians: (.*) \(Limit:'

        test_dict = OrderedDict()
        with open(file, encoding='utf-8', mode='r') as f:

            test_dict['log'] = os.path.basename(file).split('.')[0]
            try:
                soup = BeautifulSoup(f, 'lxml')
                text = soup.text
                for key, value in ctl_defective_patterns.items():
                    res = re.findall(value, text)
                    if res:
                        if key == 'image_constant_result':
                            test_dict[key] = 1 if res[0] == 'passed' else 0
                        else:
                            for i, val in enumerate(res[0].split(',')):
                                test_dict['median_' + str(i)] = int(val)

            except Exception as e:
                logging.error(file, sys.exc_info())
            finally:
                return test_dict

    def _get_data_json(self, file):
        with open(file, encoding='utf-8', mode='r') as f:
            test_dict = OrderedDict()
            test_dict['log'] = os.path.basename(file).split('_result.')[0]
            try:
                json_dict = json.load(f)

                test_dict['host_id'], test_dict['sensorid'] = get_host_sensor_id(json_dict)

                for report in json_dict['TestReportItems']:
                    if report['Result']['TestName'] == 'TestCtlDefectivePixels':
                        if 'ImageConstantAnalysisSettings' in \
                                report['Result']['TestLog']['Steps']['measurement']['Items']['settings']['Analysis']:
                            self.settings_dict['MinMedian'] = report['Result']['TestLog']['Steps']['measurement'][
                                'Items']['settings']['Analysis']['ImageConstantAnalysisSettings']['MinMedian']
                            self.settings_dict['MaxMedian'] = report['Result']['TestLog']['Steps']['measurement'][
                                'Items']['settings']['Analysis']['ImageConstantAnalysisSettings']['MaxMedian']
                            self.settings_dict['MaxPixelErrors'] = report['Result']['TestLog']['Steps']['measurement'][
                                'Items']['settings']['Analysis']['ImageConstantAnalysisSettings']['MaxPixelErrors']

                        if 'ImageConstantAnalysisResult' in parse_json_settings(report)['analysis_result']:
                            medians = parse_json_settings(report)['analysis_result']['ImageConstantAnalysisResult'][
                                'ImageConstantMedians']
                            test_dict['MinMedian'] = self.settings_dict['MinMedian']

                            for i, val in enumerate(medians):
                                test_dict['median_' + str(i)] = val
                            test_dict['MaxMedian'] = self.settings_dict['MaxMedian']
                            test_dict['PixelErrors'] = \
                            parse_json_settings(report)['analysis_result']['ImageConstantAnalysisResult'][
                                'PixelErrors']
                            test_dict['PixelErrors_upp'] = self.settings_dict['MaxPixelErrors']
                            self.settings_dict['len_median'] = len(medians)

                        break

            except KeyError as e:
                    logging.error('KeyError {} happens in {} {}, might be no test result, regard all nan'.format(e, self.__class__.__name__, file))
            finally:
                return test_dict

    def show_hist(self):
        if not os.path.exists(self.report_file):
            return
        my_config = config()
        hist = pygal.Bar(my_config)
        results = {}

        for i in range(0, self.settings_dict['len_median']):
            key_median = 'median_{}'.format(i)
            results[i] = analyze_excel(self.report_file).get_valid_data_by_key(key_median)

            frequencies = []
            minMedian = self.settings_dict['MinMedian']
            maxMedian = self.settings_dict['MaxMedian']

            for j in range(0, len(results[i])):
                if results[i][j] > maxMedian:
                    results[i][j] = maxMedian

            for value in range(minMedian, maxMedian + 1):
                frequency = results[i].count(value)
                frequencies.append(frequency)

            hist.add("median_{}".format(i), frequencies)

        hist.title = "image constant value distribution, limit is ({}, {})".format(minMedian, maxMedian)
        hist.x_title = "image constant value"
        hist.y_title = "number of constant value"
        hist.x_labels = range(minMedian, maxMedian + 1)
        hist.render_to_file(os.path.splitext(self.report_file)[0] + '.svg')

        # get pixel error distribution
        pixel_error = analyze_excel(self.report_file).get_valid_data_by_key('PixelErrors')

        pixel_error_frequencies = []
        for j in range(0, len(pixel_error)):
            if pixel_error[j] > 7:
                pixel_error[j] = 7

        for value in range(0, max(pixel_error) + 1):
            frequency = pixel_error.count(value)
            pixel_error_frequencies.append(frequency)

        hist_pixel_error = pygal.Bar(my_config)
        hist_pixel_error.title = "pixel errors value distribution, limit < {}".format(
            self.settings_dict["MaxPixelErrors"])
        hist_pixel_error.x_title = "pixel error value"
        hist_pixel_error.y_title = "number of pixel error"
        hist_pixel_error.x_labels = range(0, max(pixel_error) + 1)
        hist_pixel_error.add("PixelErrors", pixel_error_frequencies)
        try:
            hist_pixel_error.render_to_file(os.path.splitext(self.report_file)[0] + 'pixel_error.svg')
        except Exception as e:
            print("{}::{} Exception:".format(self.__class__.__name__, sys._getframe().f_code.co_name))
            print(e)
