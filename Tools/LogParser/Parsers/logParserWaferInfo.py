# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#

from Parsers.LogParser import *


@typeassert(log_path=str, log_pattern=str, report_file=str)
class logParserWaferInfo(logParser):

    def __init__(self, log_path: str, report_file: str = ''):
        super().__init__(log_path, report_file=report_file, log_pattern='*.txt')

    def _get_data_txt(self, file):
        otp_info = OrderedDict()
        otp_info['log'] = os.path.basename(file).split('_log.')[0]
        with open(file, encoding='utf-8', mode='r') as f:
            text = f.read()
            otp_info['host_id'], otp_info['sensorid'] = get_host_sensor_id(text)
            if '-> Test Read OTP (TestReadOtp)' in text:
                lot_id = re.findall(r'LOT ID: (.*)', text)
                x_id = re.findall(r'X Coordinate: (.*)', text)
                y_id = re.findall(r'Y Coordinate = (.*)', text)
                id_id = re.findall(r'\nID: (.*)', text)

                otp_info['lot_id'] = lot_id[0]
                otp_info['x_id'] = x_id[0]
                otp_info['y_id'] = y_id[0]
                otp_info['id'] = id_id[0]

            return otp_info
