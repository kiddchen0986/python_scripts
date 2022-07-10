import os
import xlrd, xlwt, xlutils
from xlutils.copy import copy as xl_copy
import pygal
from pygal.style import LightColorizedStyle as LCS, LightenStyle as LS

print("Here set test limits as 181, 226")
print("Please check if you need to change the limits before running this script!")
file = "D:\\LogAnalyze\\XG7B-2\\1541-S_image_constant.xls"


def get_valid_data(file, sheetname, column):
    rb = xlrd.open_workbook(file)
    sheet = rb.sheet_by_name(sheetname)
    nrows = sheet.nrows
    results = []

    for i in range(1, nrows):
        if len(str(sheet.cell_value(i, column))) != 0:
            result = int(sheet.cell_value(i, column))
            results.append(result)
    results.sort()
    return results


def get_frequency(file, sheetname, column):
    frequencies = []
    results = get_valid_data(file, sheetname, column)

    for i in range(0, len(results)):
        if results[i] <= 179:
            results[i] = 179
        elif results[i] >= 229:
            results[i] = 229

    for num in range(179, 230):
        frequency = results.count(num)
        frequencies.append(frequency)

    return frequencies


image_constant__1_frequencies = get_frequency(file, "Sheet1", 3)
image_constant__2_frequencies = get_frequency(file, "Sheet1", 4)
image_constant__3_frequencies = get_frequency(file, "Sheet1", 5)
image_constant__4_frequencies = get_frequency(file, "Sheet1", 6)
image_constant__5_frequencies = get_frequency(file, "Sheet1", 7)
image_constant__6_frequencies = get_frequency(file, "Sheet1", 8)
image_constant__7_frequencies = get_frequency(file, "Sheet1", 9)
image_constant__8_frequencies = get_frequency(file, "Sheet1", 10)
image_constant__9_frequencies = get_frequency(file, "Sheet1", 11)
image_constant__10_frequencies = get_frequency(file, "Sheet1", 12)

# my_style = LS('#333366', base_style=LCS)
my_config = pygal.Config()
my_config.x_label_rotation = 45
my_config.show_legend = True
my_config.title_font_size = 24
my_config.label_font_size = 14
my_config.major_label_font_size = 18
my_config.truncate_label = 15
my_config.show_y_guides = 15
my_config.width = 1200

hist = pygal.Bar(my_config)
hist.title = "image constant distribution of 1541-S"
hist.x_title = "pixels value"
hist.y_title = "number of pixels"
hist.x_labels = range(179, 230)
hist.add('median_0', image_constant__1_frequencies)
hist.add('median_1', image_constant__2_frequencies)
hist.add('median_2', image_constant__3_frequencies)
hist.add('median_3', image_constant__4_frequencies)
hist.add('median_4', image_constant__5_frequencies)
hist.add('median_5', image_constant__6_frequencies)
hist.add('median_6', image_constant__7_frequencies)
hist.add('median_7', image_constant__8_frequencies)
hist.add('median_8', image_constant__9_frequencies)
hist.add('median_9', image_constant__10_frequencies)
hist.render_to_file(os.path.dirname(file) + "\\image_constant_median.svg")
