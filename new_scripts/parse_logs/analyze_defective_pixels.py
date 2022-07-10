from LogParser import logParserDefectivePixels
import sys

path = r'D:\Logs\Huawei\Lens\1261\FT2D45PJ'

if __name__ == "__main__":
    try:
        logParserDefectivePixels(path, report_file='defective_pixel.xls').analyze()

    except Exception as e:
        print("Error {} caught in script".format(sys.exc_info()))