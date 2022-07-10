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
import operator
from Parsers.LogParser import *


@typeassert(log_path=str, log_pattern=str, report_file=str)
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
                logging.error('KeyError {} happens in {} {}, might be no test result, regard all nan'.format(e, self.__class__.__name__, file))
            except Exception as e:
                print("{}::{} Exception:".format(self.__class__.__name__, sys._getframe().f_code.co_name))
                print(e)
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
