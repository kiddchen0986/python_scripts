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

        plt.savefig(os.path.splitext(self.report_file)[0] + '.png')
        plt.show()
