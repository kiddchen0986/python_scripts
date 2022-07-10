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
class logParserOtpInfo(logParser):
    def _get_data_txt(self, file):
        otp_info = OrderedDict()
        otp_info['log'] = os.path.basename(file).split('_log.')[0]
        with open(file, encoding='utf-8', mode='r') as f:
            try:
                text = f.read()
                otp_info['host_id'], otp_info['sensorid'] = get_host_sensor_id(text)

                res = re.findall(r'Test started: (.*)', text)
                if res:
                    otp_info['test_time'] = res[0]

                res = re.findall(r'User: (.*)', text)
                if res:
                    otp_info['user'] = res[0]

                if r'-> Test Write Otp' in text:
                    otp_info['sequence'] = 'write_otp'
                    if r'Amount of vendor bytes specified' in text or r'Vendor data size mismatch!' in text:
                        otp_info['module_vendor_otp_size_mismatch'] = 'true'
                    else:
                        otp_info['module_vendor_otp_size_mismatch'] = 'false'
                else:
                    otp_info['sequence'] = 'default'

                total_err_bit = re.findall(r'Total Bit Errors: (.*)', text)
                total_err_byte = re.findall(r'Bit error found in byte (.*)', text)
                max_err_bit = re.findall(r'Max Bit Errors in one byte: (.*)', text)
                date = re.findall(r'Date: (.*)', text)
                module_version = re.findall(r'MODULE SECTION: Version Version(.*)', text)
                wafer_version = re.findall(r'WAFER SECTION: Version Version(.*)', text)

                if total_err_bit:
                    otp_info['total_bit_errors'] = int(total_err_bit[0])
                else:
                    otp_info['total_bit_errors'] = 0
                if total_err_byte:
                    otp_info['total_byte_errors'] = len(total_err_byte)
                else:
                    otp_info['total_byte_errors'] = 0
                if max_err_bit:
                    otp_info['max_bit_err_in_one_byte'] = int(max_err_bit[0])
                else:
                    otp_info['max_bit_err_in_one_byte'] = 0

                if module_version:
                    otp_info['module_version'] = int(module_version[0])
                else:
                    otp_info['module_version'] = 0

                if wafer_version:
                    otp_info['wafer_version'] = int(wafer_version[0])
                else:
                    otp_info['wafer_version'] = 0

                if date:
                    if len(date) >= 2:
                        otp_info['wafer_production_date'] = date[0]
                        if r'MODULE SECTION: Version' in text:
                            otp_info['module_production_date'] = date[1]
                    elif len(date) == 1:
                        otp_info['wafer_production_date'] = date[0]

            except KeyError as e:
                logging.error('KeyError {} happens in {} {}, might be no test result, regard all nan'.format(e, self.__class__.__name__, file))
            except Exception as e:
                print("{}::{} Exception:".format(self.__class__.__name__, sys._getframe().f_code.co_name))
                print(e)
            finally:
                return otp_info
