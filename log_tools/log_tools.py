#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 16:05:38 2017

@author: petter.ostlund
"""

import os
import json
from fnmatch import fnmatch
import numpy as np
import re
import struct

enc_types = ['utf8', 'cp1252']

# Extract values from "UdrTestValues"
def hexstring2values(x):
     uf = struct.unpack('>f',struct.pack('I',int(x[0:8],16)))[0]
     ss = struct.unpack('>f',struct.pack('I',int(x[8:16],16)))[0]
     rms = struct.unpack('>f',struct.pack('I',int(x[16:24],16)))[0]
     #print('run')
     return uf, ss, rms

class Optical:

    def __init__(self):
        self.root_dir = None
        self.data = {}

    def __call__(self, root_dir):
        self.root_dir = root_dir

        filelist = []
        for path, subdirs, files in os.walk(root_dir):
            for name in files:
                if fnmatch(name, '*.json'):
                    filelist.append(os.path.join(path, name))
        filelist.sort()

        # Regular expressions to extract values
        reg_dict = {'hwid': '("BridgeHwId": ")(\d+)',
                    'fpga_fw': '("BridgeFwRev": ")(\d+)',
                    'fpga_rev': '("BridgeRtlRev": ")(\d+)',
                    'sensor_id': '("SensorProdId": ")(\d+)',
                    'current': '(MeasuredCurrentMilliAmperes": )(\d+)'
                    }

        for file in filelist:
            for enc in enc_types:
                with open(file, encoding=enc, errors='replace') as f:
                    buffer = f.read()

            self.data[file] = []

            try:
                for key, values in reg_dict.items():
                    val = re.search(values, buffer).group(2)
                    #print(val)
                    self.data[file].append(float(val))
            except:
                pass

        return self.data


class MQT2ReRun:

    def __init__(self):
        self.root_dir = None
        self.data = {}

    def __call__(self, root_dir):
        self.root_dir = root_dir

        filelist = []
        for path, subdirs, files in os.walk(root_dir):
            for name in files:
                if fnmatch(name, '*.json'):
                    filelist.append(os.path.join(path, name))
        filelist.sort()

        # Regular expressions, comment out if not present
        #reg_sensorid = '("Sensor ID": ")(\w*)'
        reg_dict = {'snr': '("snr_db": )(\d+\.\d+)',
                    'blobs': '("number_of_blobs": )(\d+)',
                    'udr': '("udr": )(\d+\.\d+)',
                    'fp_pxl': '("fixed_pattern_pixels": )(\d+)',
                    'rms_us': '("rms_us": )(\d+.\d+|d+)',
                    'signal_power': '("value0": )(\d+.\d+|d+)',
#                    'value1': '("value1": )(\d+.\d+|d+)',
                    'noise_fp': '("value2": )(\d+.\d+|d+)',
                    'noise_thermal': '("value3": )(\d+.\d+|d+)'
#                    'value4': '("value4": )(\d+.\d+|d+)',
#                    'value5': '("value5": )(\d+.\d+|d+)',
#                    'value6': '("value6": )(\d+.\d+|d+)',
#                    'value7': '("value7": )(\d+.\d+|d+)',
#                    'value8': '("value8": )(\d+.\d+|d+)',
#                    'value9': '("value9": )(\d+.\d+|d+)',
#                    'value10': '("value10": )(\d+.\d+|d+)',
#                    'value11': '("value11": )(\d+.\d+|d+)',
#                    'value12': '("value12": )(\d+.\d+|d+)',
#                    'value13': '("value13": )(\d+.\d+|d+)',
#                    'value14': '("value14": )(\d+.\d+|d+)',
#                    'value15': '("value15": )(\d+.\d+|d+)'
                    }

        for file in filelist:
            for enc in enc_types:
                with open(file, encoding=enc, errors='replace') as f:
                    buffer = f.read()

            self.data[file] = []
            try:
                for key, values in reg_dict.items():
                    if key == 'value0':
                        val = re.findall(values, buffer).group(2)
                    val = re.search(values, buffer).group(2)
                    #print(val)
                    self.data[file].append(float(val))
            except:
                pass

        return self.data


class MTTLogsVaduz:

    def __init__(self):
        self.root_dir = None
        self.data = {}

    def static_mqt2(self, file, t):
        print(file)
        test_con = t['TestMethodConclusion']
        #print(test_con)
        if test_con == "Exception" or test_con == "NotRun":
            print('Exception or NotRun','\n')
            #self.data[file] = "exception_or_not_run"
        else:
            res = t['TestLog']['Steps']['analysis']['Items']['result']
            self.data[file] = []
            for p in res['ModuleQualityAnalysis']:
                #if p['Status'] == "OK":
                try:
                    snr = float(p['Snr']['SnrDb'])
                    blob = float(p['Blob']['BlobCount'])
                    udr = float(p['Udr']['Udr'])
                    uf, ss, rms = hexstring2values(p['Udr']['UdrTestValues'])
                    #print([snr, blob, udr, uf, ss, rms], '\n')
                    self.data[file].append([snr, blob, udr, uf, ss, rms])
                except:
                    self.data[file].append([-1000, -1000, -1000, -1000, -1000, -1000])

    def __call__(self, root_dir):
        self.root_dir = root_dir

        filelist = []
        for path, subdirs, files in os.walk(root_dir):
            for name in files:
                if fnmatch(name, '*.json'):
                    filelist.append(os.path.join(path, name))

        for file in filelist:
            for enc in enc_types:
                with open(file, encoding=enc, errors='replace') as f:
                    filedata = json.load(f)

            for item in filedata['TestReportItems']:
                if item['Name'] == 'Static Capture Module Quality':
                    self.static_mqt2(file, item['Result'])

        return self.data

class MTTLogsVaduzWrapper:

    def __init__(self):
        self.root_dir = None
        self.data = {}

    def static_mqt2(self, file, t):
        #print(file)
        #test_con = t['conclusion']
        #print(test_con)
        #if test_con == "Exception" or test_con == "NotRun":
            #print('Exception or NotRun','\n')
            #self.data[file] = "exception_or_not_run"
        if t['conclusion'] == "pass":
            res = 1
        else:
            res = 0
        self.data[file] = []
        # Check total stamp yield.
        for p in t['analysis']['result']['model_quality_analysis']:
            #if p['Status'] == "OK":
            try:
                snr = float(p['snr']['snr_db'])
                blob = float(p['blob']['number_of_blobs'])
                udr = float(p['udr']['udr'])
                uf, ss, rms = hexstring2values(p['udr']['udr_test_values'])
                #print([snr, blob, udr, uf, ss, rms], '\n')
                self.data[file].append([snr, blob, udr, uf, ss, rms, res])
            except:
                self.data[file].append([-1000, -1000, -1000, -1000, -1000, -1000, -1000])

    def __call__(self, root_dir):
        self.root_dir = root_dir

        filelist = []
        for path, subdirs, files in os.walk(root_dir):
            for name in files:
                if fnmatch(name, '*.json'):
                    filelist.append(os.path.join(path, name))

        print("Number of json files = ", len(filelist))

        for file in filelist:
            for enc in enc_types:
                with open(file, encoding=enc, errors='replace') as f:
                    filedata = json.load(f)

            for item in filedata['sequence']:
                if item['name'] == 'static_capture_module_quality':
                    self.static_mqt2(file, item)

        return self.data


class MTTLogsMQT2:

    def __init__(self):
        self.root_dir = None
        self.data = {}

    def hexstring2values(self, x):
     uf = struct.unpack('>f',struct.pack('I',int(x[0:8],16)))[0]
     ss = struct.unpack('>f',struct.pack('I',int(x[8:16],16)))[0]
     rms = struct.unpack('>f',struct.pack('I',int(x[16:24],16)))[0]
     #print('run')
     return uf, ss, rms

    def __call__(self, root_dir, sensor_id = True):
        self.root_dir = root_dir
        self.sensor_id = sensor_id  # If False, use filename

        filelist = []
        for path, subdirs, files in os.walk(root_dir):
            for name in files:
                if fnmatch(name, '*.json'):
                    filelist.append(os.path.join(path, name))
        filelist.sort()
        print(len(filelist), "log files")

        # Regular expressions, comment out if not present
        #reg_sensorid = '("Sensor ID": ")(\w*)'
        reg_dict = {'mqt2': '(Quality2",\s*"TestMethodConclusion": ")(\w*)',
                    'snr': '("SnrDb": )(\d+\.\d+)',
                    'blobs': '("BlobCount": )(\d+)',
                    'udr': '("Udr": )(\d+\.\d+)',
                    'udr_string': '("UdrTestValues": ")(\w+)',
                    'afd': '("TestAfdCal",\s*"TestMethodConclusion": ")(\w*)',
# BM lite                    'afd': '("TestResetPixels",\s*"TestMethodConclusion": ")(\w*)',
                    'def': '("TestCtlDefectivePixels",\s*"TestMethodConclusion": ")(\w*)',
# BM lite                    'def': '("TestCtlDeadPixels",\s*"TestMethodConclusion": ")(\w*)',
                    'otp': '("TestReadOtp",\s*"TestMethodConclusion": ")(\w*)',
                    'fp': '(FixedPatternPixels": )(\d+)'}

        for file in filelist:
            for enc in enc_types:
                with open(file, encoding=enc, errors='replace') as f:
                    buffer = f.read()

            if sensor_id == False: # Use filename as "sensor id"
                sens_id = file[-30:].rstrip('.json')
                #reg_sensorid = '("OtpData": ")([\w+\s+]+)'
                try:
                    sens_id = re.search(reg_sensorid, buffer).group(2)
                    no_id = 0
                except:
                    no_id = 1
            elif sensor_id == True: #
#                reg_sensorid = '("UniqueTestId": ")(\w+-\w+-\w+)'
                reg_sensorid = '("SensorId": ")(\w+)'
                try:
                    sens_id = re.search(reg_sensorid, buffer).group(2)
                    no_id = 0
                except:
                    no_id = 1

            if no_id == 0:  # if sensor id exists
                if sens_id not in self.data:
                     self.data[sens_id] = {'snr': [], 'blobs': [], 'udr': [],\
                              'uf': [], 'ss': [], 'rms': [], 'afd': [],\
                              'def': [], 'otp':[], 'mqt2':[], 'fp':[]}
                     #print(sens_id)

                try:
                    for _,val in re.findall(reg_dict['mqt2'], buffer):
                        if val == "Success":
                            self.data[sens_id]['mqt2'].append(1)
                        elif val == "Fail":
                            self.data[sens_id]['mqt2'].append(0)
                            #print(sens_id, val)
                except:
                    pass

                try:
                    snr = re.findall(reg_dict['snr'], buffer)
                    for _, val in snr:
                        self.data[sens_id]['snr'].append(float(val))
                        if float(val) < 10.3 and float(val) > 5 :
                            print("SNR >5 <10.3", sens_id, float(val))
                            print("\n")
                except:
                    pass

                try:
                    blobs = re.findall(reg_dict['blobs'], buffer)
                    for _, val in blobs:
                        self.data[sens_id]['blobs'].append(float(val))
                        if float(val) > 0:
                            print("Blobs >1", sens_id, float(val))
                            print("\n")
                except:
                    pass

                try:
                    udr = re.findall(reg_dict['udr'], buffer)
                    for _, val in udr:
                        self.data[sens_id]['udr'].append(float(val))
                        #if val == "0.0":
                            #print(sens_id)
                except:
                    pass

                try:
                   udr_str = re.findall(reg_dict['udr_string'], buffer)
                   #print(udr_str)
                   if udr_str:
                       for _, string in udr_str:
                           uf, ss, rms = self.hexstring2values(string)
                           #print(file, sens_id, uf, ss, rms)
                           self.data[sens_id]['uf'].append(uf)
                           self.data[sens_id]['ss'].append(ss)
                           self.data[sens_id]['rms'].append(rms)
                except:
                    pass

                try:
                    for _,val in re.findall(reg_dict['afd'], buffer):
                        if val == "Success":
                            self.data[sens_id]['afd'].append(1)
                        elif val == "Fail":
                            self.data[sens_id]['afd'].append(0)
                except:
                    pass
                try:
                    for _,val in re.findall(reg_dict['def'], buffer):
                        if val == "Success":
                           self.data[sens_id]['def'].append(1)
                        elif val == "Fail":
                            self.data[sens_id]['def'].append(0)
                            print(file)
                except:
                    pass
                try:
                    for _,val in re.findall(reg_dict['otp'], buffer):
                        if val == "Success":
                            self.data[sens_id]['otp'].append(1)
                        elif val == "Fail":
                            self.data[sens_id]['otp'].append(0)
                except:
                    pass
                try:
                    for _,val in re.findall(reg_dict['fp'], buffer):
                        self.data[sens_id]['fp'].append(float(val))
                        if float(val) > 30:
                            print(file)
                except:
                    pass

    def get_data(self):
        return self.data

    # Shape of array (sensor_ids) x (tests) x (min,max,mean,no)
    def get_min_max_mean_array(self):
        no_of_sens = len(self.data)
        test_strings = ['snr', 'blobs', 'udr', 'uf', 'ss', 'rms', 'afd', 'def', 'otp', 'mqt2', 'fp']
        ii = 0
        result = np.zeros((no_of_sens, 11, 4), np.float)
        for keys, values in self.data.items():
            for index, test in enumerate(test_strings):
                test_array = values[test]
                if test_array == []: # No test data
                    test_array.append(-1000)
                result[ii, index, 0] = np.min(test_array)
                result[ii, index, 1] = np.max(test_array)
                result[ii, index, 2] = np.mean(test_array)
                result[ii, index, 3] = len(test_array)

            ii += 1
        return result


class MTTLogsJson:

    def __init__(self):
        self.root_dir = None
        self.data = {}

    def __call__(self, root_dir, sensor_id = True):

        filelist = []
        for path, subdirs, files in os.walk(root_dir):
            for name in files:
                if fnmatch(name, '*.json'):
                    filelist.append(os.path.join(path, name))
        filelist.sort()
        print(len(filelist), "log files")

        # Regular expressions, comment out if not present
        reg_dict = {'uf': '("uniformity_level": {\s*"d": )(\d*\.\d*)',
                    'ss': '("signal_strength": {\s*"d": )(\d*\.\d*)',
                    'blobs': '("number_of_blob_pixels": {\s*"d": )(\d*)',
                    'snr': '("snr_db": )(\d*\.\d*)',
                    'afd': '("TestAfdCalibrationWithRubberstamp",\s*"TestMethodConclusion": ")(\w*)',
                    'dead': '("TestDeadPixelsProdTestLibGradient",\s*"TestMethodConclusion": ")(\w*)',
                    'otp': '("TestReadOtp",\s*"TestMethodConclusion": ")(\w*)'}

        for file in filelist:
            for enc in enc_types:
                with open(file, encoding=enc, errors='replace') as f:
                    buffer = f.read()

            if sensor_id == False: # Use filename as "sensor id"
                sens_id = file.rstrip('.json')
                if sens_id not in self.data:
                    self.data[sens_id] = {'uf': [], 'ss': [], 'blobs': [],\
                             'snr': [], 'afd': [], 'dead': [], 'otp':[]}

            elif sensor_id == True: # Use Sensor Id in json file
                reg_sensorid = '("SensorId": ")(\w*)'
                #reg_sensorid = '("OtpMemoryMainData": ")([\w+\s+]+)'
                try:
                    sens_id = re.search(reg_sensorid, buffer).group(2)
                    if sens_id not in self.data:
                        self.data[sens_id] = {'uf': [], 'ss': [], 'blobs': [],\
                             'snr': [], 'afd': [], 'dead': [], 'otp':[]}
                except:
                    pass

            try:
                uf = re.findall(reg_dict['uf'], buffer)
                for _, val in uf:
                    self.data[sens_id]['uf'].append(float(val))
            except:
                pass
            try:
                ss = re.findall(reg_dict['ss'], buffer)
                for _, val in ss:
                    self.data[sens_id]['ss'].append(float(val))
            except:
                pass
            try:
                blobs = re.findall(reg_dict['blobs'], buffer)
                for _, val in blobs:
                    self.data[sens_id]['blobs'].append(float(val))
            except:
                pass
            try:
                snr = re.findall(reg_dict['snr'], buffer)
                for _, val in snr:
                    self.data[sens_id]['snr'].append(float(val))
                    if float(val) < 9:
                        print(file)
            except:
                pass
            try:
                for _,val in re.findall(reg_dict['afd'], buffer):
                    if val == "Success":
                        self.data[sens_id]['afd'].append(1)
                    elif val == "Fail":
                        self.data[sens_id]['afd'].append(0)
            except:
                pass
            try:
                for _,val in re.findall(reg_dict['dead'], buffer):
                    if val == "Success":
                        self.data[sens_id]['dead'].append(1)
                    elif val == "Fail":
                        self.data[sens_id]['dead'].append(0)
            except:
                pass
            try:
                for _,val in re.findall(reg_dict['otp'], buffer):
                    if val == "Success":
                        self.data[sens_id]['otp'].append(1)
                    elif val == "Fail":
                        self.data[sens_id]['otp'].append(0)
            except:
                pass


    def get_data(self):
        return self.data

    # Shape of array (sensor_ids) x (tests) x (min,max,mean,no)
    def get_min_max_mean_array(self):
        no_of_sens = len(self.data)
        test_strings = ['uf', 'ss', 'blobs', 'snr', 'afd', 'dead', 'otp']
        ii = 0
        result = np.zeros((no_of_sens, 8, 4), np.float)
        for keys, values in self.data.items():
            for index, test in enumerate(test_strings):
                test_array = values[test]
                if test_array == []: # No test data
                    test_array.append(-1000)
                result[ii, index, 0] = np.min(test_array)
                result[ii, index, 1] = np.max(test_array)
                result[ii, index, 2] = np.mean(test_array)
                result[ii, index, 3] = len(test_array)

            ii += 1
        return result


class MTTLogsHtml2:

    def __init__(self):
        self.root_dir = None
        self.data = {}

    def __call__(self, root_dir, sensor_id = True):

        filelist = []
        for path, subdirs, files in os.walk(root_dir):
            for name in files:
                if fnmatch(name, '*.html'):
                    filelist.append(os.path.join(path, name))
        filelist.sort()
        print(len(filelist), "log files")

        reg_exp = {'udr': '(UDR: )(\d*\.\d*)',
                   'udr_string': '(Udr test value: )(\w+)',
                   'blobs': '(Blob count: )(\d*)',
                   'snr':  '(SNR\(dB\): )(\d*\.\d*)',
                   'afd':  '(Test Afd Cal: <b>)([A-Z][a-z]*)',
                   'def':  '(Test Ctl Defective Pixels: <b>)([A-Z][a-z]*)',
                   'otp':  '(Test OTP Read: <b>)([A-Z][a-z]*)',
                   'total': '(Sensor Result: <b>)(\w+)'}

        for file in filelist:
            for enc in enc_types:
                with open(file, encoding=enc, errors='replace') as f:
                    buffer = f.read()

            if sensor_id == False: # Use filename as "sensor id"
                sens_id = file.rstrip('.html')
                if sens_id not in self.data:
                    self.data[sens_id] = {'uf': [], 'ss': [], 'blobs': [],\
                             'snr': [], 'afd': [], 'def': [], 'otp': [],\
                             'udr': [], 'rms': [], 'tot': []}

            elif sensor_id == True: # Use Sensor Id in html file
                reg_sensorid = '(Sensor ID: </b>)(.+)'
#                reg_sensorid = '(OTP ChipID:)(\w*)'
                try:
                    sens_id = re.search(reg_sensorid, buffer).group(2)
                    #print(sens_id)
                    if sens_id not in self.data:
                        self.data[sens_id] = {'uf': [], 'ss': [], 'blobs': [],\
                                 'snr': [], 'afd': [], 'def': [], 'otp':[],
                                 'udr': [], 'rms': [], 'tot': []}
                except:
                    pass


                try:
                    # Add uniformity value
                    udr = re.search(reg_exp['udr'], buffer).group(2)
                    self.data[sens_id]['udr'].append(float(udr))
                    # Add signal strength
                    udr_string = re.search(reg_exp['udr_string'], buffer).group(2)
                    #print(udr_string)
                    uf, ss, rms = hexstring2values(udr_string)
                    #print(uf, ss, rms)
                    self.data[sens_id]['uf'].append(float(uf))
                    self.data[sens_id]['ss'].append(float(ss))
                    self.data[sens_id]['rms'].append(float(rms))
                except:
                    pass
                try:
                    # Add number of blobs
                    blobs = re.search(reg_exp['blobs'], buffer).group(2)
                    self.data[sens_id]['blobs'].append(int(blobs))
                    if int(blobs) > 7:
                        print(file)
                except:
                    pass
                try:
                    # Add snr
                    snr = re.search(reg_exp['snr'], buffer).group(2)
                    self.data[sens_id]['snr'].append(float(snr))
                except:
                    pass
                try:
                    # Add defective pixels
                    de = re.search(reg_exp['def'], buffer).group(2)
                    if de ==  'Pass':
                        self.data[sens_id]['def'].append(1)
                    else:
                        self.data[sens_id]['def'].append(0)
                except:
                    pass
                try:
                    # Add AFD
                    afd = re.search(reg_exp['afd'], buffer).group(2)
                    if afd ==  'Pass':
                        self.data[sens_id]['afd'].append(1)
                    else:
                        self.data[sens_id]['afd'].append(0)
                except:
                    pass
                try:
                    # Total
                    tot = re.search(reg_exp['total'], buffer).group(2)
                    if tot ==  'Pass':
                        self.data[sens_id]['tot'].append(1)
                    else:
                        self.data[sens_id]['tot'].append(0)
                except:
                    pass

    def get_data(self):
        return self.data

    # Shape of array (sensor_ids) x (tests) x (min,max,mean,no)
    def get_min_max_mean_array(self):
        no_of_sens = len(self.data)
        test_strings = ['uf', 'ss', 'blobs', 'snr', 'afd', 'def', 'otp', 'udr', 'rms', 'tot']
        ii = 0
        result = np.zeros((no_of_sens, 10, 4), np.float)
        for keys, values in self.data.items():
            for index, test in enumerate(test_strings):
                test_array = values[test]
                if test_array == []:
                    test_array.append(-1000)
                result[ii, index, 0] = np.min(test_array)
                result[ii, index, 1] = np.max(test_array)
                result[ii, index, 2] = np.mean(test_array)
                result[ii, index, 3] = len(test_array)

            ii += 1
        return result


class MTTLogsHtml:

    def __init__(self):
        self.root_dir = None
        self.data = {}

    def __call__(self, root_dir, sensor_id = True):

        filelist = []
        for path, subdirs, files in os.walk(root_dir):
            for name in files:
                if fnmatch(name, '*.html'):
                    filelist.append(os.path.join(path, name))
        filelist.sort()
        print(len(filelist), "log files")

        reg_exp = {'uf': '(Uniformity: )(\d*\.\d*)',
                   'ss': '(Capacitance Signal Strength Median: )(\d*\.\d*)',
                   'blobs': '(Number of blobs pixels: )(\d*)',
                   'snr':  '(snr: )(\d*\.\d*)',
                   'afd':  '(Test Afd: <b>)([A-Z][a-z]*)',
                   'dead':  '(Test Dead Pixel: <b>)([A-Z][a-z]*)',
                   'otp':  '(Test OTP Read: <b>)([A-Z][a-z]*)'}

        for file in filelist:
            for enc in enc_types:
                with open(file, encoding=enc, errors='replace') as f:
                    buffer = f.read()

            if sensor_id == False: # Use filename as "sensor id"
                sens_id = file.rstrip('.html')
                if sens_id not in self.data:
                    self.data[sens_id] = {'uf': [], 'ss': [], 'blobs': [],\
                             'snr': [], 'afd': [], 'dead': [], 'otp':[]}

            elif sensor_id == True: # Use Sensor Id in html file
#                reg_sensorid = '(Sensor ID: </b>)(\w*)'
                reg_sensorid = '(OTP ChipID:)(\w*)'
                try:
                    sens_id = re.search(reg_sensorid, buffer).group(2)
                    if sens_id not in self.data:
                        self.data[sens_id] = {'uf': [], 'ss': [], 'blobs': [],\
                                 'snr': [], 'afd': [], 'dead': [], 'otp':[]}
                except:
                    pass


                try:
                    # Add uniformity value
                    uf = re.search(reg_exp['uf'], buffer).group(2)
                    self.data[sens_id]['uf'].append(float(uf)/100)
                    # Add signal strength
                    ss = re.search(reg_exp['ss'], buffer).group(2)
                    self.data[sens_id]['ss'].append(float(ss))
                    # Add number of blobs
                    blobs = re.search(reg_exp['blobs'], buffer).group(2)
                    self.data[sens_id]['blobs'].append(int(blobs))
                except:
                    pass
                try:
                    # Add snr
                    snr = re.search(reg_exp['snr'], buffer).group(2)
                    self.data[sens_id]['snr'].append(float(snr))
                except:
                    pass
                try:
                    # Add dead pixels
                    dead = re.search(reg_exp['dead'], buffer).group(2)
                    if dead ==  'Pass':
                        self.data[sens_id]['dead'].append(1)
                    else:
                        self.data[sens_id]['dead'].append(0)
                except:
                    pass

    def get_data(self):
        return self.data

    # Shape of array (sensor_ids) x (tests) x (min,max,mean,no)
    def get_min_max_mean_array(self):
        no_of_sens = len(self.data)
        test_strings = ['uf', 'ss', 'blobs', 'snr', 'afd', 'dead', 'otp']
        ii = 0
        result = np.zeros((no_of_sens, 7, 4), np.float)
        for keys, values in self.data.items():
            for index, test in enumerate(test_strings):
                test_array = values[test]
                if test_array == []:
                    test_array.append(-1000)
                result[ii, index, 0] = np.min(test_array)
                result[ii, index, 1] = np.max(test_array)
                result[ii, index, 2] = np.mean(test_array)
                result[ii, index, 3] = len(test_array)

            ii += 1
        return result