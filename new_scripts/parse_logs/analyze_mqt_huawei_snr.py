#https://fpc-jira.fingerprint.local/jira/browse/CET-9
#Analyze MQT and Huawei SNR test

import sys
from LogParser import logParserHuaweiSnrMqt


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("python analyze_mqt_huawei_snr.py <log_path> <report_file_name>")
        sys.exit(1)

    logParserHuaweiSnrMqt(sys.argv[1], '*_log.txt', sys.argv[2]).analyze()
