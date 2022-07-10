# -*- coding: utf-8 -*-
"""
Created on Thu Mar  8 09:18:43 2018

@author: petter.ostlund
"""

import numpy as np
import log_tools as lt
import matplotlib.pyplot as plt


#path = r'C:\Logs\FPC1321_nedcard_20180228\ForFPC2\testlog'
#path = r'C:\Logs\FPC1321_logs\MTT_ola_drop_20180320'
#path = r'C:\Logs\FPC1321_stage1_20180403\sven\1321-MTT15_1\2'
#path = r'C:\Logs\FPC1321_20180403\sven_rc2_20180403\1321-MTT15_1-RC2'
# stage1 MTT15.1 build 4224
#path = r'C:\Logs\FPC1321_mtt15_1_build4224_stage1\MTT-build-4224'
#path = r'C:\Logs\FPC1321_nedcard_20180406\24932AB1'
path =r'C:\Logs\FPC1321_nedcard_1up_20180413\share2fpc\testlog_1strun_with_setup'
#path = r'C:\Logs\FPC1321_nedcard_1up_20180413\share2fpc_2nd_run'

logs = lt.MTTLogsVaduzWrapper() # Init logs object
data = logs(path) # Call function, arguments: rootdirector, sensor id

# Put all values in a 3D array
no = len(data)
print('Number of static mqt without exception or not run = ', no)
values = np.zeros((no,8,7))

index = 0
for key, value in data.items():
    #print(key, value)
    values[index, :,:] = value
    index += 1

# Collect data for the profiles and the tests

#p0_snr = values[:,0,0]
#print(p0_snr)
#p0_blob = values[:,0,1]
#print(p0_blob)
#p0_udr = values[:,0,2]
#print(p0_udr)

# Plot snr, blob and udr for each profile
#for i in range(8):
#    snr_values = values[0::2,i,0]
#    title = ' profile_'+str(i)
#    y_max = 50
#    n, bins, patches = plt.hist(snr_values, 100, range=(4,18))
#    plt.title("SNR" + title)
#    axis = plt.gca()
#    axis.set_ylim([0, y_max])
#    plt.plot([8, 8],[0, 100], 'r')
#    plt.ylabel("Number of modules")
#    plt.xlabel("SNR")
#    plt.show()
#    
#    blob_values = values[0::2,i,1]
#    y_max = 50
#    n, bins, patches = plt.hist(blob_values, 100, range=(0,50))
#    plt.title("Blobs" + title)
#    axis = plt.gca()
#    axis.set_ylim([0, y_max])
#    plt.ylabel("Number of modules")
#    plt.xlabel("Number of blobs")
#    plt.show()
#    
#    udr_values = values[0::2,i,2]
#    y_max = 50
#    n, bins, patches = plt.hist(udr_values, 100, range=(0,1))
#    plt.title("UDR" + title)
#    axis = plt.gca()
#    axis.set_ylim([0, y_max])
#    plt.plot([0.25, 0.25],[0, 200], 'r')
#    plt.ylabel("Number of modules")
#    plt.xlabel("UDR")
#    plt.show()


# Find values based on profile with highest SNR

print(values.shape)

max_snr_position = []
values_max_snr = np.zeros((no,7))
for i in range(no):
    pos = values[i,:,0].argmax(axis=0)
    max_snr_position.append(pos)
    values_max_snr[i,:] = values[i,pos,:]
    
#print(values_max_snr)
#for x in range(no):
#    print(values_max_snr[x,:])

print("Number of tests with SNR value = ", len(values_max_snr[:,0]))

#print(max_snr_position)
title = 'Profile with highest SNR'
y_max = 450
n, bins, patches = plt.hist(max_snr_position, 100, range=(0,7))
plt.title(title)
axis = plt.gca()
axis.set_ylim([0, y_max])
#plt.plot([8, 8],[0, 100], 'r')
plt.ylabel("Profile count")
plt.xlabel("Profile")
plt.show()

# SNR highest, [snr, blob, udr, uf, ss, rms] 
title = 'SNR (highest SNR)'
y_max = 160
n, bins, patches = plt.hist(values_max_snr[:,0], 100, range=(4,18))
plt.title(title)
axis = plt.gca()
plt.plot([10, 10],[0, 1000], 'r')
axis.set_ylim([0, y_max])
#plt.plot([8, 8],[0, 100], 'r')
plt.ylabel("Modules/Tests")
plt.xlabel("SNR (dB)")
plt.show()

title = 'UDR (highest SNR)'
y_max = 550
n, bins, patches = plt.hist(values_max_snr[:,2], 100, range=(0,1))
plt.title(title)
axis = plt.gca()
plt.plot([0.25, 0.25],[0, 1000], 'r')
axis.set_ylim([0, y_max])
#plt.plot([8, 8],[0, 100], 'r')
plt.ylabel("Modules/Tests")
plt.xlabel("UDR")
plt.show()

title = 'Blobs (highest SNR)'
y_max = 70
n, bins, patches = plt.hist(values_max_snr[:,1], 100, range=(0,50))
plt.title(title)
axis = plt.gca()
plt.plot([7, 7],[0, 1000], 'r')
axis.set_ylim([0, y_max])
#plt.plot([8, 8],[0, 100], 'r')
plt.ylabel("Modules/Tests")
plt.xlabel("Blobs")
plt.show()

title = 'Uniformity (highest SNR)'
y_max = 70
n, bins, patches = plt.hist(values_max_snr[:,3], 100, range=(0,0.15))
plt.title(title)
axis = plt.gca()
axis.set_ylim([0, y_max])
#plt.plot([8, 8],[0, 100], 'r')
plt.ylabel("Modules/Tests")
plt.xlabel("Uniformity")
plt.show()

title = 'Signal strength (highest SNR)'
y_max = 200
n, bins, patches = plt.hist(values_max_snr[:,4], 100, range=(0,0.5))
plt.title(title)
axis = plt.gca()
axis.set_ylim([0, y_max])
#plt.plot([8, 8],[0, 100], 'r')
plt.ylabel("Modules/Tests")
plt.xlabel("Signal strength (fF)")
plt.show()

title = 'RMS (highest SNR)'
y_max = 150
n, bins, patches = plt.hist(values_max_snr[:,5], 100, range=(0,30))
plt.title(title)
axis = plt.gca()
axis.set_ylim([0, y_max])
#plt.plot([8, 8],[0, 100], 'r')
plt.ylabel("Modules/Tests")
plt.xlabel("RMS (Root Mean Square)")
plt.show()


blob_limit = [7] #, 8, 9, 10, 11, 12, 13,14,15,16,17,18,19,20]
for limit in blob_limit:
    print("Blob limit = ", limit)
    blob_fail = len([x for x in values_max_snr[:,1] if x > limit])
    blob_len = len([x for x in values_max_snr[:,1] if x != -1000])
    print("Blob yield = ", 1-blob_fail/blob_len, " (", blob_len - blob_fail, "/", blob_len, ")")

snr_succ = len([x for x in values_max_snr[:,0] if x > 10])
snr_len = len([x for x in values_max_snr[:,0] if x != -1000])
print("SNR yield = ", snr_succ/snr_len, " (", snr_succ, "/", snr_len, ")")

udr_succ = len([x for x in values_max_snr[:,2] if x > 0.25])
udr_len = len([x for x in values_max_snr[:,2] if x != -1000])
print("UDR yield = ", udr_succ/udr_len, " (", udr_succ, "/", udr_len, ")")

stamp_succ = len([x for x in values_max_snr[:,6] if x == 1])
stamp_len = len([x for x in values_max_snr[:,6] if x != -1000])
print("Stamp test yield = ", stamp_succ/stamp_len, " (", stamp_succ, "/", stamp_len, ")")

