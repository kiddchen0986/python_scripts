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
from Parsers.json_settings import parse_json_settings
import sys
from Parsers.LogParser import *


@typeassert(log_path=str, log_pattern=str, report_file=str)
class logParserCtlImageDrive(logParser):
    # item = name, value key, low limit key, upp limit key
    data_columns = [
        ['PixelErrors', 'PixelErrorsLimit', 'PixelErrorsLimit'],
        ['SubAreaErrors', '', ''],
        ['GlobalPixelErrors', '', ''],
        ['MedianRow_1', 'MedianRow1Min', 'MedianRow1Max'],
        ['MedianRow_2', 'MedianRow2Min', 'MedianRow2Max'],
        ['MedianRowMiddle', 'MedianRowMiddleMin', 'MedianRowMiddleMax',],
        ['MedianRowNextToLast', 'MedianRowNextToLastMin', 'MedianRowNextToLastMax'],
        ['MedianRowLast', 'MedianRowNextToLastMin', 'MedianRowNextToLastMax'],
        ['MedianRow_1_Inv', 'MedianRow1InvMin', 'MedianRow1InvMax'],
        ['MedianRowLastInv', 'MedianRowLastInvMin', 'MedianRowLastInvMax'],
        ['MedianRow_1_DevMax', '', ''],
        ['MedianRow_2_DevMax', '', ''],
        ['MedianRowMiddleDevMax', '', ''],
        ['MedianRowNextToLastDevMax', '', ''],
        ['MedianRowLastDevMax', '', ''],
        ['MedianRow_1_InvDevMax', '', ''],
        ['MedianRowLastInvDevMax', '', ''],
    ]

    def _get_data_json(self, file):
        with open(file, encoding='utf-8', mode='r') as f:

            test_dict = OrderedDict({'log': os.path.basename(file).split('_result.')[0]})
            try:
                json_dict = json.load(f)

                test_dict['host_id'], test_dict['sensorid'] = get_host_sensor_id(json_dict)

                for report in json_dict['TestReportItems']:
                    if report['Result']['TestName'] == 'TestCtlDefectivePixels':
                        if 'ImageDriveAnalysisSettings' in report['Result']['TestLog']['Steps']['measurement']['Items'][
                            'settings']['Analysis'] and report['Result']['TestLog']['Steps']['measurement']['Items'][
                            'settings']['Analysis']['ImageDriveAnalysisSettings']['Enabled']:

                            test_dict['defective_pixels_result'] = check_test_method_conclusion(report)
                            result_key = ''
                            if 'ImageDriveResult' in parse_json_settings(report)['analysis_result']:
                                result_key = 'ImageDriveResult'
                            elif 'ImageDriveAnalysisResult' in parse_json_settings(report)['analysis_result']:
                                result_key = 'ImageDriveAnalysisResult'
                                if result_key != '':
                                    for item in self.data_columns:
                                        if item[1] != '' and item[1] != item[2]:
                                            test_dict[item[0] + '_low'] = report['Result']['TestLog']['Steps']['measurement'
                                            ]['Items']['settings']['Analysis']['ImageDriveAnalysisSettings'][item[1]]
                                        test_dict[item[0]] = parse_json_settings(report)['analysis_result'][
                                            result_key][item[0]]
                                        if item[2] != '' and item[1] != item[2]:
                                            test_dict[item[0] + '_upp'] = \
                                            report['Result']['TestLog']['Steps']['measurement'
                                            ]['Items']['settings']['Analysis']['ImageDriveAnalysisSettings'][item[2]]
                                        elif item[2] != '' and item[1] == item[2]:
                                            test_dict[item[0] + '_upp'] = \
                                                report['Result']['TestLog']['Steps']['measurement'
                                                ]['Items']['settings']['Analysis']['ImageDriveAnalysisSettings'][
                                                    item[2]]

                        return test_dict

            except KeyError as e:
                logging.error('KeyError {} happens in {} {}, might be no test result, regard all nan'.format(e, self.__class__.__name__, file))
            except Exception as error:
                logging.error('UnknowError {} happens in {} {},'.format(error, self.__class__.__name__, file))
            finally:
                return test_dict

    def _get_data_html(self, file):

        ctl_defective_patterns = OrderedDict()
        ctl_defective_patterns['image_drive_result'] = r'Image drive test (.*)'
        ctl_defective_patterns['image_drive_median_row_1'] = r'Median Row 1: (.*) \(Limit: > (.*) and < (.*)\)'
        ctl_defective_patterns['image_drive_median_row_2'] = r'Median Row 2: (.*) \(Limit: > (.*) and < (.*)\)'
        ctl_defective_patterns[
            'image_drive_median_row_middle'] = r'Median Row Middle: (.*) \(Limit: > (.*) and < (.*)\)'
        ctl_defective_patterns[
            'image_drive_median_row_next_last'] = r'Median Row Next To Last: (.*) \(Limit: > (.*) and < (.*)\)'
        ctl_defective_patterns['image_drive_median_row_last'] = r'Median Row Last: (.*) \(Limit: > (.*) and < (.*)\)'
        ctl_defective_patterns[
            'image_drive_median_row_last_inv'] = r'Median Row Last Inv: (.*) \(Limit: > (.*) and < (.*)\)'
        ctl_defective_patterns['image_drive_median_row_1_inv'] = r'Median Row 1 Inv: (.*) \(Limit: > (.*) and < (.*)\)'
        ctl_defective_patterns['image_drive_number_pixel_errors'] = r'Number of pixel errors: (.*) \(Limit: < (.*)\)'

        test_dict = OrderedDict()
        with open(file, encoding='utf-8', mode='r') as f:

            test_dict['log'] = os.path.basename(file).split('.')[0]
            test_dict['host_id'] = 'N/A'
            try:
                soup = BeautifulSoup(f, 'lxml')
                text = soup.text
                for key, value in ctl_defective_patterns.items():
                    res = re.findall(value, text)
                    if res:
                        if key == 'image_drive_result':
                            test_dict[key] = 1 if res[0] == 'passed' else 0
                        else:
                            test_dict[key] = int(res[0][0])

            except Exception as e:
                logging.error(file, sys.exc_info())
            finally:
                return test_dict
