# -*- coding: utf-8 -*-
#
# Copyright (c) 2021-2022 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#

import json
from bs4 import BeautifulSoup
import shutil
from Parsers.analyze_excel_data import analyze_excel
from Parsers.json_settings import parse_json_settings
import sys
from Parsers.LogParser import *
import math


@typeassert(log_path=str, log_pattern=str, report_file=str)
class logParserMqt(logParser):
    def __init__(self, log_path: str, log_pattern='*.json', report_file: str = ''):
        super(logParserMqt, self).__init__(log_path, log_pattern, report_file)
        self.max_mqt_count = 0

    def _get_key_suffix(self, index):
        if index == 0:
            return ''
        return '_%d' % (index + 1)

    def _get_data_json(self, file):
        with open(file, encoding='utf-8', mode='r') as f:
            test_data = OrderedDict()
            test_data['log'] = os.path.basename(file).split('_result.')[0]

            str_otp = None
            try:
                json_dict = json.load(f)
                test_data['host_id'], test_data['sensorid'] = get_host_sensor_id(json_dict)
                for item in json_dict['TestReportItems']:
                    if item['Result']['TestName'] == 'TestReadOtp':
                        if "OtpMemoryMainData" in item['Result']['TestLog']['Steps']['measurement']['Items']:
                            str_otp = item['Result']['TestLog']['Steps']['measurement']['Items'][
                                'OtpMemoryMainData']
                        else:
                            str_otp = item['Result']['TestLog']['Steps']['measurement']['Items'][
                                'OtpMemoryData']
                        break
                if str_otp is not None:
                    str_otp_split = str_otp.split(' ')
                    otp_info = []
                    for val in str_otp_split:
                        otp_info.append(int(val, 16))
                    if len(otp_info) > 12:
                        test_data['LOT ID'], test_data['X Coordinate'], test_data['Y Coordinate'], test_data[
                            'Wafer ID'] = self.get_wafer_info(otp_info)

            except Exception as e:
                logging.warning(
                    'LOT ID or X Coordinate or Y Coordinate or Wafer ID not correct')

            try:
                # parse TestModuleQuality2
                mqt_cycles = [item for item in json_dict['TestReportItems'] if
                              item['Result']['TestName'] == 'TestModuleQuality2']
                if len(mqt_cycles) > self.max_mqt_count:
                    self.max_mqt_count = len(mqt_cycles)
                for index, item in enumerate(mqt_cycles):
                    suffix = self._get_key_suffix(index)
                    test_data['mqt2_result' + suffix] = check_test_method_conclusion(item)
                    if item['Result']['TestLog']['Steps']['measurement']['Items']['settings']['Analysis']['Snr'][
                        'IsEnabled']:
                        self.settings_dict['snr'] = \
                            item['Result']['TestLog']['Steps']['measurement']['Items']['settings']['Analysis'][
                                'Snr']['SnrLimitDb']
                        test_data['SnrLimitDb' + suffix] = self.settings_dict['snr']
                        test_data['snr' + suffix] = parse_json_settings(item)['analysis_result']['Snr']['SnrDb']
                        if float(test_data['snr' + suffix]) == -1000:
                            test_data['snr' + suffix] = -1
                        if 'SaturationFraction' in parse_json_settings(item)['analysis_result']['Snr']:
                            test_data['SaturationFraction' + suffix] = \
                            parse_json_settings(item)['analysis_result']['Snr'][
                                'SaturationFraction']
                    if item['Result']['TestLog']['Steps']['measurement']['Items']['settings']['Analysis']['Blob'][
                        'IsEnabled']:
                        test_data['blob' + suffix] = \
                            parse_json_settings(item)['analysis_result']['Blob']['BlobCount']
                        self.settings_dict['blob'] = \
                            item['Result']['TestLog']['Steps']['measurement']['Items']['settings']['Analysis'][
                                'Blob']['BlobLimit']
                        test_data['BlobLimit' + suffix] = self.settings_dict['blob']

                    if item['Result']['TestLog']['Steps']['measurement']['Items']['settings']['Analysis'][
                        'Uniformity']['IsEnabled']:
                        self.settings_dict['udr'] = \
                            item['Result']['TestLog']['Steps']['measurement']['Items']['settings']['Analysis'][
                                'Uniformity']['UdrLimit']
                        test_data['UdrLimit' + suffix] = self.settings_dict['udr']
                        test_data['udr' + suffix] = \
                            parse_json_settings(item)['analysis_result']['Uniformity']['Udr']

                    if 'FixedPattern' in parse_json_settings(item)['analysis_result'] and \
                            item['Result']['TestLog']['Steps']['measurement']['Items']['settings']['Analysis'][
                                'FixedPattern']['IsEnabled']:
                        test_data['FixedPatternPixels' + suffix] = \
                            parse_json_settings(item)['analysis_result']['FixedPattern']['FixedPatternPixels']
                        self.settings_dict['FixedPattern'] = \
                            item['Result']['TestLog']['Steps']['measurement']['Items']['settings']['Analysis'][
                                'FixedPattern']['FixedPatternLimit']

                    if hasattr(self, 'fmi_folder') and hasattr(self, 'limits') and 'ZebraImages' in \
                            item['Result']['TestLog']['Steps']['measurement']['Items']['result']:
                        fmi_file = os.path.join(os.path.dirname(file), item['Result']['TestLog']['Steps'][
                            'measurement']['Items']['result']['ZebraImages'])
                        self.move_fmi(float(test_data['snr' + suffix]), [file, fmi_file])

                # parse TestModuleQuality
                mqt_cycles = [item for item in json_dict['TestReportItems'] if
                              item['Result']['TestName'] == 'TestModuleQuality']
                for index, item in enumerate(mqt_cycles):
                    test_data['mqt_result'] = check_test_method_conclusion(item)
                    test_data['snr'] = item['Result']['TestLog']['Steps']['analysis']['Items']['snr_db']
                    if float(test_data['snr']) == -1000:
                        test_data['snr'] = -1

                    if 'SnrLimit' in item['Result']['TestLog']['Steps']['measurement']['Items']['settings']:
                        self.settings_dict['snr'] = \
                            item['Result']['TestLog']['Steps']['measurement']['Items']['settings'][
                                'SnrLimit']

                    if hasattr(self, 'fmi_folder') and hasattr(self, 'limits') and 'ZebraImages' in \
                            item['Result']['TestLog']['Steps']['measurement']['Items']['results']:
                        fmi_file = os.path.join(os.path.dirname(file), item['Result']['TestLog']['Steps'
                        ]['measurement']['Items']['results']['ZebraImages'])
                        self.move_fmi(float(test_data['snr']), [file, fmi_file])

            except KeyError as e:
                logging.error('KeyError {} happens in {} {}, might be no test result, regard all nan'.format(e,
                                                                                                             self.__class__.__name__,
                                                                                                             file))
            except Exception as e:
                print("{}::{} Exception:".format(self.__class__.__name__, sys._getframe().f_code.co_name))
                print(e)

            finally:
                return test_data

    def _get_data_json_primax(self, file):
        with open(file, encoding='utf-8', mode='r') as f:
            test_data = OrderedDict()
            test_data['log'] = os.path.basename(file).split('_result.')[0]
            try:
                json_dict = json.load(f)

                if 'sensor_id' in json_dict['device']:
                    test_data['sensorid'] = json_dict['device']['sensor_id']
                else:
                    test_data['sensorid'] = ''

                for item in json_dict['sequence']:
                    if item['name'] == 'module_quality':
                        test_data['mqt_result'] = check_test_method_conclusion_primax(item)
                        if 'snr_db' in item['analysis']['result']['snr']:
                            test_data['snr'] = item['analysis']['result']['snr']['snr_db']

                        if hasattr(self, 'fmi_folder') and hasattr(self, 'limits'):
                            self.move_fmi(float(test_data['snr']), file)

                        # break

            except KeyError as e:
                logging.error('KeyError {} happens in {} {}, might be no test result, regard all nan'.format(e,
                                                                                                             self.__class__.__name__,
                                                                                                             file))
            finally:
                return test_data

    def _get_data_html(self, file):
        mqt_patterns = OrderedDict()
        mqt_patterns['sensorid'] = r'Sensor ID: (.*)'
        mqt_patterns['MQT'] = r'Module Quality Test: (.*)'
        mqt_patterns['error_code'] = r'Make sure stamp is in contact with sensor\nTest failed, reason: (.*)'
        mqt_patterns['snr'] = r'SNR\(dB\): (.*)'
        mqt_patterns['blob'] = r'Blob count: (.*)'
        mqt_patterns['udr'] = 'UDR: (.*)'

        log_mqt_dict = OrderedDict()
        log_mqt_dict['log'] = os.path.basename(file).split('.')[0]
        log_mqt_dict['host_id'] = 'N/A'
        with open(file, mode='r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'lxml')
            try:
                text = soup.text

                for key, value in mqt_patterns.items():
                    res = re.findall(value, text)
                    if res:
                        if key == 'MQT':
                            log_mqt_dict[key] = 1 if res[0] == 'Pass' else 0
                        elif key == 'error_code' or key == 'sensorid':
                            log_mqt_dict[key] = res[0]
                        else:
                            log_mqt_dict[key] = float(res[0])

                            if key == 'snr' and hasattr(self, 'fmi_folder') and hasattr(self, 'limits'):
                                self.move_fmi(float(res[0]), file)

            except Exception as e:
                logging.error(file, sys.exc_info())
            finally:
                return log_mqt_dict

    def move_fmi(self, snr, files):
        '''
        Move fmi & json to another path according to SNR limit
        :param snr: SNR value from logs
        :param file: log file
        :return:
        '''
        if snr >= self.limits[0] and snr < self.limits[1]:
            if not os.path.exists(self.fmi_folder):
                os.mkdir(self.fmi_folder)
            for file in files:
                logging.info('Copying', file)
                shutil.copy(file, self.fmi_folder)

    # Calculate yield based on different SNR value
    def cal_yield_on_snr(self, snr):
        result = pd.DataFrame(self.yield_results())
        result_on_snr = result['snr'] >= snr
        counts = result_on_snr.value_counts()

        yield_rate = counts[True] / sum(counts)
        return yield_rate

    def get_wafer_info(self, otp_data):
        admin = otp_data[0] & 0x1F
        if admin == 1 or admin == 4:
            lot_id = "%c%c%c%d" % (otp_data[1], otp_data[2], otp_data[3], otp_data[4] * 256 + otp_data[5])
        elif admin == 2:
            fab_id = (otp_data[1] & 0xF0) >> 4
            if 1 == fab_id:
                fab_code = 'G'
            elif 2 == fab_id:
                fab_code = 'Q'
            else:
                fab_code = 'H'

            lot_id = "%s%c%c%c%c%c" % (fab_code,
                                       ((otp_data[1] & 0xF) << 3 | (otp_data[2] & 0xE0) >> 5) & 0xFF,
                                       ((otp_data[2] & 0x1F) << 2 | (otp_data[3] & 0xC0) >> 6) & 0xFF,
                                       ((otp_data[3] & 0x3F) << 1 | (otp_data[4] & 0x80) >> 7) & 0xFF,
                                       (otp_data[4] & 0x7F),
                                       (otp_data[5] & 0xF7) >> 1)
        elif admin == 3:
            lot_id = "%c%c%c%c%c" % (otp_data[1], otp_data[2], otp_data[3], otp_data[4], otp_data[5])
        elif admin == 5:
            lot_id = "%c%c%c%c%d" % (otp_data[1], otp_data[2], otp_data[3], otp_data[4], otp_data[5])
        else:
            return None
        x_coordinate = otp_data[6]
        y_coordinate = otp_data[7]
        wafer_id = otp_data[8] >> 3
        return lot_id, x_coordinate, y_coordinate, wafer_id

    def show_hist(self):
        for index in range(0, self.max_mqt_count):
            key_snr = 'snr' + self._get_key_suffix(index)
            key_fix_pattern = 'FixedPatternPixels' + self._get_key_suffix(index)
            if os.path.exists(self.report_file):
                results = analyze_excel(self.report_file).get_valid_datas_by_key(key_snr)
            else:
                return
            snr_results = []
            pxl_results = []
            for row in results.itertuples(index=False):
                if hasattr(row, key_snr):
                    val1 = getattr(row, key_snr)
                    if not math.isnan(val1):
                        snr_results.append(math.floor(val1))
                if hasattr(row, key_snr) and hasattr(row, key_fix_pattern):
                    val2 = getattr(row, key_fix_pattern)
                    if not math.isnan(val1) and not math.isnan(val2):
                        pxl_results.append(round(val2))
            snr_frequencies = []
            for value in range(0, max(snr_results) + 1):
                snr_frequency = snr_results.count(value)
                snr_frequencies.append(snr_frequency)
            hist = pygal.Bar()
            hist.title = "snr distribution, limit > {}db".format(self.settings_dict['snr'])
            hist.x_title = "snr value"
            hist.y_title = "number of snr"
            hist.x_labels = range(0, max(snr_results) + 1)
            hist.add("snr", snr_frequencies)
            try:
                hist.render_to_file(os.path.splitext(self.report_file)[0] + '_' + key_snr + '.svg')
            except Exception as e:
                print("{}::{} Exception:".format(self.__class__.__name__, sys._getframe().f_code.co_name))
                print(e)

            if len(pxl_results) == 0:
                return
            pxl_frequencies = []
            for value in range(0, max(pxl_results) + 1):
                pxl_frequency = pxl_results.count(value)
                pxl_frequencies.append(pxl_frequency)
            hist = pygal.Bar()
            hist.title = "FixedPatternPixels distribution, limit < {}".format(self.settings_dict['FixedPattern'])
            hist.x_title = "FixedPatternPixels value"
            hist.y_title = "number of FixedPatternPixels"
            hist.x_labels = range(0, max(pxl_results) + 1)
            hist.add("FixedPatternPixels", pxl_frequencies)
            try:
                hist.render_to_file(os.path.splitext(self.report_file)[0] + '_' + key_fix_pattern + '.svg')
            except Exception as e:
                print("{}::{} Exception:".format(self.__class__.__name__, sys._getframe().f_code.co_name))
                print(e)
