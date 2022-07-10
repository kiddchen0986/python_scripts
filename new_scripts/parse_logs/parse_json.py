# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#

import sys
from LogParser import logParserYieldReport

if __name__ == "__main__":
    try:
        # third parameter means if the json logs from primax, 1 means yes
        logParserYieldReport(sys.argv[1], '*.json', sys.argv[2]).analyze()

    except IndexError as e:
        print("python parse_json.py <log_path> <csv_file_name>, error".format(e))
    except Exception as e:
        print("Error {} caught in script".format(sys.exc_info()))
