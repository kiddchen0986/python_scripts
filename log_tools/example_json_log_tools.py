#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 16:05:38 2017

@author: petter.ostlund
"""

import log_tools as lt
import matplotlib.pyplot as plt



# Example/test code
#path = r'C:\Logs\FPC1228_primax_oppo_120zr_prodp-187\primax_logs'
#path = r'C:\Logs\FPC1261-S_20180124\crucaltec_stage2'
#path = r'C:\jira\prodp-312\20180116\DM1XTGOK'
#path = r'C:\jira\dd-15\1228-G175-Oppo'
#path = r'C:\jira\dd-23\FT2B6PY4'
#path = r'C:\Logs\FPC1321_logs\MTT log files_NXP build 4.5K (CP09)'
#path = r'C:\Logs\FPC1321_logs\MTT Logs_CP09_qual build_500 pcs'
#path = r'C:\Logs\FPC1321_logs\MTT Logs_Idemia ES1_3K (CP17)'
#path = r'C:\jira\fmt-54\Huawei_FPC1267_MTT12.0_testlogs_results'
path = r'C:\Logs\FPC1228_fpc2060_evaluate\MTT_MQT_LOG_FT1K823J_fpc1228_fpc2060_g175'

logs = lt.MTTLogsJson()
logs(path, True)

data_dict = logs.get_data()
test_results = logs.get_min_max_mean_array()

number_of_modules = len(data_dict)
print("Number of unique logs = ", number_of_modules )

cap_yield = len([x for x in test_results[:,7,1] if x == 1])/\
    len([x for x in test_results[:,7,1] if x != -1000])
print("cap yield = ", cap_yield)

# Yield values (based on max values)
snr_yield = len([x for x in test_results[:,3,1] if x > 8.0])/\
    len([x for x in test_results[:,3,1] if x != -1000])
print("SNR yield = ", snr_yield, ", Number of logs = ", len([x for x in test_results[:,3,1] if x != -1000]))


afd_yield = len([x for x in test_results[:,4,1] if x == 1.0])/\
len([x for x in test_results[:,4,1] if x != -1000])
print("AFD yield = ", afd_yield)

uf_yield = 1 - len([x for x in test_results[:,0,0] if x > 0.10])/\
    len([x for x in test_results[:,0,0] if x != -1000])
print("uf yield = ", uf_yield, ", Number of logs = ", len([x for x in test_results[:,0,0] if x != -1000]))

ss_yield = 1 - len([x for x in test_results[:,1,0] if x < 0.2])/\
    len([x for x in test_results[:,1,0] if x != -1000])
print("ss yield = ", ss_yield, ", Number of logs = ", len([x for x in test_results[:,1,0] if x != -1000]))

blobs_yield = 1 - len([x for x in test_results[:,2,0] if x > 7])/\
    len([x for x in test_results[:,2,0] if x != -1000])
print("Blobs yield = ", blobs_yield, ", Number of logs = ", len([x for x in test_results[:,2,0] if x != -1000]))



dead_pixel_yield = len([x for x in test_results[:,5,1] if x == 1.0])/\
len([x for x in test_results[:,5,1] if x != -1000])
print("Dead pixel yield = ", dead_pixel_yield)

# Mean values for plotting
snr_values = test_results[:,3,1]
uf_values = test_results[:,0,0]
ss_values = test_results[:,1,0]
blob_values = test_results[:,2,0]

print(len(snr_values))

title = ", FPC1228 2060, G175"

y_max = 5
n, bins, patches = plt.hist(snr_values, 100, range=(5,14))
plt.title("SNR" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("SNR")
plt.show()


y_max = 5
n, bins, patches = plt.hist(uf_values, 100, range=(0.01,0.13))
plt.title("Uniformity" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("Uniformity")
plt.show()

y_max = 20
n, bins, patches = plt.hist(ss_values, 100, range=(0.3, 1.35))
plt.title("Signal strength" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("Signal strength")
plt.show()

y_max = 8
n, bins, patches = plt.hist(blob_values, 100, range=(0,25))
plt.title("Blobs" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("Number of blobs")
plt.show()

fig, ax = plt.subplots()
ax.plot(ss_values, snr_values, 'o')
ax.set_title("SNR vs Signal strength" + title)
ax.set_ylim([5, 23])
ax.set_xlim([0.1, 0.5])
ax.set_ylabel("SNR (dB)")
ax.set_xlabel("Signal strength (fF)")
plt.show()

fig, ax = plt.subplots()
ax.plot(uf_values, snr_values, 'o')
ax.set_title("SNR vs Uniformity" + title)
ax.set_ylim([5, 14])
ax.set_xlim([0.01, 0.08])
ax.set_ylabel("SNR (dB)")
ax.set_xlabel("Signal strength (fF)")
plt.show()



