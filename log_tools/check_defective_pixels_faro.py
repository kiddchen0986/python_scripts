# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 15:49:14 2018

@author: petter.ostlund
"""

# Check defective pixel values.

import os
from fnmatch import fnmatch
import re
import numpy as np
import matplotlib.pyplot as plt

enc_types = ['utf8', 'cp1252']

#path = r'C:\Logs\FPC1511-S_mtt16_2_lens_20180821'
#path = r'C:\Logs\FPC1511-S_mtt16_2_lens_20180821\jira_flga-7'
path = r'C:\Logs\FPC1511-S_mtt16_2_lens_20180821\huawei_faro_test_lens'

filelist = []
for path, subdirs, files in os.walk(path):
    for name in files:
        if fnmatch(name, '*log.txt'):
            filelist.append(os.path.join(path, name))
    filelist.sort()

print(len(filelist))


re_sensorid = '(Sensor ID: )(\w+)'
re_sw_cb = '(Swinging checkerboard result...\s+Max deviation: <= 15\s+Type1 median, min )(\d+)( max )(\d+)( \(Limit: > )(\d+)( and < )(\d+)(\)\s+Type2 median, min )(\d+)( max )(\d+)( \(Limit: > )(\d+)( and < )(\d+)'
re_sw_icb = '(Swinging inverted checkerboard result...\s+Max deviation: <= 15\s+Type1 median, min )(\d+)( max )(\d+)( \(Limit: > )(\d+)( and < )(\d+)(\)\s+Type2 median, min )(\d+)( max )(\d+)( \(Limit: > )(\d+)( and < )(\d+)'


sw_cb = {}
sw_icb = {}

for file in filelist:
    for enc in enc_types:
        with open(file, encoding=enc, errors='replace') as f:
            buffer = f.read()

    try:
        sensorid = re.search(re_sensorid, buffer).group(2)

        # sw cb
        vals = re.search(re_sw_cb, buffer)
        type1_min = int(vals.group(2))
        type1_max = int(vals.group(4))
        type1_lim_min = int(vals.group(6))
        type1_lim_max = int(vals.group(8))
        type2_min = int(vals.group(10))
        type2_max = int(vals.group(12))
        type2_lim_min = int(vals.group(14))
        type2_lim_max = int(vals.group(16))
        sw_cb_vals = np.array([type1_min, type1_max, type1_lim_min, type1_lim_max,
                      type2_min, type2_max, type2_lim_min, type2_lim_max])
        if sensorid not in sw_cb:
            sw_cb[sensorid] = sw_cb_vals
        if sensorid in sw_cb:
            pass
            #sw_cb[sensorid].append(sw_cb_vals)
    except:
        pass

    try:
        # sw icb
        vals = re.search(re_sw_icb, buffer)
        type1_min = int(vals.group(2))
        type1_max = int(vals.group(4))
        type1_lim_min = int(vals.group(6))
        type1_lim_max = int(vals.group(8))
        type2_min = int(vals.group(10))
        type2_max = int(vals.group(12))
        type2_lim_min = int(vals.group(14))
        type2_lim_max = int(vals.group(16))
        sw_icb_vals = np.array([type1_min, type1_max, type1_lim_min, type1_lim_max,
                      type2_min, type2_max, type2_lim_min, type2_lim_max])
        if sensorid not in sw_icb:
            sw_icb[sensorid] = sw_icb_vals
        if sensorid in sw_icb:
            pass
            #sw_icb[sensorid].append(sw_icb_vals)
    except:
        pass

## Write results to csv file
#with open("CB_log_summary_Huawei_modules.csv", 'w') as f:
#    f.write("SensorID;CB_type1_min;CB_type1_max;CB_type1_LL;CB_type1_UL;CB_type2_min;CB_type2_max;CB_type2_LL;CB_type2_UL;\n")
#    for k, v in sw_cb.items():
#        res = k +';'+str(v[0])+';'+str(v[1])+';'+str(v[2])+';'+str(v[3])+';'+str(v[4])+';'+str(v[5])+';'+str(v[6])+';'+str(v[7])+'\n'
#        f.write(res)
#
#print(sw_icb)
#
## Write results to csv file
#with open("ICB_log_summary_Huawei_modules.csv", 'w') as f:
#    f.write("SensorID;ICB_type1_min;ICB_type1_max;ICB_type1_LL;ICB_type1_UL;ICB_type2_min;ICB_type2_max;ICB_type2LUL;ICB_type2_UL;\n")
#    for k, v in sw_icb.items():
#        res = k +';'+str(v[0])+';'+str(v[1])+';'+str(v[2])+';'+str(v[3])+';'+str(v[4])+';'+str(v[5])+';'+str(v[6])+';'+str(v[7])+'\n'
#        f.write(res)

# Make array for plotting
result_sw_cb = np.zeros((len(sw_cb), 8), np.float)
ii = 0
for keys, values in sw_cb.items():
    arr = np.asarray(values)
    result_sw_cb[ii] = arr
    ii += 1

result_sw_icb = np.zeros((len(sw_icb), 8), np.float)
ii = 0
for keys, values in sw_icb.items():
    arr = np.asarray(values)
    result_sw_icb[ii] = arr
    ii += 1



title = "CB "

y_max = 300
n, bins, patches = plt.hist(result_sw_cb[:,0], 100, range=(0,255))
n, bins, patches = plt.hist(result_sw_cb[:,1], 100, range=(0,255))
plt.plot([result_sw_cb[0,2], result_sw_cb[0,2]],[0, y_max], 'r')
plt.plot([result_sw_cb[0,3], result_sw_cb[0,3]],[0, y_max], 'r')
plt.title(title + "type1_min and max")
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("Values (min and max)")
plt.show()

y_max = 300
n, bins, patches = plt.hist(result_sw_cb[:,4], 100, range=(0,255))
n, bins, patches = plt.hist(result_sw_cb[:,5], 100, range=(0,255))
plt.plot([result_sw_cb[0,6], result_sw_cb[0,6]],[0, y_max], 'r')
plt.plot([result_sw_cb[0,7], result_sw_cb[0,7]],[0, y_max], 'r')
plt.title(title + "type2_min and max")
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("Values (min and max)")
plt.show()


title = "ICB "

y_max = 300
n, bins, patches = plt.hist(result_sw_icb[:,0], 100, range=(0,255))
n, bins, patches = plt.hist(result_sw_icb[:,1], 100, range=(0,255))
plt.plot([result_sw_icb[0,2], result_sw_icb[0,2]],[0, y_max], 'r')
plt.plot([result_sw_icb[0,3], result_sw_icb[0,3]],[0, y_max], 'r')
plt.title(title + "type1_min and max")
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("Values (min and max)")
plt.show()

y_max = 300
n, bins, patches = plt.hist(result_sw_icb[:,4], 100, range=(0,255))
n, bins, patches = plt.hist(result_sw_icb[:,5], 100, range=(0,255))
plt.plot([result_sw_icb[0,6], result_sw_icb[0,6]],[0, y_max], 'r')
plt.plot([result_sw_icb[0,7], result_sw_icb[0,7]],[0, y_max], 'r')
plt.title(title + "type2_min and max")
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("Values (min and max)")
plt.show()


#print(result_sw_cb)
#print(sw_icb)

print(len(sw_cb))
print(len(sw_icb))

#        try:
#            for key, values in reg_dict.items():
#                if key == 'value0':
#                    val = re.findall(values, buffer).group(2)
#                val = re.search(values, buffer).group(2)
#                #print(val)
#                self.data[file].append(float(val))
#        except:
#            pass