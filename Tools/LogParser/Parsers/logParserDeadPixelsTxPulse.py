# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#

import matplotlib.pyplot as plt
from Parsers.util import get_window_size
from bs4 import BeautifulSoup
import sys
from Parsers.LogParser import *


@typeassert(log_path=str, log_pattern=str, report_file=str)
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

        plt.savefig(os.path.splitext(self.report_file)[0] + '.png')
        plt.show()
