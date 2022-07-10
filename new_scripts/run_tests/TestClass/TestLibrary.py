import ctypes as c
import os
import re

MAX_NBR_SUB_AREA_ROWS = 4
MAX_NBR_SUB_AREA_COLS = 4

product_map = {
    "1080" : 0,
    "1020" : 1,
    "1021" : 2,
    "1025" : 3,
    "1225" : 4,
    "1022" : 5,
    "1035" : 6,
    "1235" : 7,
    "1140" : 8,
    "1145" : 9,
    "1245" : 10,
    "1150" : 11,
    "1155" : 12,
    "1265" : 14,
    "1268" : 15,
    "1028" : 16,
    "1075" : 17,
    "1320" : 18,
    "1321" : 19,
    "1263" : 20,
    "1262" : 21,
    "1266" : 22,
    "1264" : 23,
    "1272" : 24,
    "1228" : 25,
    "1181" : 26,
    "1267" : 27,
    "1282" : 28,
    "1283" : 29,
    "1286" : 30,
    "1291" : 31}

sensor_map = {
"1011": 0,
"1020": 1,
"1021": 2,
"1022": 3,
"1140": 4,
"1150": 5,
"1080": 6,
"1260": 7,
"1023": 8,
"1270": 9,
"1280": 10,
"1290": 11
}

PRODTESTLIB_MTT_VERSIONS = {8.1: "ModuleTestTool 8.1\\prodtestlib.dll",
                            9.1: "MTT 9.1\\prodtestlib.dll",
                            10.0: "MTT 10.0\\prodtestlib.dll",
                            11.0: "MTT 11.0\\prodtestlib.dll",
                            12.0: "MTT_12.0\\prodtestlib.dll"}

class TestLib(object):
    def __init__(self, test, version = 12.0):
        self.hal_library_name = PRODTESTLIB_MTT_VERSIONS[version]

        self._load_library(version)

        assert self.hal_dll != None
        
        if test == "DeadPixels":
            self.init_gradient_checkerboard_test_based_on_test_level = self.hal_dll.init_gradient_checkerboard_test_based_on_test_level
            self.gradient_checkerboard_test = self.hal_dll.gradient_checkerboard_test
            self.checkerboard_test = self.hal_dll.checkerboard_test
            self.init_checkerboard_test = self.hal_dll.init_checkerboard_test
        elif test == "ImageConstant":
            self.init_image_constant_test = self.hal_dll.init_image_constant_test
            self.image_constant_test = self.hal_dll.image_constant_test
            self.free_image_constant_medians = self.hal_dll.free_image_constant_medians
        elif test == "Blob":
            self.init_blob_test = self.hal_dll.init_blob_test
            self.calculate_blob = self.hal_dll.calculate_blob

    def __str__(self):
        return self.hal_library_name + ": " + str(self.hal_dll)

    def _load_library(self, version):
        current_wdr = os.getcwd()
        pattern = ".+?(?=python_scripts)"
        search_object = re.match(pattern, current_wdr)
        mtt_directory = os.path.join(search_object.group(0), "python_scripts", "wrapper", "binaries")
        file_path = os.path.join(mtt_directory, PRODTESTLIB_MTT_VERSIONS[version])
        directory, file = os.path.split(file_path)

        os.chdir(directory)
        self.hal_dll = c.CDLL(file_path)
        os.chdir(current_wdr)