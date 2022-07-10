import sys
from LogParser import logParserMqt


if __name__ == "__main__":
    try:
        parser = logParserMqt(sys.argv[1], '*.json', sys.argv[2], 1)

        # copy fmi within limits to a specific folder
        parser.limits = (15, 17)
        parser.fmi_folder = r'C:\project\C1\FPC1075_log_primax-0705\2747\Log\MQTtestlog\15-17'

        parser.analyze()

    except IndexError as e:
        print("python analyze_mqt.py <log_path> <report_file_name>")
    except Exception as e:
        print("Error {} caught in script".format(e))