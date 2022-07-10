import os
import xlrd, xlwt, xlutils
from xlutils.copy import copy as xl_copy
import pygal
from pygal.style import LightColorizedStyle as LCS, LightenStyle as LS

print("Here set type1 test limits as (185, 232), and type2 test limits (115,139)")
print("Please check if you need to change the limits before running this script!")
filepath = "D:\\LogAnalyze\\XG7B-2\\1541-S_defective_pixels.xls"


def get_valid_data(filepath, sheetname, column):
    rb = xlrd.open_workbook(filepath)
    sheet = rb.sheet_by_name(sheetname)
    nrows = sheet.nrows

    results = []
    for i in range(1, nrows):
        if len(str(sheet.cell_value(i, column))) != 0:
            result = int(sheet.cell_value(i, column))
            results.append(result)
    results.sort()

    return results


def get_type1_frequency(filepath, sheetname, column):
    frequencies = []
    results = get_valid_data(filepath, sheetname, column)

    for i in range(0, len(results)):
        if results[i] <= 182:
            results[i] = 182
        elif results[i] >= 235:
            results[i] = 235

    for value in range(182, 235):
        frequency = results.count(value)
        frequencies.append(frequency)

    return frequencies


def get_type2_frequency(filepath, sheetname, column):
    frequencies = []
    results = get_valid_data(filepath, sheetname, column)

    for i in range(0, len(results)):
        if results[i] <= 111:
            results[i] = 111
        elif results[i] >= 143:
            results[i] = 143

    for value in range(111, 143):
        frequency = results.count(value)
        frequencies.append(frequency)

    return frequencies


cb_type1_min_frequencies = get_type1_frequency(filepath, "Sheet1", 4)
cb_type1_max_frequencies = get_type1_frequency(filepath, "Sheet1", 5)
icb_type1_min_frequencies = get_type1_frequency(filepath, "Sheet1", 11)
icb_type1_max_frequencies = get_type1_frequency(filepath, "Sheet1", 12)

cb_type2_min_frequencies = get_type2_frequency(filepath, "Sheet1", 7)
cb_type2_max_frequencies = get_type2_frequency(filepath, "Sheet1", 8)
icb_type2_min_frequencies = get_type2_frequency(filepath, "Sheet1", 14)
icb_type2_max_frequencies = get_type2_frequency(filepath, "Sheet1", 15)

my_config = pygal.Config()
my_config.x_label_rotation = 45
my_config.show_legend = True
my_config.title_font_size = 24
my_config.label_font_size = 14
my_config.major_label_font_size = 18
my_config.truncate_label = 15
my_config.show_y_guides = 15
my_config.width = 1100

hist_type1 = pygal.Bar(my_config)
hist_type1.title = "Type1 defective pixels distribution of 1541-S"
hist_type1.x_title = "pixels value"
hist_type1.y_title = "number of pixels"
hist_type1.x_labels = range(182, 235)
hist_type1.add('cb_type1_min_histogram_median', cb_type1_min_frequencies)
hist_type1.add('cb_type1_max_histogram_median', cb_type1_max_frequencies)
hist_type1.add('icb_type1_min_histogram_median', icb_type1_min_frequencies)
hist_type1.add('icb_type1_max_histogram_median', icb_type1_max_frequencies)
hist_type1.render_to_file(os.path.dirname(filepath) + "\\Type1_defective_pixels_distribution.svg")

hist_type2 = pygal.Bar(my_config)
hist_type2.title = "Type2 defective pixels distribution of 1541-S"
hist_type2.x_title = "pixels value"
hist_type2.y_title = "number of pixels"
hist_type2.x_labels = range(111, 143)
hist_type2.add('cb_type2_min_histogram_median', cb_type2_min_frequencies)
hist_type2.add('cb_type2_max_histogram_median', cb_type2_max_frequencies)
hist_type2.add('icb_type2_min_histogram_median', icb_type2_min_frequencies)
hist_type2.add('icb_type2_max_histogram_median', icb_type2_max_frequencies)
hist_type2.render_to_file(os.path.dirname(filepath) + "\\Type2_defective_pixels_distribution.svg")
