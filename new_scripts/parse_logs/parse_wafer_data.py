import os
import xlrd
import xlwt
import sys


class analyze_excel:
    def __init__(self, file):
        self.file = file

    def parse_wafer_data(self, data):
        wafer_lot_ID = data[4:10]
        ID = data[-2:]
        X = data[10:12]
        Y = data[12:14]
        return [wafer_lot_ID, ID, (X, Y)]

    def insert_data(self):
        rb = xlrd.open_workbook(self.file)
        sheet_raw = rb.sheet_by_name('Sheet1')
        nrows = sheet_raw.nrows
        ncols = sheet_raw.ncols

        book = xlwt.Workbook()
        sheet = book.add_sheet('sheetname', cell_overwrite_ok=True)

        for i in range(0, nrows):
            for j in range(0, ncols):
                sheet.write(i, j, sheet_raw.cell_value(i, j))

                if i != 0:
                    test_data = str(sheet_raw.cell_value(i, 0)).strip()
                    wafer_info = self.parse_wafer_data(test_data)
                    sheet.write(i, 1, wafer_info[0])
                    sheet.write(i, 2, int(wafer_info[1], 16))
                    sheet.write(i, 3, "(" + str(int(wafer_info[2][0], 16)) + "," + str(int(wafer_info[2][1], 16)) + ")")

        book.save("D:\\09LogAnalyze\\extra\\Benson\\OTP_new.xls")


if __name__ == "__main__":
    try:
        path = "D:\\09LogAnalyze\\extra\\Benson\\OTP.xlsx"
        analyze_excel(path).insert_data()

    except Exception as e:
        print("Error {} caught in script".format(sys.exc_info()))