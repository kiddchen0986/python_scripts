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

class TestLib(object):
    def __init__(self, test:str, version = 15.0):
        self._load_library(version)

        assert self.c_dll != None
        
        if test == "DeadPixels":
            self.init_gradient_checkerboard_test_based_on_test_level = self.c_dll.init_gradient_checkerboard_test_based_on_test_level
            self.gradient_checkerboard_test = self.c_dll.gradient_checkerboard_test
            self.checkerboard_test = self.c_dll.checkerboard_test
            self.init_checkerboard_test = self.c_dll.init_checkerboard_test
        elif test == "ImageConstant":
            self.init_image_constant_test = self.c_dll.init_image_constant_test
            self.image_constant_test = self.c_dll.image_constant_test
            self.free_image_constant_medians = self.c_dll.free_image_constant_medians
        elif test == "Blob":
            self.init_blob_test = self.c_dll.init_blob_test
            self.calculate_blob = self.c_dll.calculate_blob

    def __str__(self):
        return  str(self.c_dll)

    def _load_library(self, version):
        current_wdr = os.getcwd()
        mtt_directory = os.path.join(current_wdr, 'MTTLibs\\' + str(version))
        os.chdir(mtt_directory)
        self.c_dll = c.CDLL('prodtestlib.dll')
        os.chdir(current_wdr)