# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#
from LogParser import logParserLensCurrentTest

if __name__== '__main__':
    path = r'C:\Jira\CET-468'
    path_xls = r'C:\Jira\CET-468\lens_current_analysis.xls'

    logParserLensCurrentTest(path, '*.json', path_xls).analyze()
