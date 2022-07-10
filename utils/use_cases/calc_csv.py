"""Containing functions to manipulate and calculate values found in csv file"""
import utils.io_csv as io_csv
from utils.from_files import find_files

def read_defective_pixel(file_path):
    """Read the data found in .csv file containing test results from defective pixel

    Since there are multiple cell values with the same value, the generic method could not be used to create a
    dictionary of the data without supplying a list of the modified header values.

    :param file_path: the path to the csv file
    :type file_path: str
    :return: list of dicts, key is header and value is the cell value
    :rtype: list of dicts
    """

    headers = ["test_id",
               "file_paths",
               "pass",
               "error_code",
               "product_type",
               "hwid",
               "dead_pixels_list.num_dead_pixels",
               "dead_pixels_list.dead_pixels_index_list",
               "dead_pixels_list.list_max_size",
               "dead_pixels_list.is_initialized",
               "checkerboard.CheckerboardResult.pixel_errors",
               "checkerboard.CheckerboardResult.sub_area_errors",
               "checkerboard.CheckerboardResult.type1_median",
               "checkerboard.CheckerboardResult.type2_median",
               "checkerboard.CheckerboardResult.type1_mean",
               "checkerboard.CheckerboardResult.type2_mean",
               "checkerboard.CheckerboardResult.type1_deviation_max",
               "checkerboard.CheckerboardResult.type2_deviation_max",
               "checkerboard.CheckerboardResult.result",
               "checkerboard.CheckerboardResult.pass",
               "checkerboard.CheckerboardResult.pixel_errors_per_row",
               "checkerboard.CheckerboardResult.pixel_errors_per_col",
               "checkerboard.CheckerboardResult.error_code",
               "inverted_checkerboard.CheckerboardResult.pixel_errors",
               "inverted_checkerboard.CheckerboardResult.sub_area_errors",
               "inverted_checkerboard.CheckerboardResult.type1_median",
               "inverted_checkerboard.CheckerboardResult.type2_median",
               "inverted_checkerboard.CheckerboardResult.type1_mean",
               "inverted_checkerboard.CheckerboardResult.type2_mean",
               "inverted_checkerboard.CheckerboardResult.type1_deviation_max",
               "inverted_checkerboard.CheckerboardResult.type2_deviation_max",
               "inverted_checkerboard.CheckerboardResult.result",
               "inverted_checkerboard.CheckerboardResult.pass",
               "inverted_checkerboard.CheckerboardResult.pixel_errors_per_row",
               "inverted_checkerboard.CheckerboardResult.pixel_errors_per_col",
               "inverted_checkerboard.CheckerboardResult.error_code",
               "reset_pixel.ResetPixelsResult.median",
               "reset_pixel.ResetPixelsResult.pixels_outside_limit",
               "reset_pixel.ResetPixelsResult.pixels_under_limit",
               "reset_pixel.ResetPixelsResult.pixels_over_limit",
               "reset_pixel.ResetPixelsResult.min_value",
               "reset_pixel.ResetPixelsResult.max_value",
               "reset_pixel.ResetPixelsResult.pass",
               "reset_pixel.ResetPixelsResult.error_code"]

    return io_csv.read_file(file_path, headers, 15)


def analyze_data(data):
    """Count the number of value occurrences for each key

    :param data: row data; each dict containing a rows values
    :type data: list of dicts
    :return: dict of dicts. header is first key, value is sub-key and number of occurrences is thevalue
    :rtype: dict of dicts
    """
    analyzed = {}
    for row in data:
        for header, value in row.items():

            if header not in analyzed:
                analyzed[header] = {}

            if value in analyzed[header]:
                analyzed[header][value] += 1
            else:
                analyzed[header][value] = 1

    return analyzed


def calc_yield_tests_def_pix(*file_path):
    """Calculate the yield for the combined and individual tests in the defective pixels suite

    :param file_path: file paths to the .csv files
    :type file_path: str
    :return:
    """
    for f in file_path:
        data = read_defective_pixel(f)
        analyze = analyze_data(data)

        analyze["dead_pixels_list.pass"] = {"True": 0, "False": 0}
        for key, value in analyze["dead_pixels_list.num_dead_pixels"].items():
            if int(key) > 8:
                analyze["dead_pixels_list.pass"]["False"] += value
            else:
                analyze["dead_pixels_list.pass"]["True"] += value

        nbr_tests = len(data)
        yields = {"defective_pixel": analyze["pass"]["True"] / nbr_tests,
                  "dead_pixels_list": analyze["dead_pixels_list.pass"]["True"] / nbr_tests,
                  "checkerboard": analyze["checkerboard.CheckerboardResult.pass"]["True"] / nbr_tests,
                  "inverted_checkerboard": analyze["inverted_checkerboard.CheckerboardResult.pass"]["True"] / nbr_tests,
                  "reset_pixel": analyze["reset_pixel.ResetPixelsResult.pass"]["True"] / nbr_tests}

        print(f)
        for key, value in yields.items():
            print("\t", key, "\t", value)


if __name__ == '__main__':
    file_paths = find_files(r"C:\Hugo_documents\Qualification Defective Pixel\1245_defective_pixels_results", ".csv")

    calc_yield_tests_def_pix(*file_paths)
