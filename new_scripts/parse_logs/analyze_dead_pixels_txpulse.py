from LogParser import logParserDeadPixelsTxPulse
import sys

path = r'D:\Logs\OPPO\Ofilm\1228\20180605'

if __name__ == "__main__":
    try:
        logParserDeadPixelsTxPulse(path, log_pattern=r'*.html', report_file='dead_pixel_tx.xls').analyze()

    except Exception as e:
        print("Error {} caught in script".format(sys.exc_info()))