from LogParser import logParserTime

import sys

if __name__ == "__main__":
    try:
        logParserTime(sys.argv[1], sys.argv[2]).analyze()

    except IndexError as e:
        print("python analyze_execution_time.py <log_path> <report_file_name> ")
    except Exception as e:
        print("Error {} caught in script".format(sys.exc_info()))
