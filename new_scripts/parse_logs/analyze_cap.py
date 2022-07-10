#Analyze Cap test
import sys
from LogParser import logParserCap


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("python analyze_cap.py <log_path> <report_file_name>")
        sys.exit(1)

    parser = logParserCap(sys.argv[1], '*.json', sys.argv[2]).analyze()
