from LogParser import logParserImageScoring
import sys
import os

Getpath = input("Please enter log path:")
os.chdir(Getpath)
cwd = os.getcwd()
print("Changed current directory is: ", cwd)

if __name__ == "__main__":
    try:
        logParserImageScoring(cwd, log_pattern=r'*.txt', report_file='image_scoring.xls').analyze()

    except Exception as e:
        print("Error {} caught in script".format(sys.exc_info()))