from LogParser import logParserCtlImageConstant
import sys

if __name__ == "__main__":
    try:
        path = r'D:\Logs\xiaomi\1291\ofilm\20180419\1007-00-MT'
        path_xls = r'1291_e1_image_constant.xls'
        logParserCtlImageConstant(path, '*.json', path_xls).analyze()

    except Exception as e:
        print("Error {} caught in script".format(sys.exc_info()))



