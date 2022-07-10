import os
import xlrd, xlwt, xlutils
from xlutils.copy import copy as xl_copy
import pygal

print("Here set test limits as 15")
print("Please check if you need to change the limits before running this script!")
filepath = "D:\\LogAnalyze\\VIVO1903-8\\1511-S_80um_mqt.xls"


def get_valid_data(filepath, sheetname):
    rb = xlrd.open_workbook(filepath)
    sheet = rb.sheet_by_name(sheetname)
    nrows = sheet.nrows

    results = []
    for i in range(1, nrows - 2):
        result = int(sheet.cell_value(i, 4))
        results.append(result)
    results.sort()

    return results


def get_snr_frequency(filepath, sheetname):
    frequencies = []
    results = get_valid_data(filepath, sheetname)
    for value in range(0, 35):
        frequency = results.count(value)
        frequencies.append(frequency)

    return frequencies


snr_frequencies = get_snr_frequency(filepath, "Sheet2")

hist = pygal.Bar()
hist.title = "snr distribution"
hist.x_title = "snr value"
hist.y_title = "number of snr"
hist.x_labels = range(0, 35)
hist.add('snr', snr_frequencies)
hist.render_to_file(os.path.dirname(filepath) + "\\snr.svg")