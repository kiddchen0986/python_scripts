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
from Parsers.LogParser import *
from Parsers.analyze_excel_data import analyze_excel

@typeassert(log_path=str, log_pattern=str, report_file=str)
class LogParserHuaweiSNR(logParser):
    def _get_data_json(self, file):
        with open(file, encoding='utf-8', mode='r') as f:
            test_data = OrderedDict()
            test_data['log'] = os.path.basename(file).split('_result.')[0]
            try:
                json_dict = json.load(f)
                test_data['host_id'], test_data['sensorid'] = get_host_sensor_id(json_dict)
                for item in json_dict['TestReportItems']:
                    if 'TestHuaweiSNRWhiteZebra' in item['Result']['TestName']:
                        test_data['HuaWei_MQT'] = check_test_method_conclusion(item)
                        test_data['Huawei_SNR'] = item['Result']['TestLog']['Steps']['measurement']['Items']['SNR']
                        test_data['Huawei_Signal_Strength'] = item['Result']['TestLog']['Steps']['measurement']['Items']['Signal']
                        test_data['Huawei_Noise'] = item['Result']['TestLog']['Steps']['measurement']['Items']['Noise']

            except KeyError as e:
                logging.error('KeyError {} happens in {} {}, might be no test result, regard all nan'.format(e, self.__class__.__name__, file))
            except Exception as e:
                print("{}::{} Exception:".format(self.__class__.__name__, sys._getframe().f_code.co_name))
                print(e)

            finally:
                return test_data


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

    def show_hist(self):
        frequencies = []
        if os.path.exists(self.report_file):
            results = analyze_excel(self.report_file).get_valid_data_by_key('Huawei_SNR')
        else:
            return

        for value in range(0, max(results) + 1):
            frequency = results.count(value)
            frequencies.append(frequency)
        hist = pygal.Bar()
        hist.title = "snr distribution"
        hist.x_title = "snr value"
        hist.y_title = "number of snr"
        hist.x_labels = range(0, max(results) + 1)
        hist.add("snr", frequencies)
        try:
            hist.render_to_file(os.path.splitext(self.report_file)[0] + '.svg')
        except Exception as e:
            print("{}::{} Exception:".format(self.__class__.__name__, sys._getframe().f_code.co_name))
            print(e)
