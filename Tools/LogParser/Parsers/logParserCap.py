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
import matplotlib.pyplot as plt
from Parsers.util import get_window_size
from bs4 import BeautifulSoup
from Parsers.json_settings import parse_json_settings
import sys
from Parsers.LogParser import *


@typeassert(log_path=str, log_pattern=str, report_file=str)
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
                            parse_json_settings(item)['analysis_result']['UniformityLevel'])
                        test_data['signal_strength'] = float(
                            parse_json_settings(item)['analysis_result']['SignalStrength'])
                        test_data['number_of_blob_pixels'] = float(
                            parse_json_settings(item)['analysis_result']['BlobCount'])

                        break

            except KeyError as e:
                logging.error('KeyError {} happens in {} {}, might be no test result, regard all nan'.format(e, self.__class__.__name__, json_file))
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
        try:
            plt.savefig(os.path.splitext(self.report_file)[0] + '.png')
            plt.show()
        except Exception as e:
            print("{}::{} Exception:".format(self.__class__.__name__, sys._getframe().f_code.co_name))
            print(e)

        return df
