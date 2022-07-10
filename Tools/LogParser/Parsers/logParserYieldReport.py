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
import sys
from Parsers.LogParser import *


#################################################yield report###########################################################
@typeassert(log_path=str, log_pattern=str, report_file=str)
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
                if 'Success' in json_dict:
                    test_dict['result'] = 'Pass' if json_dict['Success'] == 'Success' else 'Fail'
                else:
                    test_dict['result'] = 'Pass' if json_dict['TestReportConclusion'] == 'Success' else 'Fail'
                test_dict['tool_ver'] = json_dict['ProgramInfo']['Version']
                test_dict['TestStartTime'] = json_dict['TestStartTime']
                for _, item in enumerate(json_dict['TestReportItems']):
                    test_dict[item['Name'].lower()] = check_test_method_conclusion(item)

            except KeyError as e:
                logging.error('KeyError {} happens in {} {}, might be no test result, regard all nan'.format(e, self.__class__.__name__, file))
            except Exception as e:
                print("{}::{} Exception:".format(self.__class__.__name__, sys._getframe().f_code.co_name))
                print(e)
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

                if 'sensor_id' in json_dict['device']:
                    test_dict['sensorid'] = json_dict['device']['sensor_id']

                test_dict['result'] = 1 if json_dict['conclusion'] == 'pass' else 0

                for _, item in enumerate(json_dict['sequence']):
                    test_dict[item['name'].lower()] = check_test_method_conclusion_primax(item)

            except KeyError as e:
                logging.error('KeyError {} happens in {} {}, might be no test result, regard all nan'.format(e, self.__class__.__name__, file))
            finally:
                return test_dict
