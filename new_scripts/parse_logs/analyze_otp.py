# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#
from LogParser import logParserReadOtp

if __name__== '__main__':
    path = r'C:\OTP'
    path_xls = r'C:\OTP\otp_analysis.xls'

    #logParserOtpInfo(path, '*.txt', path_xls).analyze()
    logParserReadOtp(path, '*.json', path_xls).analyze()