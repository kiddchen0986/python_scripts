# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#

from collections import OrderedDict
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
from util import gen_find
from util import typeassert
from util import get_window_size
import re
import numpy as np
import sys
from bs4 import BeautifulSoup
import os
import logging
import shutil
import operator
import pygal
from analyze_excel_data import analyze_excel
from json_settings import defective_json_settings
'''
Implement all the parsers for MTT log analysis
Always support json
To support txt and html if necessary
'''
logging.basicConfig(level=logging.ERROR)

style.use('ggplot')


def config(x_label_rotation=45, show_legend=True, title_font_size=24, label_font_size=14,
           major_label_font_size=18, truncate_label=15, show_y_guides=15, width=1200):
    my_config = pygal.Config()
    my_config.x_label_rotation = x_label_rotation
    my_config.show_legend = show_legend
    my_config.title_font_size = title_font_size
    my_config.label_font_size = label_font_size
    my_config.major_label_font_size = major_label_font_size
    my_config.truncate_label = truncate_label
    my_config.show_y_guides = show_y_guides
    my_config.width = width
    return my_config


def check_test_method_conclusion(item):
    '''
    The method checks the result of test case
    :param item: json dict
    :return: 1, 0, nan
    '''
    if item['Result']['TestMethodConclusion'] == 'Success':
        return 1
    elif item['Result']['TestMethodConclusion'] == 'Fail' or item['Result']['TestMethodConclusion'] == 'Exception':
        return 0
    else:
        return np.nan


def check_test_method_conclusion_primax(item):
    '''
    The method checks the result of test case
    :param item: json dict
    :return: 1, 0, nan
    '''
    if item['conclusion'] == 'pass':
        return 1
    elif item['conclusion'] == 'Fail' or item['conclusion'] == 'Exception':
        return 0
    else:
        return np.nan


def get_host_sensor_id(text):
    '''
    The method returns sensorid and hostid if existed
    :param text: string or json dict
    :return: sensorid, hostid, time
    '''
    host_id = 'N/A'
    sensor_id = 'N/A'

    if isinstance(text, dict):
        if 'StationInfo' in text and 'Id' in text['StationInfo']:
            host_id = text['StationInfo']['Id']

        if 'Identity' in text:
            if 'SensorId' in text['Identity']:
                sensor_id = text['Identity']['SensorId']
            elif 'UniqueTestId' in text['Identity']:
                sensor_id = text['Identity']['UniqueTestId']

    else:
        res = re.findall(r'Sensor ID: (.*)', text)
        if res:
            sensor_id = res[0]

        res = re.findall(r'Hostname|Session: (.*)', text)
        if res:
            host_id = res[0]

    return host_id, sensor_id


@typeassert(log_path=str, log_pattern=str, report_file=str)
class logParser(object):
    '''
    Base class of the parser
    '''

    def __init__(self, log_path: str, log_pattern='*.json', report_file: str = ''):
        '''
        Initialize the parser
        :param log_path: MTT log path
        :param log_pattern: MTT log format, could be json, txt, html
        :param report_file: report file, could be excel, csv, html
        '''
        self.log_path = log_path
        self.report_file = report_file
        self.log_pattern = log_pattern
        self.settings_dict = OrderedDict()

    def __str__(self):
        return str(self.__class__.__name__[len(__class__.__name__):])

    def save_report(self, df: pd.DataFrame):
        '''
        Save the data frame to csv, excel, html, called by self.analyze
        :param df: MTT data frame
        :return: None
        '''
        if self.report_file.endswith('.csv'):
            df.to_csv(self.report_file, encoding='utf-8', index=False)
        elif self.report_file.endswith('.html'):
            df.to_html(self.report_file, index=False)
        elif self.report_file.endswith('.xls'):
            df.to_excel(self.report_file, encoding='utf-8', index=False)

        logging.info('Finish saving {}'.format(self.report_file))

    def analyze(self):
        '''
        Run the analyze by calling self.yield_results
        :return: None
        '''
        results = list(self.yield_results())
        if len(results) == 0:
            logging.error('No {} data, are you setting correct path ?'.format(self))
            exit(-1)

        df = pd.DataFrame(results)
        # if len(df.columns) <= 3:
        #    logging.error('no test result')
        #    return

        self.save_report(df)
        df.dropna(inplace=True)
        logging.info(df.describe())

        return self.show_hist()

    def yield_results(self):
        '''
        Yield results by call _get_data_json, _get_data_html or _get_data_txt based on log_pattern
        :return: None
        '''
        for file in gen_find(self.log_pattern, self.log_path):
            yield getattr(self, '_get_data_' + self.log_pattern.split('.')[1])(file)

    def show_hist(self):
        '''
        Show and save the histogram
        :param df: All the MTT data frame
        :return: None
        '''
        # df.hist(figsize=get_window_size(), bins=20)

        # plt.savefig(self.report_file.split('.')[0] + '.png')
        # plt.show()

    def get_general_yield(self):
        '''
        Calculate the yield based on the logs
        :return: Data Frame
        '''
        yield_row = pd.DataFrame([self.df.mean()])
        new_df = pd.concat([yield_row, self.df], ignore_index=True, sort=False)
        final_df = new_df[self.df.columns]
        self.save_report(final_df)

        return final_df

    def get_unique_sensor_yield(self):
        '''
        Calculate the yield based on the module
        :return: Data Frame
        '''
        groupby = self.df.groupby('sensorid')
        df_group = groupby.mean()

        test_yield = {}
        for col in df_group:
            count = pd.value_counts(df_group[col])
            if 0 in count.index:
                test_yield[col] = 1 - count[0] / sum(count)
            else:
                test_yield[col] = 1

        yield_row = pd.DataFrame([test_yield], index=['yield'])
        new_df = pd.concat([yield_row, df_group], ignore_index=False, sort=False)

        final_sensor_df = new_df[self.df.columns[3:]]

        if len(self.report_file) != 0:
            directory, file = os.path.split(self.report_file)
            if directory:
                final_sensor_df.to_excel(os.path.join(directory, file.split('.')[0] + '_unique_sensor.xls'),
                                         encoding='utf-8')
            else:
                final_sensor_df.to_excel(file.split('.')[0] + '_unique_sensor.xls', encoding='utf-8')

            logging.info('Finish saving sensor_yield.xls')

        return final_sensor_df

    @staticmethod
    def show_top2_hist_text(hist, ax):
        '''
        Show the data of the top2 items in histogram
        '''
        count_and_vals = sorted(zip(hist[0], hist[1], hist[2]), reverse=True)

        ax.text(count_and_vals[0][1], count_and_vals[0][2].get_height(), (count_and_vals[0][1], count_and_vals[0][0]))
        ax.text(count_and_vals[1][1], count_and_vals[1][2].get_height(), (count_and_vals[1][1], count_and_vals[1][0]))


class logParserDfdCal(logParser):
    def _get_data_json(self, json_file):
        with open(json_file, encoding='utf-8', mode='r') as f:
            test_data = OrderedDict()
            test_data['log'] = os.path.basename(json_file).split('_result.')[0]
            try:
                json_dict = json.load(f)
                test_data['host_id'], test_data['sensorid'] = get_host_sensor_id(json_dict)

                for item in json_dict['TestReportItems']:
                    if item['Name'].startswith('DFD Calibration'):
                        test_data['DFD Calibration'] = check_test_method_conclusion(item)
                        test_data['DfdCalibrationVal'] = int(
                            item['Result']['TestLog']['Steps']['measurement']['Items']['DfdCalibrationVal'])
                        test_data['DfdCalibrationOffset'] = int(
                            item['Result']['TestLog']['Steps']['measurement']['Items']['DfdCalibrationOffset'])

            except KeyError as e:
                logging.error('KeyError {} happens in {}, might be no test result, regard all nan'.format(e, json_file))
            finally:
                return test_data


class logParserDfdSignal(logParser):
    def _get_data_json(self, json_file):
        with open(json_file, encoding='utf-8', mode='r') as f:
            test_data = OrderedDict()
            test_data['log'] = os.path.basename(json_file).split('_result.')[0]
            try:
                json_dict = json.load(f)
                test_data['host_id'], test_data['sensorid'] = get_host_sensor_id(json_dict)

                for item in json_dict['TestReportItems']:
                    if item['Name'].startswith('Dfd Signal'):
                        test_data['Dfd Signal'] = check_test_method_conclusion(item)
                        test_data['Timeout'] = item['Result']['TestLog']['Steps']['analysis']['Items'][
                                                   'Timeout'] == 'True'
                        test_data['Median'] = float(item['Result']['TestLog']['Steps']['analysis']['Items']['Median'])
                        test_data['Min'] = float(item['Result']['TestLog']['Steps']['analysis']['Items']['Min'])
                        test_data['Max'] = float(item['Result']['TestLog']['Steps']['analysis']['Items']['Max'])
                        test_data['Low5'] = float(item['Result']['TestLog']['Steps']['analysis']['Items']['Low5'])
                        test_data['High5'] = float(item['Result']['TestLog']['Steps']['analysis']['Items']['High5'])
                        test_data['SubAreaPixelsLess50'] = int(
                            item['Result']['TestLog']['Steps']['analysis']['Items']['SubAreaPixelsLess50'])
                        test_data['SubAreaPixelsLess80'] = int(
                            item['Result']['TestLog']['Steps']['analysis']['Items']['SubAreaPixelsLess80'])
                        test_data['SubAreaPixelsLess100'] = int(
                            item['Result']['TestLog']['Steps']['analysis']['Items']['SubAreaPixelsLess100'])
                        test_data['SubAreaPixelsLess130'] = int(
                            item['Result']['TestLog']['Steps']['analysis']['Items']['SubAreaPixelsLess130'])
                        test_data['SubAreaPixelsLess180'] = int(
                            item['Result']['TestLog']['Steps']['analysis']['Items']['SubAreaPixelsLess180'])
                        test_data['Zone5SubAreaLess50'] = int(
                            item['Result']['TestLog']['Steps']['analysis']['Items']['Zone5SubAreaLess50'])
                        test_data['Zone6SubAreaLess50'] = int(
                            item['Result']['TestLog']['Steps']['analysis']['Items']['Zone6SubAreaLess50'])
                        test_data['Zone5SubAreaLess100'] = int(
                            item['Result']['TestLog']['Steps']['analysis']['Items']['Zone5SubAreaLess100'])
                        test_data['Zone6SubAreaLess100'] = int(
                            item['Result']['TestLog']['Steps']['analysis']['Items']['Zone6SubAreaLess100'])
                        test_data['DfdPixelsLessThan50'] = int(
                            item['Result']['TestLog']['Steps']['analysis']['Items']['DfdPixelsLessThan50'])
                        test_data['DfdPixelsLessThan100'] = int(
                            item['Result']['TestLog']['Steps']['analysis']['Items']['DfdPixelsLessThan100'])
                        test_data['ShouldDfdBeTriggeredOn50'] = (item['Result']['TestLog']['Steps']['analysis']['Items']
                                                                 ['ShouldDfdBeTriggeredOn50'] == 'True')
                        test_data['ShouldDfdBeTriggeredOn100'] = (
                                item['Result']['TestLog']['Steps']['analysis']['Items'][
                                    'ShouldDfdBeTriggeredOn100'] == 'True')
                        test_data['SubAreaMedian'] = int(
                            item['Result']['TestLog']['Steps']['analysis']['Items']['SubAreaMedian'])

            except KeyError as e:
                logging.error('KeyError {} happens in {}, might be no test result, regard all nan'.format(e, json_file))
            finally:
                return test_data


class logParserOtpInfo(logParser):
    def _get_data_txt(self, file):
        otp_info = OrderedDict()
        otp_info['log'] = os.path.basename(file).split('_log.')[0]
        with open(file, encoding='utf-8', mode='r') as f:
            try:
                text = f.read()
                otp_info['host_id'], otp_info['sensorid'] = get_host_sensor_id(text)

                res = re.findall(r'Test started: (.*)', text)
                if res:
                    otp_info['test_time'] = res[0]

                res = re.findall(r'User: (.*)', text)
                if res:
                    otp_info['user'] = res[0]

                if r'-> Test Write Otp' in text:
                    otp_info['sequence'] = 'write_otp'
                    if r'Amount of vendor bytes specified' in text or r'Vendor data size mismatch!' in text:
                        otp_info['module_vendor_otp_size_mismatch'] = 'true'
                    else:
                        otp_info['module_vendor_otp_size_mismatch'] = 'false'
                else:
                    otp_info['sequence'] = 'default'

                total_err_bit = re.findall(r'Total Bit Errors: (.*)', text)
                total_err_byte = re.findall(r'Bit error found in byte (.*)', text)
                max_err_bit = re.findall(r'Max Bit Errors in one byte: (.*)', text)
                date = re.findall(r'Date: (.*)', text)
                module_version = re.findall(r'MODULE SECTION: Version Version(.*)', text)
                wafer_version = re.findall(r'WAFER SECTION: Version Version(.*)', text)

                if total_err_bit:
                    otp_info['total_bit_errors'] = int(total_err_bit[0])
                else:
                    otp_info['total_bit_errors'] = 0
                if total_err_byte:
                    otp_info['total_byte_errors'] = len(total_err_byte)
                else:
                    otp_info['total_byte_errors'] = 0
                if max_err_bit:
                    otp_info['max_bit_err_in_one_byte'] = int(max_err_bit[0])
                else:
                    otp_info['max_bit_err_in_one_byte'] = 0

                if module_version:
                    otp_info['module_version'] = int(module_version[0])
                else:
                    otp_info['module_version'] = 0

                if wafer_version:
                    otp_info['wafer_version'] = int(wafer_version[0])
                else:
                    otp_info['wafer_version'] = 0

                if date:
                    if len(date) >= 2:
                        otp_info['wafer_production_date'] = date[0]
                        if r'MODULE SECTION: Version' in text:
                            otp_info['module_production_date'] = date[1]
                    elif len(date) == 1:
                        otp_info['wafer_production_date'] = date[0]

            except KeyError as e:
                logging.error('KeyError {} happens in {}, might be no test result, regard all nan'.format(e, file))
            finally:
                return otp_info


class logParserReadOtp(logParser):
    def _get_data_json(self, json_file):
        with open(json_file, encoding='utf-8', mode='r') as f:
            test_data = OrderedDict()
            test_data['log'] = os.path.basename(json_file).split('_result.')[0]
            try:
                json_dict = json.load(f)
                test_data['host_id'], test_data['sensorid'] = get_host_sensor_id(json_dict)

                for item in json_dict['TestReportItems']:
                    if item['Name'].startswith('TestReadOtp'):
                        test_data['OtpMemoryMainData'] = item['Result']['TestLog']['Steps']['measurement']['Items'][
                            'OtpMemoryMainData']
                        test_data['OtpMemoryBackupData'] = item['Result']['TestLog']['Steps']['measurement']['Items'][
                            'OtpMemoryBackupData']
                        # Wafer Section
                        test_data['WaferSectMainData'] = test_data['OtpMemoryMainData'].split(' ', -1)[0:12]
                        test_data['LayoutTagMainData'] = test_data['WaferSectMainData'][0][0]
                        test_data['WaferSectMainData'][0] = test_data['WaferSectMainData'][0][1]
                        test_data['WaferSectBackupData'] = test_data['OtpMemoryBackupData'].split(' ', -1)[0:12]
                        test_data['LayoutTagBackupData'] = test_data['WaferSectBackupData'][0][0]
                        test_data['WaferSectBackupData'][0] = test_data['WaferSectBackupData'][0][1]
                        test_data['WaferSectCheck'] = operator.eq(test_data['WaferSectMainData'],
                                                                  test_data['WaferSectBackupData'])
                        # Module Section
                        test_data['ModuleSectMainData'] = test_data['OtpMemoryMainData'].split(' ', -1)[12:19]
                        test_data['ModuleSectBackupData'] = test_data['OtpMemoryBackupData'].split(' ', -1)[12:19]
                        tmplist = ['00', '00', '00', '00', '00', '00', '00']
                        if (operator.eq(test_data['ModuleSectMainData'], tmplist)) or (
                                operator.eq(test_data['ModuleSectBackupData'], tmplist)):
                            test_data['ModuleSectCheck'] = False
                        else:
                            test_data['ModuleSectCheck'] = operator.eq(test_data['ModuleSectMainData'],
                                                                       test_data['ModuleSectBackupData'])
                        # Layout Tag Check
                        if ((test_data['LayoutTagMainData'] == '8') and (test_data['LayoutTagBackupData'] == '8')):
                            test_data['LayoutTagCheck'] = True
                        else:
                            test_data['LayoutTagCheck'] = False
                        test_data['read_otp_result'] = test_data['LayoutTagCheck'] and test_data['WaferSectCheck'] and \
                                                       test_data['ModuleSectCheck']
                        test_data['TotalBitErrors'] = item['Result']['TestLog']['Steps']['measurement']['Items'][
                            'TotalBitErrors']
                        test_data['MaxBitErrorsInOneByte'] = item['Result']['TestLog']['Steps']['measurement']['Items'][
                            'MaxBitErrorsInOneByte']

            except KeyError as e:
                logging.error('KeyError {} happens in {}, might be no test result, regard all nan'.format(e, json_file))
            finally:
                return test_data

    def _get_data_txt(self, file):
        otp_info = OrderedDict()
        otp_info['log'] = os.path.basename(file).split('_log.')[0]
        with open(file, encoding='utf-8', mode='r') as f:
            text = f.read()
            if '-> Test Read OTP (TestReadOtp)' in text:
                err_bit = re.findall(r'Bit error found in byte (.*)', text)
                date = re.findall(r'Date: (.*)', text)

                if err_bit:
                    otp_info['err_bit'] = err_bit[0]
                if date and len(date) == 2:
                    otp_info['date'] = date[1]

            return otp_info


class logParserWaferInfo(logParser):
    def __init__(self, log_path: str, report_file: str = ''):
        super().__init__(log_path, report_file=report_file, log_pattern='*.txt')

    def _get_data_txt(self, file):
        otp_info = OrderedDict()
        otp_info['log'] = os.path.basename(file).split('_log.')[0]
        with open(file, encoding='utf-8', mode='r') as f:
            text = f.read()
            otp_info['host_id'], otp_info['sensorid'] = get_host_sensor_id(text)
            if '-> Test Read OTP (TestReadOtp)' in text:
                lot_id = re.findall(r'LOT ID: (.*)', text)
                x_id = re.findall(r'X Coordinate: (.*)', text)
                y_id = re.findall(r'Y Coordinate = (.*)', text)
                id_id = re.findall(r'\nID: (.*)', text)

                otp_info['lot_id'] = lot_id[0]
                otp_info['x_id'] = x_id[0]
                otp_info['y_id'] = y_id[0]
                otp_info['id'] = id_id[0]

            return otp_info


class logParserCap(logParser):
    data_columns = ['signal_strength', 'uniformity_level', 'number_of_blob_pixels']

    def _get_data_json(self, json_file: str):
        with open(json_file, encoding='utf-8', mode='r') as f:
            test_data = OrderedDict()
            test_data['log'] = os.path.basename(json_file).split('_result.')[0]
            try:
                json_dict = json.load(f)

                test_data['host_id'], test_data['sensorid'] = get_host_sensor_id(json_dict)

                for item in json_dict['TestReportItems']:
                    if item['Name'].startswith('Capacitance Test'):
                        test_data['cap_result'] = check_test_method_conclusion(item)

                        self.settings_dict['MaxUniformityLevel'] = \
                            item['Result']['TestLog']['Steps']['initialization']['Items']['settings'][
                                'MaxUniformityLevel']
                        self.settings_dict['MaxSignalStrength'] = \
                            item['Result']['TestLog']['Steps']['initialization']['Items']['settings'][
                                'MaxSignalStrength']
                        self.settings_dict['MinSignalStrength'] = \
                            item['Result']['TestLog']['Steps']['initialization']['Items']['settings'][
                                'MinSignalStrength']
                        self.settings_dict['max_number_of_blob_pixels'] = \
                            item['Result']['TestLog']['Steps']['initialization']['Items']['settings']['BlobConfig'][
                                'max_number_of_blob_pixels']

                        for i in self.data_columns:
                            test_data[i] = float(item['Result']['TestLog']['Steps']['initialization']['Items'][i]['d'])

                        break
                    elif item['Name'].startswith('CTL Capacitance Test 2'):
                        test_data['cap2_result'] = check_test_method_conclusion(item)

                        self.settings_dict['MaxUniformityLevel'] = \
                            item['Result']['TestLog']['Steps']['analysis']['Items']['test_criteria'][
                                'MaxUniformityLevel']
                        self.settings_dict['MaxSignalStrength'] = \
                            item['Result']['TestLog']['Steps']['analysis']['Items']['test_criteria'][
                                'MaxSignalStrength']
                        self.settings_dict['MinSignalStrength'] = \
                            item['Result']['TestLog']['Steps']['analysis']['Items']['test_criteria'][
                                'MinSignalStrength']
                        self.settings_dict['max_number_of_blob_pixels'] = \
                            item['Result']['TestLog']['Steps']['analysis']['Items']['test_criteria'][
                                'max_number_of_blob_pixels']

                        test_data['uniformity_level'] = float(
                            defective_json_settings(item)['analysis_result']['UniformityLevel'])
                        test_data['signal_strength'] = float(
                            defective_json_settings(item)['analysis_result']['SignalStrength'])
                        test_data['number_of_blob_pixels'] = float(
                            defective_json_settings(item)['analysis_result']['BlobCount'])

                        break

            except KeyError as e:
                logging.error('KeyError {} happens in {}, might be no test result, regard all nan'.format(e, json_file))
            finally:
                return test_data

    def _get_data_html(self, file):
        self.settings_dict['MaxSignalStrength'] = 1.3
        self.settings_dict['MinSignalStrength'] = 0.3
        self.settings_dict['MaxUniformityLevel'] = 0.15
        self.settings_dict['max_number_of_blob_pixels'] = 7

        test_patterns = OrderedDict()
        test_patterns['sensorid'] = r'Sensor ID: (.*)'
        test_patterns['Capacitance'] = r'Capacitance Test: (.*)'
        test_patterns['signal_strength'] = r'Capacitance Signal Strength Median: (.*)'
        test_patterns['uniformity_level'] = r'Uniformity: (.* )% \(limit:'
        test_patterns['number_of_blob_pixels'] = r'Number of blobs pixels: (.*) \(limit: '

        log_dict = OrderedDict()
        log_dict['log'] = os.path.basename(file).split('.')[0]
        log_dict['host_id'] = 'N/A'
        with open(file, mode='r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'lxml')
            try:
                text = soup.text

                for key, value in test_patterns.items():
                    res = re.findall(value, text)
                    if res:
                        if key == 'Capacitance':
                            log_dict[key] = 1 if res[0] == 'Pass' else 0
                        elif key == 'host_id' or key == 'sensorid':
                            log_dict[key] = res[0]
                        elif key == 'uniformity_level':
                            log_dict[key] = float(res[0]) / 100
                        else:
                            log_dict[key] = float(res[0])

            except Exception as e:
                logging.error(file, sys.exc_info())
            finally:
                return log_dict

    def show_hist(self, df):
        figure = plt.figure(figsize=get_window_size())
        axes = figure.subplots(2, 2)

        max_val = max(df[self.data_columns[0]].max(), self.settings_dict['MinSignalStrength'])
        step = (self.settings_dict['MaxSignalStrength'] - self.settings_dict['MinSignalStrength']) / 10

        histo = axes[0, 0].hist(df[self.data_columns[0]], bins=np.arange(0, max_val + 1, step),
                                label=self.data_columns[0], color=np.random.rand(3))
        self.show_top2_hist_text(histo, axes[0, 0])

        axes[0, 0].plot([self.settings_dict['MinSignalStrength'], self.settings_dict['MinSignalStrength']],
                        [0, int(max(histo[0]))], 'r--', label='signal min threshold')
        axes[0, 0].plot([self.settings_dict['MaxSignalStrength'], self.settings_dict['MaxSignalStrength']],
                        [0, int(max(histo[0]))], 'g--', label='signal max threshold')
        axes[0, 0].set_xticks(np.arange(0, self.settings_dict['MaxSignalStrength'] + 0.3, 0.1))
        axes[0, 0].set_title('signal hist')
        axes[0, 0].legend(loc='best')

        step = self.settings_dict['MaxUniformityLevel'] / 10
        histo = axes[0, 1].hist(df[self.data_columns[1]],
                                bins=np.arange(0, df[self.data_columns[1]].max() + 5 * step, step),
                                label=self.data_columns[1], color=np.random.rand(3))
        self.show_top2_hist_text(histo, axes[0, 1])
        axes[0, 1].plot([self.settings_dict['MaxUniformityLevel'], self.settings_dict['MaxUniformityLevel']],
                        [0, int(max(histo[0]))], 'r--', label='uniformity threshold')
        axes[0, 1].set_title('uniformity hist')
        axes[0, 1].legend(loc='best')

        histo = axes[1, 0].hist(df[self.data_columns[2]],
                                bins=np.arange(df[self.data_columns[2]].min(), df[self.data_columns[2]].max() + 5, 1),
                                label=self.data_columns[2], color=np.random.rand(3))
        self.show_top2_hist_text(histo, axes[1, 0])
        axes[1, 0].plot(
            [self.settings_dict['max_number_of_blob_pixels'], self.settings_dict['max_number_of_blob_pixels']],
            [0, int(max(histo[0]))], 'r--', label='blob threshold')
        axes[1, 0].set_title('blob hist')
        axes[1, 0].legend(loc='best')

        axes[1, 1].scatter(df[self.data_columns[0]], df[self.data_columns[1]], color=np.random.rand(3))
        axes[1, 1].set_title(self.data_columns[0] + ' vs ' + self.data_columns[1])
        axes[1, 1].set_xlabel(self.data_columns[0])
        axes[1, 1].set_ylabel(self.data_columns[1])

        axes[1, 1].legend(loc='best')

        plt.savefig(self.report_file.split('.xls')[0] + '.png')
        plt.show()

        return df


class logParserMqt(logParser):
    def _get_data_json(self, file):
        with open(file, encoding='utf-8', mode='r') as f:
            test_data = OrderedDict()
            test_data['log'] = os.path.basename(file).split('_result.')[0]
            try:
                json_dict = json.load(f)

                test_data['host_id'], test_data['sensorid'] = get_host_sensor_id(json_dict)

                for item in json_dict['TestReportItems']:
                    if item['Result']['TestName'] == 'TestModuleQuality2':
                        test_data['mqt2_result'] = check_test_method_conclusion(item)
                        if item['Result']['TestLog']['Steps']['measurement']['Items']['settings']['Analysis']['Snr'][
                            'IsEnabled']:
                            test_data['snr2'] = defective_json_settings(item)['analysis_result']['Snr']['SnrDb']
                            if float(test_data['snr2']) == -1000:
                                test_data['snr2'] = -1
                            self.settings_dict['snr2'] = \
                                item['Result']['TestLog']['Steps']['measurement']['Items']['settings']['Analysis'][
                                    'Snr']['SnrLimitDb']

                        if item['Result']['TestLog']['Steps']['measurement']['Items']['settings']['Analysis']['Blob'][
                            'IsEnabled']:
                            test_data['blob'] = \
                                defective_json_settings(item)['analysis_result']['Blob']['BlobCount']
                            self.settings_dict['blob'] = \
                                item['Result']['TestLog']['Steps']['measurement']['Items']['settings']['Analysis'][
                                    'Blob']['BlobLimit']

                        if item['Result']['TestLog']['Steps']['measurement']['Items']['settings']['Analysis'][
                            'Uniformity']['IsEnabled']:
                            test_data['udr'] = \
                                defective_json_settings(item)['analysis_result']['Uniformity']['Udr']
                            self.settings_dict['udr'] = \
                                item['Result']['TestLog']['Steps']['measurement']['Items']['settings']['Analysis'][
                                    'Uniformity']['UdrLimit']

                        if 'FixedPattern' in defective_json_settings(item)['analysis_result'] and \
                                item['Result']['TestLog']['Steps']['measurement']['Items']['settings']['Analysis'][
                                    'FixedPattern']['IsEnabled']:
                            test_data['FixedPatternPixels'] = \
                                defective_json_settings(item)['analysis_result']['FixedPattern']['FixedPatternPixels']
                            self.settings_dict['FixedPattern'] = \
                                item['Result']['TestLog']['Steps']['measurement']['Items']['settings']['Analysis'][
                                    'FixedPattern']['FixedPatternLimit']

                        if hasattr(self, 'fmi_folder') and hasattr(self, 'limits'):
                            self.move_fmi(float(test_data['snr2']), file)

                        # break

                    if item['Result']['TestName'] == 'TestModuleQuality':
                        test_data['mqt_result'] = check_test_method_conclusion(item)
                        test_data['snr'] = item['Result']['TestLog']['Steps']['analysis']['Items']['snr_db']
                        if float(test_data['snr']) == -1000:
                            test_data['snr'] = -1

                        if 'SnrLimit' in item['Result']['TestLog']['Steps']['measurement']['Items']['settings']:
                            self.settings_dict['snr'] = \
                                item['Result']['TestLog']['Steps']['measurement']['Items']['settings'][
                                    'SnrLimit']

                        if hasattr(self, 'fmi_folder') and hasattr(self, 'limits'):
                            self.move_fmi(float(test_data['snr']), file)

                        # break

            except KeyError as e:
                logging.error('KeyError {} happens in MQT {}, might be no test result, regard all nan'.format(e, file))
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
                logging.error('KeyError {} happens in {}, might be no test result, regard all nan'.format(e, file))
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

    def move_fmi(self, snr, file):
        '''
        Move fmi & json to another path according to SNR limit
        :param snr: SNR value from logs
        :param file: log file
        :return:
        '''
        if snr >= self.limits[0] and snr < self.limits[1]:
            file_names = os.path.basename(file).split('.')[0].split('_')
            prefix = file_names[0]  # + '_' + file_names[1]

            if not os.path.exists(self.fmi_folder):
                os.mkdir(self.fmi_folder)
            for path, _, file_list in os.walk(self.log_path):
                for f in file_list:
                    if prefix in f and (f.endswith('.fmi') or f.endswith('.json')):
                        logging.info('Copying', os.path.join(path, f))
                        shutil.copy(os.path.join(path, f), self.fmi_folder)

    # Calculate yield based on different SNR value
    def cal_yield_on_snr(self, snr):
        result = pd.DataFrame(self.yield_results())
        result_on_snr = result['snr'] >= snr
        counts = result_on_snr.value_counts()

        yield_rate = counts[True] / sum(counts)
        return yield_rate

    def show_hist(self):
        frequencies = []
        if os.path.exists(self.report_file):
            results = analyze_excel(self.report_file).get_valid_data(4)

        for value in range(0, max(results) + 1):
            frequency = results.count(value)
            frequencies.append(frequency)

        hist = pygal.Bar()
        hist.title = "snr distribution, limit > {}db".format(self.settings_dict['snr2'])
        hist.x_title = "snr value"
        hist.y_title = "number of snr"
        hist.x_labels = range(0, max(results) + 1)
        hist.add("snr", frequencies)
        hist.render_to_file(self.report_file.split('.xls')[0] + '.svg')


class logParserCtlImageDrive(logParser):
    data_columns = [
        'PixelErrors',
        'SubAreaErrors',
        'GlobalPixelErrors',
        'MedianRow_1',
        'MedianRow_2',
        'MedianRowMiddle',
        'MedianRowNextToLast',
        'MedianRowLast',
        'MedianRow_1_Inv',
        'MedianRowLastInv',
        'MedianRow_1_DevMax',
        'MedianRow_2_DevMax',
        'MedianRowMiddleDevMax',
        'MedianRowNextToLastDevMax',
        'MedianRowLastDevMax',
        'MedianRow_1_InvDevMax',
        'MedianRowLastInvDevMax'
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

                            for item in self.data_columns:
                                if 'ImageDriveResult' in defective_json_settings(report)['analysis_result']:
                                    test_dict[item] = defective_json_settings(report)['analysis_result'][
                                            'ImageDriveResult'][item]
                                elif 'ImageDriveAnalysisResult' in defective_json_settings(report)['analysis_result']:
                                    test_dict[item] = \
                                        defective_json_settings(report)['analysis_result']['ImageDriveAnalysisResult'][item]

                        return test_dict

            except KeyError as e:
                logging.error('KeyError {} happens in {}, might be no test result, regard all nan'.format(e, file))
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

                        if 'ImageConstantAnalysisResult' in defective_json_settings(report)['analysis_result']:
                            medians = defective_json_settings(report)['analysis_result']['ImageConstantAnalysisResult'][
                                'ImageConstantMedians']
                            for i, val in enumerate(medians):
                                test_dict['median_' + str(i)] = val
                            test_dict['PixelErrors'] = \
                            defective_json_settings(report)['analysis_result']['ImageConstantAnalysisResult'][
                                'PixelErrors']
                            self.settings_dict['len_median'] = len(medians)

                        break

            except KeyError as e:
                logging.error(
                    'KeyError {} happens in ImageConstant Test {}, might be no test result, regard all nan'.format(e,
                                                                                                                   file))
            finally:
                return test_dict

    def show_hist(self):
        my_config = config()
        hist = pygal.Bar(my_config)
        results = {}
        if os.path.exists(self.report_file):
            for i in range(0, self.settings_dict['len_median']):
                results[i] = analyze_excel(self.report_file).get_valid_data(i + 3)

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
            hist.render_to_file(self.report_file.split('.')[0] + '.svg')

            # get pixel error distribution
            pixel_error = analyze_excel(self.report_file).get_valid_data(i + 3 + 1)

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
            hist_pixel_error.render_to_file(self.report_file.split('.xls')[0] + 'pixel_error.svg')


class logParserImageScoring(logParser):
    def _get_data_txt(self, file: str):
        result = OrderedDict()
        result['log'] = os.path.basename(file).split('.')[0]

        with open(file) as f:
            for line in f:
                if "image quality is" in line:
                    imagescorer = line.split(" ")[3].strip()
                    imagescore = imagescorer.split()[0]
                    result['score'] = imagescore
                if "Image Scoring:" in line:
                    result['result'] = line.split(":")[1][0:8]

        return result

    def _get_data_html(self, file):
        test_patterns = OrderedDict()
        test_patterns['image_scoring_result'] = r'Test Cac Image Scoring: (.*)'
        test_patterns['score'] = r'Image Quality Score: (.*), Limit >= (.*)'

        test_dict = OrderedDict()
        with open(file, encoding='utf-8', mode='r') as f:

            test_dict['log'] = file  # os.path.basename(file).split('.')[0]

            try:
                soup = BeautifulSoup(f, 'lxml')
                text = soup.text

                test_dict['host_id'], test_dict['sensorid'] = get_host_sensor_id(text)

                for key, value in test_patterns.items():
                    res = re.findall(value, text)
                    if res:
                        if key == 'image_scoring_result':
                            test_dict[key] = 1 if res[0] == 'Pass' else 0
                        else:
                            test_dict[key] = int(res[0][0])
                            self.settings_dict['limit'] = int(res[0][1])

            except Exception as e:
                logging.error(file, sys.exc_info())
            finally:
                return test_dict

    def show_hist(self, df):
        figure = plt.figure(figsize=get_window_size())

        axes = figure.subplots(1, 1)

        hist = axes.hist(df['score'], alpha=0.5, label='image score', color=np.random.rand(3), bins=50)
        axes.plot([self.settings_dict['limit'], self.settings_dict['limit']], [0, int(max(hist[0]))], 'r--',
                  label='limit')

        axes.legend(loc='best')
        axes.set_xticks(range(0, int(df['score'].max()), 10))

        plt.savefig(self.report_file.split('.xl')[0] + '.png')
        plt.show()


class logParserDeadPixelsTxPulse(logParser):
    def _get_data_html(self, file):
        test_patterns = OrderedDict()
        test_patterns['dead_pixels_txpulse_result'] = r'Test Dead Pixel Tx Pulse: (.*)'
        test_patterns['cb_type1_median_diff'] = r'Checkerboard Type1 Median Difference btw TX on and off: (.*)'
        test_patterns['cb_type2_median_diff'] = r'Checkerboard Type2 Median Difference btw TX on and off: (.*)'
        test_patterns[
            'icb_type1_median_diff'] = r'Inverted Checkerboard Type1 Median Difference btw TX on and off: (.*)'
        test_patterns[
            'icb_type2_median_diff'] = r'Inverted Checkerboard Type2 Median Difference btw TX on and off: (.*)'

        test_dict = OrderedDict()
        with open(file, encoding='utf-8', mode='r') as f:

            test_dict['log'] = file  # os.path.basename(file).split('.')[0]
            try:
                soup = BeautifulSoup(f, 'lxml')
                text = soup.text
                test_dict['host_id'], test_dict['sensorid'] = get_host_sensor_id(text)

                for key, value in test_patterns.items():
                    res = re.findall(value, text)
                    if res:
                        if key == 'dead_pixels_txpulse_result':
                            test_dict[key] = 1 if res[0] == 'Pass' else 0
                        else:
                            test_dict[key] = abs(int(res[0]))

            except Exception as e:
                logging.error(file, sys.exc_info())
            finally:
                return test_dict

    def show_hist(self, df):
        figure = plt.figure(figsize=get_window_size())

        axes = figure.subplots(2, 2)

        axes[0, 0].hist(df['cb_type1_median_diff'], alpha=0.5, label='cb_type1_median_diff', color=np.random.rand(3),
                        bins=50)
        axes[0, 0].legend(loc='best')
        axes[0, 0].set_xticks(range(0, int(df['cb_type1_median_diff'].max()), 10))

        axes[0, 1].hist(df['cb_type2_median_diff'], alpha=0.5, label='cb_type2_median_diff', color=np.random.rand(3),
                        bins=50)
        axes[0, 1].set_xticks(range(0, int(df['cb_type2_median_diff'].max()), 10))
        axes[0, 1].legend(loc='best')

        axes[1, 0].hist(df['icb_type1_median_diff'], alpha=0.5, label='icb_type1_median_diff', color=np.random.rand(3),
                        bins=50)
        axes[1, 0].set_xticks(range(0, int(df['icb_type1_median_diff'].max()), 10))
        axes[1, 0].legend(loc='best')

        axes[1, 1].hist(df['icb_type1_median_diff'], alpha=0.5, label='icb_type2_median_diff', color=np.random.rand(3),
                        bins=50)
        axes[1, 1].set_xticks(range(0, int(df['icb_type2_median_diff'].max()), 10))
        axes[1, 1].legend(loc='best')

        plt.savefig(self.report_file.split('.xls')[0] + '.png')
        plt.show()


class logParserDefectivePixels(logParser):
    data_columns = [
        'cb_type1_min_histogram_median',
        'cb_type1_max_histogram_median',
        'cb_type1_deviation_max',
        'cb_type2_min_histogram_median',
        'cb_type2_max_histogram_median',
        'cb_type2_deviation_max',
        'cb_pixel_errors',

        'icb_type1_min_histogram_median',
        'icb_type1_max_histogram_median',
        'icb_type1_deviation_max',
        'icb_type2_min_histogram_median',
        'icb_type2_max_histogram_median',
        'icb_type2_deviation_max',
        'icb_pixel_errors',

        'swing_cb_type1_min_histogram_median',
        'swing_cb_type1_max_histogram_median',
        'swing_cb_type1_deviation_max',
        'swing_cb_type2_min_histogram_median',
        'swing_cb_type2_max_histogram_median',
        'swing_cb_type2_deviation_max',
        'swing_cb_pixel_errors',

        'swing_icb_type1_min_histogram_median',
        'swing_icb_type1_max_histogram_median',
        'swing_icb_type1_deviation_max',
        'swing_icb_type2_min_histogram_median',
        'swing_icb_type2_max_histogram_median',
        'swing_icb_type2_deviation_max',
        'swing_icb_pixel_errors',
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
                        if ('DefPixelsAnalysisDeadPixelsResult' and 'SwingingDefPixelsAnalysisDeadPixelsResult') in \
                                defective_json_settings(report)['analysis_result']:
                            for item in self.data_columns:
                                if item.startswith('cb'):
                                    test_dict[item] = defective_json_settings(report)['analysis_result'][
                                        'DefPixelsAnalysisDeadPixelsResult']['CheckerboardResult'][item[3:]]
                                elif item.startswith('icb'):
                                    test_dict[item] = \
                                        defective_json_settings(report)['analysis_result'][
                                            'DefPixelsAnalysisDeadPixelsResult']['InvertedCheckerboardResult'][item[4:]]
                                elif item.startswith('swing_cb'):
                                    test_dict[item] = \
                                        defective_json_settings(report)['analysis_result'][
                                            'SwingingDefPixelsAnalysisDeadPixelsResult']['CheckerboardResult'][item[9:]]
                                elif item.startswith('swing_icb'):
                                    test_dict[item] = \
                                        defective_json_settings(report)['analysis_result'][
                                            'SwingingDefPixelsAnalysisDeadPixelsResult']['InvertedCheckerboardResult'][
                                            item[10:]]
                        elif 'DefPixelsAnalysisDeadPixelsResult' in defective_json_settings(report)['analysis_result']:
                            for item in self.data_columns:
                                if item.startswith('cb'):
                                    test_dict[item] = defective_json_settings(report)['analysis_result'][
                                        'DefPixelsAnalysisDeadPixelsResult']['CheckerboardResult'][item[3:]]
                                elif item.startswith('icb'):
                                    test_dict[item] = \
                                        defective_json_settings(report)['analysis_result'][
                                            'DefPixelsAnalysisDeadPixelsResult']['InvertedCheckerboardResult'][item[4:]]
                        else:
                            for item in self.data_columns:
                                if item.startswith('cb'):
                                    test_dict[item] = \
                                        defective_json_settings(report)['analysis_result']['CheckerboardResult'][item[3:]]
                                elif item.startswith('icb'):
                                    test_dict[item] = \
                                        defective_json_settings(report)['analysis_result'][
                                            'InvertedCheckerboardResult'][item[4:]]
                                elif item.startswith('swing_cb'):
                                    test_dict[item] = \
                                        defective_json_settings(report)['analysis_result'][
                                            'InvertedCheckerboardResult'][item[9:]]
                                elif item.startswith('swing_icb'):
                                    test_dict[item] = \
                                        defective_json_settings(report)['analysis_result'][
                                            'InvertedCheckerboardResult'][item[10:]]

                        if 'DeadPixelsAnalysisSettings' in \
                                report['Result']['TestLog']['Steps']['measurement']['Items']['settings']['Analysis']:
                            for key, value in self.settings.items():
                                self.settings_dict[key] = \
                                    report['Result']['TestLog']['Steps']['measurement']['Items']['settings'][
                                        'Analysis']['DeadPixelsAnalysisSettings'][value]

                        break
                    elif report['Result']['TestName'] == 'TestCtlDeadPixels':
                        test_dict['dead_pixels_result'] = check_test_method_conclusion(report)
                        for i in self.data_columns[:5]:
                            test_dict[i] = defective_json_settings(report)['analysis_result']['CheckerboardResult'][i[3:]]
                            self.settings_dict[i] = report['Result']['TestLog']['Steps']['measurement'][
                                'Items']['settings']['Analysis'][self.settings[i]]

                        for i in self.data_columns[5:10]:
                            test_dict[i] = defective_json_settings(report)['analysis_result']['InvertedCheckerboardResult'][i[4:]]
                            self.settings_dict[i] = report['Result']['TestLog']['Steps']['measurement'][
                                'Items']['settings']['Analysis'][self.settings[i]]

                        break

                    elif report['Result']['TestName'] == 'TestDeadPixelsProdTestLibGradient':
                        test_dict['dead_pixels_result'] = check_test_method_conclusion(report)
                        for i in self.data_columns[:10]:
                            test_dict[i] = report['Result']['TestLog']['Steps']['analysis']['Items'][i]

                        break

                return test_dict

            except KeyError as e:
                logging.error(
                    'KeyError {} happens in CB/ICB Test {}, might be no test result, regard all nan'.format(e, file))
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
        hist1.render_to_file(self.report_file.split('.')[0] + "_type1.svg")

        hist2.title = "Type2 defective pixels distribution, limit is ({}, {})".format(value_range[2], value_range[3])
        hist2.x_title = "pixels value"
        hist2.y_title = "number of pixels"
        hist2.x_labels = range(value_range[2] - 3, value_range[3] + 3)
        hist2.render_to_file(self.report_file.split('.')[0] + "_type2.svg")

        hist3.title = "defective pixels error, limit < {}".format(value_range[4])
        hist3.x_title = "pixels errors"
        hist3.y_title = "number of errors"
        hist3.x_labels = range(0, value_range[4] + 3)
        hist3.render_to_file(self.report_file.split('.xls')[0] + "_errors.svg")


class LogParser_Current(logParser):
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
                            testData[testCase + "_Result"] = check_test_method_conclusion(test)
                            testData[testCase + "_Value"] = \
                                test['Result']['TestLog']['Steps']['measurement']['Items']['results'][
                                    'CurrentMeasurementResults'][0]['CurrentValueInMilliAmp']
                            self.settings_dict[testCase + "_LowerLimit"] = \
                                test['Result']['TestLog']['Steps']['measurement']['Items']['settings'][
                                    'MeasurementsRails'][0]['LowerLimitInMilliAmp']
                            self.settings_dict[testCase + "_UpperLimit"] = \
                                test['Result']['TestLog']['Steps']['measurement']['Items']['settings'][
                                    'MeasurementsRails'][0]['UpperLimitInMilliAmp']
        except KeyError as e:
            logging.error(
                'KeyError {} happens in Current Test {}, might be no test result, regard all nan'.format(e, file))

        return testData

    def _get_data_html(self, file):
        current_result = ['Sleep Current', 'Active Current']
        sleep_current_patterns = OrderedDict()
        sleep_current_patterns['Current at 3.3V ='] = r'Current at 3.3V = (.*)'

        test_dict = OrderedDict()
        with open(file, encoding='utf-8', mode='r') as f:

            test_dict['log'] = os.path.basename(file).split('.')[0]
            try:
                soup = BeautifulSoup(f, 'lxml')
                text = soup.text
                test_dict['Session'], test_dict['sensorid'] = get_host_sensor_id(text)
                for key, value in sleep_current_patterns.items():
                    res = re.findall(value, text)
                    if res:
                        if key == 'Current at 3.3V =':
                            test_dict[key] = 1 if res[1].strip().split(' ')[-1] == 'uA' else 0
                            if test_dict[key] == 1:
                                test_dict["Sleep " + key.split(' ')[0] + "_value"] = res[1].strip().split(' ')[0]
                                for testCase in current_result:
                                    self.settings_dict[testCase + "_LowerLimit"] = res[1].strip().split(' ')[4]
                                    self.settings_dict[testCase + "_UpperLimit"] = res[1].strip().split(' ')[6]
                        # else:
                        #     for i, val in enumerate(res[0].split(',')):
                        #         test_dict['median_' + str(i)] = int(val)

            except Exception as e:
                logging.error(file, sys.exc_info())
            finally:
                return test_dict

    def show_hist(self):
        current_type = analyze_excel(self.report_file).get_current_value_column()
        my_config = config()

        for currentType, column in current_type.items():
            result = analyze_excel(self.report_file).get_valid_data(column)
            frequencies = []
            if str(currentType).lower().find("sleep") >= 0:

                lowerlimit_sleep = round(float(self.settings_dict[currentType + "_LowerLimit"]) * 1000) - 3
                upperlimit_sleep = round(float(self.settings_dict[currentType + "_UpperLimit"]) * 1000) + 3
                unit = "[unit: uA]"

            else:
                lowerlimit_sleep = round(float(self.settings_dict[currentType + "_LowerLimit"])) - 3
                upperlimit_sleep = round(float(self.settings_dict[currentType + "_UpperLimit"])) + 3
                unit = "[unit: mA]"

            for i in range(0, len(result)):
                if result[i] < lowerlimit_sleep:
                    result[i] = lowerlimit_sleep
                elif result[i] > upperlimit_sleep:
                    result[i] = upperlimit_sleep - 1

            for value in range(lowerlimit_sleep, upperlimit_sleep):
                frequency = result.count(value)
                frequencies.append(frequency)

            hist = pygal.Bar(my_config)
            hist.add("{}".format(currentType), frequencies)
            hist.title = "{}_distribution, limit is ({}, {})".format(currentType,
                                                                     self.settings_dict[currentType + "_LowerLimit"],
                                                                     self.settings_dict[currentType + "_UpperLimit"])
            hist.x_title = "{}_Value {}".format(currentType, unit)
            hist.y_title = "number of current value"
            hist.x_labels = range(lowerlimit_sleep, upperlimit_sleep)
            hist.render_to_file(self.report_file.split(".xls")[0] + "_{}".format(currentType) + ".svg")


class LogParser_HuaweiSNR_MQT(logParser):
    def _get_data_txt(self, log: str):
        result = OrderedDict()
        result['log'] = os.path.basename(log).split('_log.')[0]

        with open(log, encoding="utf-8") as f:
            text = f.read()
            check_patterns = {'MQT': r"snr: (.*) \(limit: >=",
                              'Huawei_SNR': r"SNRUGnewresult(.*) signalnew",
                              'Huawei_Signal_Strength': r"signalnew (.*) noisenew",
                              'Huawei_Noise': r"noisenew (.*) activeArea"}
            for key, item in check_patterns.items():
                res = re.findall(item, text)
                result[key] = float(res[0]) if len(res) > 0 else np.nan

        return result

    def show_hist(self, df):
        figure = plt.figure(figsize=get_window_size())
        axes = figure.subplots(2, 2)

        df['Huawei_SNR'].dropna(inplace=True)
        df['MQT'].dropna(inplace=True)
        df['Huawei_Signal_Strength'].dropna(inplace=True)
        df['Huawei_Noise'].dropna(inplace=True)

        min_val = int(min(df['Huawei_SNR'].min(), df['MQT'].min()))
        max_val = int(max(df['Huawei_SNR'].max(), df['MQT'].max()))
        hist = axes[0, 0].hist(df['Huawei_SNR'], label='Huawei_SNR', bins=range(min_val, max_val + 1, 1),
                               color=np.random.rand(3))
        self.show_top2_hist_text(hist, axes[0, 0])
        hist = axes[0, 0].hist(df['MQT'], label='MQT', bins=range(min_val, max_val + 1, 1), alpha=0.5,
                               color=np.random.rand(3))
        self.show_top2_hist_text(hist, axes[0, 0])
        axes[0, 0].legend(loc='best')

        hist = axes[0, 1].hist(df['Huawei_Signal_Strength'], label='Huawei_Signal_Strength', color=np.random.rand(3))
        self.show_top2_hist_text(hist, axes[0, 1])
        axes[0, 1].legend(loc='best')

        hist = axes[1, 0].hist(df['Huawei_Noise'], label='Huawei_Noise', color=np.random.rand(3))
        self.show_top2_hist_text(hist, axes[1, 0])
        axes[1, 0].legend(loc='best')

        axes[1, 1].scatter(range(len(df['MQT'])), df['MQT'], label='MQT SNR', c=np.random.rand(3), s=50)
        axes[1, 1].scatter(range(len(df['Huawei_SNR'])), df['Huawei_SNR'], label='Huawei SNR', c=np.random.rand(3),
                           s=50)
        axes[1, 1].set_ylim(0)
        axes[1, 1].set_title('MQT SNR vs Huawei SNR')
        axes[1, 1].set_ylabel('SNR value')
        axes[1, 1].legend(loc='best')

        mng = plt.get_current_fig_manager()
        mng.window.state('zoomed')  # works fine on Windows!

        plt.savefig(self.report_file.split('.xls')[0] + '.png')
        plt.show()


class logParserTime(logParser):
    def _get_data_json(self, json_file):
        with open(json_file, encoding='utf-8', mode='r') as f:

            test_time_dict = OrderedDict({'Log': os.path.basename(json_file).split('_result.')[0]})
            try:
                json_dict = json.load(f)

                test_time_dict['host_id'], test_time_dict['sensorid'] = get_host_sensor_id(json_dict)

                test_time_dict['TotalTestTimeMilliseconds'] = json_dict['TotalTestTimeMilliseconds']
                for report in json_dict['TestReportItems']:
                    test_time_dict[report['Name']] = report['Result']['TestTimeMilliseconds']

            except KeyError as e:
                logging.error('KeyError {} happens in {}, might be no test result, regard all nan'.format(e, json_file))
            finally:
                return test_time_dict

    def show_hist(self, df_time):
        hosts = list(set(df_time['host_id']))
        df_list = []
        for index, host_id in enumerate(hosts):
            df_list.append(df_time[df_time['host_id'] == host_id])

        test_num = len(df_time.columns) - 2

        for index, item in enumerate(df_time.columns[2:]):
            plt.subplot(2, test_num / 2 + 1, index + 1)
            for i, df in enumerate(df_list):
                plt.hist(df[item], label='test station: ' + hosts[i], histtype='stepfilled', alpha=0.7, bins=20)
            plt.title(item)
            plt.legend(loc='best')

        mng = plt.get_current_fig_manager()
        mng.window.state('zoomed')  # works fine on Windows!

        plt.savefig(self.report_file.split('.xls')[0] + '.png')
        plt.show()


class logParserHostId(logParser):
    def __init__(self, log_path: str, report_file: str):
        super().__init__(log_path, log_pattern='*.txt', report_file=report_file)

    def _get_data_txt(self, file):
        log_data_dict = OrderedDict()
        log_data_dict['log'] = os.path.basename(file).split('_log.')[0]
        with open(file, encoding='utf-8', mode='r') as f:
            text = f.read()
            if 'Hostname' in text:
                host_name = re.findall(r':: Hostname: (.*)', text)
                log_data_dict['host_id'] = host_name[0]

        return log_data_dict


class logParserAfdCal(logParser):
    setting_data_dict = OrderedDict()

    def _get_data_json(self, file):
        test_patterns = OrderedDict()
        setting_patterns = OrderedDict()

        for i in range(5):
            for j in range(4):
                key = 'afd_cal_' + str(j) + '_' + str(i)
                pattern = r'"' + key + r'": (.*)'
                test_patterns[key] = pattern

        for i in range(5):
            for j in range(4):
                key_lower = 'afd_cal_' + str(j) + '_' + str(i) + '_lower'
                key_upper = 'afd_cal_' + str(j) + '_' + str(i) + '_upper'
                setting_patterns[key_lower] = r'"' + key_lower + r'": (.*)'
                setting_patterns[key_upper] = r'"' + key_upper + r'": (.*)'

        log_data_dict = OrderedDict()
        log_data_dict['log'] = os.path.basename(file).split('_result.')[0]

        with open(file, mode='r', encoding='utf-8') as f:
            try:
                text = f.read()
                res = re.findall(r'"Id": "(.*)"', text)
                if res:
                    log_data_dict['host_id'] = res[0]
                else:
                    log_data_dict['host_id'] = 'N/A'
                    logging.info('no host_id in {}'.format(file))

                res = re.findall(r'"SensorId": "(.*)"', text)
                if res:
                    log_data_dict['sensorid'] = res[0]
                else:
                    logging.info('no SensorId in {}'.format(file))
                    res = re.findall(r'"UniqueTestId": "(.*)"', text)
                    if res:
                        log_data_dict['sensorid'] = res[0]
                    else:
                        log_data_dict['sensorid'] = 'N/A'
                        logging.info('no UniqueTestId in {}'.format(file))

                res = re.findall(r'"TestName": "TestAfdCal",\
        "TestMethodConclusion": "(.*)"', text)
                if res:
                    log_data_dict['afd_result'] = 1 if res[0].lower().startswith('success') else 0
                else:
                    logging.info('no afd_result in {}'.format(file))

                for key, value in test_patterns.items():
                    res = re.findall(value, text)
                    if res:
                        log_data_dict[key] = float(res[0].split(',')[0])
                    else:
                        logging.info('no {} in {}'.format(key, file))

                for key, value in setting_patterns.items():
                    res = re.findall(value, text)
                    if res:
                        self.setting_data_dict[key] = float(res[0].split(',')[0])
                    else:
                        logging.info('no {} in {}'.format(key, file))

            except Exception as e:
                logging.error(file, sys.exc_info())
            finally:
                return log_data_dict

    def show_hist(self, df):
        figure = plt.figure(figsize=get_window_size())
        axes = figure.subplots(4, 5)
        for i in range(5):
            for j in range(4):
                hist = axes[j, i].hist(df[df.columns[j + 4 * i + 4]],
                                       bins=20,
                                       alpha=0.5,
                                       label=df.columns[j + 4 * i + 4],
                                       color=np.random.rand(3))

                limit_upper = self.setting_data_dict[df.columns[j + 4 * i + 4] + '_upper']
                limit_lower = self.setting_data_dict[df.columns[j + 4 * i + 4] + '_lower']
                axes[j, i].plot([limit_upper, limit_upper], [0, int(max(hist[0]))], 'r--', label='limit')
                axes[j, i].plot([limit_lower, limit_lower], [0, int(max(hist[0]))], 'r--')
                axes[j, i].legend(loc='best')

                axes[j, i].set_xticks([int(limit_lower),
                                       int(df[df.columns[j + 4 * i + 4]].min()),
                                       # int(df[df.columns[j + 4 * i + 1]].median()),
                                       int(df[df.columns[j + 4 * i + 4]].max()),
                                       int(limit_upper)])

        plt.savefig(self.report_file.split('.xls')[0] + '.png')
        plt.show()


class logParserLensCurrentTest(logParser):
    def _get_data_json(self, json_file):
        with open(json_file, encoding='utf-8', mode='r') as f:
            test_data = OrderedDict()
            test_data['log'] = os.path.basename(json_file).split('_result.')[0]
            try:
                json_dict = json.load(f)
                test_data['host_id'], test_data['sensorid'] = get_host_sensor_id(json_dict)

                for item in json_dict['TestReportItems']:
                    if item['Name'] == 'Sleep Current Test':
                        test_data['Sleep_result'] = check_test_method_conclusion(item)
                        if test_data['Sleep_result'] == 1:
                            test_data['SleepCurrent_Value'] = \
                                item['Result']['TestLog']['Steps']['measurement']['Items']['results']['currentValue']
                        else:
                            test_data['Sleep_result'] = 0
                            test_data['SleepCurrent_Value'] = -1

                    elif item['Name'] == 'Active Current Test':
                        test_data['Active_result'] = check_test_method_conclusion(item)
                        if test_data['Active_result'] == 1:
                            test_data['ActuveCurrent_Value'] = \
                                item['Result']['TestLog']['Steps']['measurement']['Items']['results']['currentValue']
                        else:
                            test_data['Active_result'] = 0
                            test_data['ActuveCurrent_Value'] = -1


            except KeyError as e:
                logging.error('KeyError {} happens in {}, might be no test result, regard all nan'.format(e, json_file))
            finally:
                return test_data


#################################################yield report###########################################################
class logParserYieldReport(logParser):
    def analyze(self):
        results = list(self.yield_results())
        if len(results) == 0:
            logging.error('No test data, are you setting correct path ?')
            exit(-1)

        self.df = pd.DataFrame(results, dtype=float)
        self.get_general_yield()
        self.get_unique_sensor_yield()

    def _get_data_html(self, file):
        test_patterns = OrderedDict()
        test_patterns['sensorid'] = r'Sensor ID: (.*)'
        test_patterns['result'] = r'Test Result: (.*)'
        test_patterns['HardwareID'] = r'TestHwId: (.*)'
        test_patterns['Irq'] = r'Test IRQ: (.*)'
        test_patterns['afd_cal'] = r'Test Afd Cal: (.*)'
        test_patterns['defective_pixels'] = r'Test Ctl Defective Pixels: (.*)'
        test_patterns['MQT'] = r'Module Quality Test: (.*)'
        test_patterns['write_module_otp'] = r'Test Write Module OTP : (.*)'
        test_patterns['read_otp'] = r'Test OTP Read: (.*)'

        log_data_dict = OrderedDict()
        log_data_dict['log'] = os.path.basename(file).split('.')[0]
        log_data_dict['host_id'] = 'N/A'

        with open(file, mode='r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'lxml')
            try:
                text = soup.text
                for key, value in test_patterns.items():
                    res = re.findall(value, text)
                    if res:
                        if key == 'sensorid':
                            log_data_dict[key] = res[0]
                        else:
                            log_data_dict[key] = 1 if res[0].lower() == 'pass' else 0
                    else:
                        logging.info('no {} in {}'.format(key, file))

            except Exception as e:
                logging.error(file, sys.exc_info())
            finally:
                return log_data_dict

    def _get_data_txt(self, file):
        log_data_dict = OrderedDict()
        log_data_dict['log'] = os.path.basename(file).split('.')[0]
        log_data_dict['host_id'] = 'N/A'

        with open(file, mode='r', encoding='utf-8') as f:
            for line in f:
                if 'Unique Module ID' in line:
                    log_data_dict['sensorid'] = line.split('Unique Module ID:')[1].strip()
                if 'SNR(dB):' in line:
                    log_data_dict['MQT'] = line.split("SNR(dB):")[1].strip()
                if 'Test Tsnr is' in line:
                    log_data_dict['Tsnr'] = line.split("Test Tsnr is")[1].strip()

        return log_data_dict

    def _get_data_json(self, file):

        test_dict = OrderedDict()
        test_dict['log'] = os.path.basename(file).split('_result.')[0]
        test_dict['host_id'] = 'N/A'
        test_dict['sensorid'] = 'N/A'

        with open(file, encoding='utf-8', mode='r') as f:
            try:
                json_dict = json.load(f)

                test_dict['host_id'], test_dict['sensorid'] = get_host_sensor_id(json_dict)
                test_dict['result'] = 1 if json_dict['Success'] == 'Success' else 0

                for _, item in enumerate(json_dict['TestReportItems']):
                    test_dict[item['Name'].lower()] = check_test_method_conclusion(item)

            except KeyError as e:
                logging.error('KeyError {} happens in {}, no test result'.format(e, file))
            finally:
                return test_dict

    def _get_data_json_primax(self, file):

        test_dict = OrderedDict()
        test_dict['log'] = os.path.basename(file).split('_result.')[0]
        test_dict['host_id'] = 'N/A'
        test_dict['sensorid'] = 'N/A'

        with open(file, encoding='utf-8', mode='r') as f:
            try:
                json_dict = json.load(f)

                if ('sensor_id' in json_dict['device']):
                    test_dict['sensorid'] = json_dict['device']['sensor_id']

                test_dict['result'] = 1 if json_dict['conclusion'] == 'pass' else 0

                for _, item in enumerate(json_dict['sequence']):
                    test_dict[item['name'].lower()] = check_test_method_conclusion_primax(item)

            except KeyError as e:
                logging.error('KeyError {} happens in {}, no test result'.format(e, file))
            finally:
                return test_dict
