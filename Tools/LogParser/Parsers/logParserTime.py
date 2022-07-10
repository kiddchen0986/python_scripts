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
from Parsers.LogParser import *


@typeassert(log_path=str, log_pattern=str, report_file=str)
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
                logging.error('KeyError {} happens in {} {}, might be no test result, regard all nan'.format(e, self.__class__.__name__, json_file))
            except Exception as e:
                print("{}::{} Exception:".format(self.__class__.__name__, sys._getframe().f_code.co_name))
                print(e)
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

        plt.savefig(os.path.splitext(self.report_file)[0] + '.png')
        plt.show()
