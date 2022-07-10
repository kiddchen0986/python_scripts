import os
import xlrd, xlwt, xlutils
from xlutils.copy import copy as xl_copy
import pygal


class analyze_excel:
    def __init__(self, file):
        self.file = file

    def get_current_value_column(self):  # get column number from current test result
        rb = xlrd.open_workbook(self.file)
        sheet = rb.sheet_by_name('Sheet1')
        cell = {}

        for i in range(0, sheet.ncols):
            if ((str(sheet.cell_value(0, i)).lower().find("sleep") >= 0) or (
                    str(sheet.cell_value(0, i)).lower().find("active") >= 0)) and (
                    str(sheet.cell_value(0, i)).lower().find("value") >= 0):
                cell[sheet.cell_value(0, i).split("_")[0]] = i

        return cell

    def get_defective_pixels_column(self):  # get column number from defective pixels test result
        rb = xlrd.open_workbook(self.file)
        sheet = rb.sheet_by_name('Sheet1')
        cell = {}

        column_settings = ['cb_type1_min_histogram_median',
                           'cb_type1_max_histogram_median',
                           'cb_type2_min_histogram_median',
                           'cb_type2_max_histogram_median',
                           'cb_pixel_errors',
                           'icb_type1_min_histogram_median',
                           'icb_type1_max_histogram_median',
                           'icb_type2_min_histogram_median',
                           'icb_type2_max_histogram_median',
                           'icb_pixel_errors', ]

        for i in range(4, sheet.ncols):
            for column in column_settings:
                if str(sheet.cell_value(0, i)) != column:
                    continue
                cell[column] = i

        return cell


    def get_valid_data(self, column):
        rb = xlrd.open_workbook(self.file)
        sheet = rb.sheet_by_name('Sheet1')
        nrows = sheet.nrows
        test_data = {}
        results = []

        for i in range(1, nrows):
            if len(str(sheet.cell_value(i, column))) != 0:
                if str(sheet.cell_value(0, column)).lower().find("sleep") >= 0:
                    if float(sheet.cell_value(i, column))< 0.1:
                        result = round(float(sheet.cell_value(i, column)) * 1000)
                    else:
                        result = round(float(sheet.cell_value(i, column)))

                else:
                    result = round(sheet.cell_value(i, column))

                if len(str(sheet.cell_value(i, 2))) != 0:  # check if column of sensor ID is null
                    test_data = self.get_highest_value(test_data, result, sheet, i)  # get highest value with same sensor ID
                else:
                    results.append(result)

        for k, v in test_data.items():
            results.append(v)
        results.sort()

        return results

    def get_highest_value(self, test_data, result, sheet, row):
        for key, value in test_data.items():
            if key == str(sheet.cell_value(row, 2)).strip():
                result = max(value, result)
        test_data[sheet.cell_value(row, 2)] = result

        return test_data
