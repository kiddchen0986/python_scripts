# -*- coding: utf-8 -*-
"""
Created on Fri Apr  6 11:25:48 2018

@author: petter.ostlund@fingerprints.com
"""

# Parses txt files from static MQT and saves the SNR, blobs and UDR in 
# a csv file

import os
import re
from fnmatch import fnmatch
import numpy as np
import matplotlib.pyplot as plt

# Path to logs
rootdir = r'C:\Logs\FPC1321_nedcard_20180406\24932AB1'
pattern = "*_log.txt"

filelist = []
# List all files below "root" directory
for path, subdirs, files in os.walk(rootdir):
    for name in files:
        if fnmatch(name, pattern):
            filelist.append(os.path.join(path, name))

results = []

for file in filelist:
    with open(file) as f:
        buffer = f.read()
    
    try:
        snr = re.search('(SNR\(db\): )(\d+\.\d+)', buffer).group(2)
    except:
        snr = -1
    try:
        blobs = re.search('(Blob count: )(\d+)', buffer).group(2)
    except:
        blobs = -1
    try:
        udr = re.search('(UDR: )(\d+\.\d+)', buffer).group(2)
    except:
        udr = -1
    results.append([file, snr, blobs, udr])

# Create numpy array for yield and histograms
data = np.asarray(results)[:,1:4].astype(float)

# Number of modules which had snr-value
print("Number of modules with snr value = ", len([x for x in data[:,0] if x > -1]))

snr_yield = len([x for x in data[:,0] if x >= 10]) / len([x for x in data[:,0] if x > -1])
print("SNR yield = ", snr_yield)

blob_limit = [7,8,9,10,11,12,13,14,15,16,17,18,19,20]
for limit in blob_limit:
    print("Blob limit = ", limit)
    blob_yield = 1 - len([x for x in data[:,1] if x > limit]) / len([x for x in data[:,1] if x > -1])
    print("Blob yield = ", blob_yield)

udr_yield = len([x for x in data[:,2] if x > 0.25]) / len([x for x in data[:,2] if x > -1])
print("UDR yield = ", udr_yield)

# Plot histograms
title = ', FPC1321 Nedcard, reel "24932AB1"'
y_max = 45
n, bins, patches = plt.hist(data[:,0], 100, range=(4,18))
plt.title("SNR" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.plot([10, 10],[0, 100], 'r')
plt.ylabel("Number of modules")
plt.xlabel("SNR")
plt.show()

y_max = 60
n, bins, patches = plt.hist(data[:,1], 100, range=(0,50))
plt.title("Blobs" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.plot([7.5, 7.5],[0, 200], 'r')
plt.ylabel("Number of modules")
plt.xlabel("Number of blobs")
plt.show()

y_max = 350
n, bins, patches = plt.hist(data[:,2], 100, range=(0,1))
plt.title("UDR" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.plot([0.25, 0.25],[0, 350], 'r')
plt.ylabel("Number of modules")
plt.xlabel("UDR")
plt.show()

# Write results to csv file
with open("log_summary.csv", 'w') as f:
    f.write("Filename;SNR;Blobs;UDR\n")
    for test in results:
        res = test[0]+';'+str(test[1])+';'+str(test[2])+';'+str(test[3])+'\n'
        f.write(res)
        
        
