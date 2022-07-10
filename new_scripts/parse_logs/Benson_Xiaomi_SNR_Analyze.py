import os
import xlrd
import xlwt
from xlutils.copy import copy
import sys
from collections import OrderedDict
from bs4 import BeautifulSoup
import re
import logging


class parse_html:
    def __init__(self, path):
        self.path = path

    def parse_wafer_data(self, data):
        wafer_lot_ID = data[4:10]
        ID = data[-2:]
        X = data[10:12]
        Y = data[12:14]
        return [wafer_lot_ID, ID, (X, Y)]

    def get_data_html(self, filename):

        test_patterns = OrderedDict()
        test_patterns['sensorid'] = r'Sensor ID: (.*)'
        test_patterns['LOT ID'] = r'LOT ID: (.*)'
        test_patterns['X'] = r'X Coordinate: (.*)'
        test_patterns['Y'] = r'Y Coordinate = (.*)'
        test_patterns['ID'] = r'ID: (.*)'

        test_patterns['CB Number of dead pixels'] = r'Number of dead pixels: (.*)'
        test_patterns['ICB Number of dead pixels'] = r'Number of dead pixels: (.*)'
        test_patterns['image constant Number of dead pixels'] = r'Number of image constant pixel errors: (.*)'
        test_patterns['Number of defective pixels'] = r'Number of defective pixels: (.*)'
        test_patterns['SNR'] = r'SNR\(dB\): (.*)'

        log_data_dict = OrderedDict()

        log_data_dict['log'] = os.path.basename(filename).split('.')[0]

        with open(os.path.join(self.path, filename), mode='r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'lxml')
            try:
                text = soup.text
                for key, value in test_patterns.items():
                    res = re.findall(value, text)
                    if res:
                        if key == 'sensorid':
                            log_data_dict[key] = res[0]
                        elif key == 'LOT ID':
                            log_data_dict[key] = res[0]
                        elif key == 'X':
                            log_data_dict[key] = res[0]
                        elif key == 'Y':
                            log_data_dict[key] = res[0]
                        elif key == 'ID':
                            log_data_dict[key] = res[4]
                        elif key == 'SNR':
                            log_data_dict[key] = res[0]
                        else:
                            if key == 'CB Number of dead pixels':
                                log_data_dict[key] = res[0][0]
                            elif key == 'ICB Number of dead pixels':
                                log_data_dict[key] = res[1][0]
                            elif key == 'image constant Number of dead pixels':
                                log_data_dict[key] = res[0][0]
                            elif key == 'Number of defective pixels':
                                log_data_dict[key] = res[0][0]
                    else:
                        logging.info('no {} in {}'.format(key, self.file))

            except Exception as e:
                logging.error(self.file, sys.exc_info())
            finally:
                return log_data_dict

    def parse_html_data(self):
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('worksheet')

        files = os.listdir(self.path)
        i = 0
        for filename in files:
            portion = os.path.splitext(filename)
            if portion[1] == '.html':
                results = self.get_data_html(filename)

                j = 0
                for key, value in results.items():
                    if i == 0:
                        worksheet.write(0, j, key)
                    worksheet.write(i+1, j, value)
                    j = j + 1
                i = i + 1

        workbook.save(os.path.join(self.path, "1511_G175.xls"))


if __name__ == "__main__":
    try:
        files = []
        path = input("Enter into your log path:")
        parse_html(path).parse_html_data()

    except Exception as e:
        print("Error {} caught in script".format(sys.exc_info()))