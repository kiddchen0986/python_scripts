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


@typeassert(log_path=str, log_pattern=str, report_file=str)
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
                logging.error('KeyError {} happens in {} {}, might be no test result, regard all nan'.format(e, self.__class__.__name__, json_file))
            except Exception as e:
                print("{}::{} Exception:".format(self.__class__.__name__, sys._getframe().f_code.co_name))
                print(e)
            finally:
                return test_data
