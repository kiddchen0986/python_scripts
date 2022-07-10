# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 14:55:50 2017

@author: petter.ostlund
"""

import matplotlib.pyplot as plt
import log_tools as lt
import numpy as np


path = r'C:\Logs\FPC1291-G175_0x0E11_E1_black\e1 black PVT log\1007-00-MT'
#path = r'C:\Logs\FPC1291-G175_hwid=0x011_o-film_xiaomi'
#path = r'C:\Logs\FPC1291-G175_hwid=0x011_o-film_xiaomi\1007-00'
#path = r'C:\Logs\FPC1291-G175_hwid=0x011_o-film_xiaomi\1007-01'
#path = r'C:\Logs\FPC1291-G175_hwid=0x011_o-film_xiaomi\1007-02'
#path = r'C:\Logs\FPC1291-G175_hwid=0x011_o-film_xiaomi\1007-03'

logs = lt.MTTLogsHtml2()
logs(path)

data_dict = logs.get_data()
test_results = logs.get_min_max_mean_array()

number_of_modules = len(data_dict)
print("Number of unique logs = ", number_of_modules )


# Yield values (based on max values)
snr_succ = len([x for x in test_results[:,3,1] if x > 8.0])
snr_len = len([x for x in test_results[:,3,1] if x != -1000])
print("SNR yield (limit 8dB)  = ", snr_succ/snr_len, " logs = ", snr_len)

# Yield values (based on max values)
snr_yield = len([x for x in test_results[:,3,1] if x > 7.0])/\
    len([x for x in test_results[:,3,1] if x != -1000])
print("SNR yield (limit 7dB)  = ", snr_yield)

# Yield values (based on max values)
snr_yield = len([x for x in test_results[:,3,1] if x > 6.0])/\
    len([x for x in test_results[:,3,1] if x != -1000])
print("SNR yield (limit 6dB)  = ", snr_yield)

# Yield values (based on max values)
snr_yield = len([x for x in test_results[:,3,1] if x > 5.0])/\
    len([x for x in test_results[:,3,1] if x != -1000])
print("SNR yield (limit 5dB)  = ", snr_yield)

#uf_yield = 1 - len([x for x in test_results[:,0,0] if x > 0.10])/\
#    len([x for x in test_results[:,0,0] if x != -1000])
#print("uf yield (limit=10.0%) = ", uf_yield)

#ss_yield = 1 - len([x for x in test_results[:,1,0] if x > 1.55])/\
#    len([x for x in test_results[:,1,0] if x != -1000])
#print("ss yield = ", ss_yield)

blob_len =     len([x for x in test_results[:,2,0] if x != -1000])
blob_fail = len([x for x in test_results[:,2,0] if x > 7])
print("Blobs yield = ", 1-blob_fail/blob_len, " logs = ", blob_len)

afd_len = len([x for x in test_results[:,4,1] if x != -1000])
afd_succ = len([x for x in test_results[:,4,1] if x == 1.0])
print("AFD yield = ", afd_succ/afd_len, " logs = ", afd_len)

def_succ = len([x for x in test_results[:,5,1] if x == 1.0])
def_len = len([x for x in test_results[:,5,1] if x != -1000])
print("Defective Pixel yield = ", def_succ/def_len, " logs = ", def_len)

# UDR yield
udr_succ = len([x for x in test_results[:,7,1] if x > 0.25])
udr_len = len([x for x in test_results[:,7,1] if x != -1000])
print("UDR yield (limit 0.25)  = ", udr_succ/udr_len, " logs = ", udr_len)


# Total yield
tot_succ = len([x for x in test_results[:,9,1] if x == 1.0])
tot_len = len([x for x in test_results[:,9,1] if x != -1000])
print("Total yield  = ", tot_succ/tot_len, " logs = ", tot_len)

# Mean values for plotting, test_strings = ['uf', 'ss', 'blobs', 'snr', 'afd', 'def', 'otp', 'udr', 'rms', 'tot']
snr_values = test_results[:,3,2]
uf_values = test_results[:,0,0]
ss_values = test_results[:,1,2]
blob_values = test_results[:,2,0]
snr_values = test_results[:,3,1]
afd_values = test_results[:,4,1]
def_values = test_results[:,5,1]
otp_values = test_results[:,6,1]
udr_values = test_results[:,7,1]
rms_values = test_results[:,8,1]
tot_values = test_results[:,9,1]



#print(np.min(test_results[:,3,2]))
#print(np.max(test_results[:,3,2]))

title = ', FPC1291-G175, hwid=0x0E11, O-film, Xiaomi'

y_max = 70
n, bins, patches = plt.hist(snr_values, 100, range=(0,17))
plt.title("SNR" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("SNR")
plt.show()


y_max = 70
n, bins, patches = plt.hist(udr_values, 100, range=(0,1))
plt.title("UDR" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("UDR")
plt.show()

y_max = 70
n, bins, patches = plt.hist(rms_values, 100, range=(0,30))
plt.title("RMS" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("RMS")
plt.show()


y_max = 100
n, bins, patches = plt.hist(uf_values, 100, range=(0.0,0.16))
plt.title("Uniformity" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("Uniformity")
plt.show()

y_max = 200
n, bins, patches = plt.hist(ss_values, 100, range=(0,0.6))
plt.title("Signal strength" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("Signal strength")
plt.show()

y_max = 10
n, bins, patches = plt.hist(blob_values, 100, range=(0,50))
plt.title("Blobs" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("Number of blobs")
plt.show()

fig, ax = plt.subplots()
ax.plot(rms_values, snr_values, 'o')
ax.set_title("SNR vs RMS" + title)
ax.set_xlim([0, 30])
ax.set_ylim([0, 17])
#plt.plot([0, 1.1],[12.5, 12.5], 'r')
#plt.plot([1.1, 1.1],[12.5, 20], 'r')
ax.set_ylabel("SNR (dB)")
ax.set_xlabel("RMS")
plt.show()

fig, ax = plt.subplots()
ax.plot(uf_values, snr_values, 'o')
ax.set_title("SNR vs uniformity" + title)
ax.set_ylim([0, 17])
ax.set_xlim([0, 0.15])
ax.set_ylabel("SNR (dB)")
ax.set_xlabel("Uniformity")
plt.show()

fig, ax = plt.subplots()
ax.plot(ss_values, snr_values, 'o')
ax.set_title("SNR vs signal strength" + title)
ax.set_ylim([0, 17])
ax.set_xlim([0, 0.6])
ax.set_ylabel("SNR (dB)")
ax.set_xlabel("Signal strength (fF)")
plt.show()

fig, ax = plt.subplots()
ax.plot(udr_values, snr_values, 'o')
ax.set_title("SNR vs UDR" + title)
ax.set_ylim([0, 17])
ax.set_xlim([0, 1])
ax.set_ylabel("SNR (dB)")
ax.set_xlabel("UDR")
plt.show()
