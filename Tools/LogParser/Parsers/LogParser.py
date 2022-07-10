# -*- coding: utf-8 -*-
#
# Copyright (c) 2018-2021 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#

from collections import OrderedDict
import pandas as pd
from matplotlib import style
from Parsers.util import gen_find
from Parsers.util import typeassert
import re
import numpy as np
import os
import logging
import pygal


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
        return 'Pass'
    elif item['Result']['TestMethodConclusion'] == 'Fail' or item['Result']['TestMethodConclusion'] == 'Exception':
        return 'Fail'
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
        Save the data frame to csv, excel, html, if have data (column count > 3), called by self.analyze
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
