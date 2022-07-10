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
class logParserHostId(logParser):

    def __init__(self, log_path: str, report_file: str):
        super().__init__(log_path, log_pattern='*.txt', report_file=report_file)

    def _get_data_txt(self, file):
        log_data_dict = OrderedDict()
        log_data_dict['log'] = os.path.basename(file).split('_log.')[0]
        with open(file, encoding='utf-8', mode='r') as f:
            text = f.read()
            if 'Hostname' in text:
                host_name = re.findall(r':: Hostname: (.*)', text)
                log_data_dict['host_id'] = host_name[0]

        return log_data_dict
