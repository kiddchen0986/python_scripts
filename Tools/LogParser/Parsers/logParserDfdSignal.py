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
                logging.error('KeyError {} happens in {} {}, might be no test result, regard all nan'.format(e, self.__class__.__name__, json_file))
            finally:
                return test_data
