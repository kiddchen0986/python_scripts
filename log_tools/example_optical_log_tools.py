# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 10:19:52 2017

@author: petter.ostlund
"""
import log_tools as lt
import matplotlib.pyplot as plt
import numpy as np

#path = r'C:\Logs\FPC1610_hana_micron_stage1_malmo_20181004\FT2NBSMFA'
path = r'C:\Logs\FPC1610_hana_micron_stage1_malmo_20181004\from_shanghai\1st 50 pieces log files_20181010'
path = r'C:\Logs\FPC1610_hana_micron_stage1_malmo_20181004\from_shanghai\50pcs_shanghai_drop2_20181012'

logs = lt.Optical() # Init logs object
data = logs(path) # Call function, arguments: rootdirector, sensor id

#print(data)

for keys, values in data.items():
    print(values)


test_results = np.zeros((5, len(data)))

cnt = 0
for keys, values in data.items():
    test_results[4,cnt] = values[4]
    cnt += 1
#
#print(test_results)
#
title = ", P1 Hana-Micron packages"
y_max = 10
n, bins, patches = plt.hist(test_results[4,:], 100, range=(50,90))
plt.title("Current measurement" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
#plt.plot([0, 0],[0, 100], 'r')
plt.ylabel("Number of measurements")
plt.xlabel("mA")
plt.show()

#-----------------------------
#number_of_modules = len(data_dict)
#print("Number of unique modules = ", number_of_modules )


#
#test_strings = ['snr', 'blobs', 'udr', 'uf', 'ss', 'rms', 'afd', 'def', 'otp', 'mqt2']
#



#snr_pass  = len([x for x in test_results[:,0,1] if x > 15.0])
#snr_total = len([x for x in test_results[:,0,1]]) # if x != -1000])
#snr_yield = snr_pass/snr_total
#print("SNR yield = {0:0.4f}, ({1}/{2})".format(snr_yield, snr_pass, snr_total))
#
#
##blob_fail  = len([x for x in test_results[:,1,0] if x > 7])
##blob_total = len([x for x in test_results[:,1,0] if x != -1000])
##blobs_yield = 1 - blob_fail/blob_total
##print("Blobs yield = {0:0.4f}, (1-{1}/{2})".format(blobs_yield, blob_fail, blob_total))
##
#
#udr_pass  = len([x for x in test_results[:,2,1] if x > 0.25])
#udr_total = len([x for x in test_results[:,2,1]]) # if x != -1000])
#udr_yield = udr_pass/udr_total
#print("UDR yield = {0:0.4f}, ({1}/{2})".format(udr_yield, udr_pass, udr_total))
#
#
##afd_pass  = len([x for x in test_results[:,6,1] if x == 1])
##afd_total = len([x for x in test_results[:,6,1] if x != -1000])
##afd_yield = afd_pass/afd_total
##print("Analog Finger Calibration yield = {0:0.4f}, ({1}/{2})".format(afd_yield, afd_pass, afd_total))
#
##
#def_pass  = len([x for x in test_results[:,7,1] if x == 1])
#def_total = len([x for x in test_results[:,7,1]]) # if x != -1000])
#def_yield = def_pass/def_total
#print("Defective Pixel yield = {0:0.4f}, ({1}/{2})".format(def_yield, def_pass, def_total))
#
#
#otp_pass  = len([x for x in test_results[:,8,1] if x == 1])
#otp_total = len([x for x in test_results[:,8,1]]) # if x != -1000])
#otp_yield = otp_pass/otp_total
#print("OTP Read yield = {0:0.4f}, ({1}/{2})".format(otp_yield, otp_pass, otp_total))
#
#
#mqt2_pass  = len([x for x in test_results[:,9,1] if x == 1])
#mqt2_total = len([x for x in test_results[:,9,1]])# if x != -1000])
#mqt2_yield = mqt2_pass/mqt2_total
#print("MQT2 yield = {0:0.4f}, ({1}/{2})".format(mqt2_yield, mqt2_pass, mqt2_total))
#
##fp_pass  = len([x for x in test_results[:,10,1] if x == 1])
##fp_total = len([x for x in test_results[:,10,1] if x != -1000])
##fp_yield = fp_pass/fp_total
##print("FP yield = {0:0.4f}, ({1}/{2})".format(fp_yield, fp_pass, fp_total))
#
#
#
## Values for plotting
#snr_values = test_results[:,0,1]  # Max
#blob_values = test_results[:,1,0] # Min
#udr_values = test_results[:,2,1] # Maxq
#uf_values = test_results[:,3,0] # Min
#ss_values = test_results[:,4,1] # Max
#rms_values = test_results[:,5,1] # Max
#fp_values = test_results[:,10,0] # Max
#
#
#print(len(snr_values))
##print("Signal strength", ss_values/1000)
#
#title = ", FPC1511-S, hwid=0x1012"
#
#y_max = 250
#n, bins, patches = plt.hist(snr_values, 100, range=(0,35))
#plt.title("SNR" + title)
#axis = plt.gca()
#axis.set_ylim([0, y_max])
##plt.plot([0, 0],[0, 100], 'r')
#plt.ylabel("Number of modules")
#plt.xlabel("SNR")
#plt.show()
#
#y_max = 250
#n, bins, patches = plt.hist(udr_values, 100, range=(0.85,1.0))
#plt.title("UDR" + title)
#axis = plt.gca()
#axis.set_ylim([0, y_max])
##plt.plot([0.0, 0.0],[0, 200], 'r')
#plt.ylabel("Number of modules")
#plt.xlabel("UDR")
#plt.show()
#
#y_max = 80
#n, bins, patches = plt.hist(rms_values, 100, range=(0,50))
#plt.title("RMS" + title)
#axis = plt.gca()
#axis.set_ylim([0, y_max])
#plt.ylabel("Number of modules")
#plt.xlabel("RMS")
#plt.show()
#
#y_max = 120
#n, bins, patches = plt.hist(uf_values, 100, range=(0,0.15))
#plt.title("Uniformity" + title)
#axis = plt.gca()
#axis.set_ylim([0, y_max])
#plt.ylabel("Number of modules")
#plt.xlabel("Uniformity")
#plt.show()
#
#y_max = 125
#n, bins, patches = plt.hist(ss_values/1000, 100, range=(0.2,0.7))
#plt.title("Signal strength" + title)
#axis = plt.gca()
#axis.set_ylim([0, y_max])
#plt.ylabel("Number of modules")
#plt.xlabel("Signal strength")
#plt.show()
#
#y_max = 200
#n, bins, patches = plt.hist(fp_values, 100, range=(0, 50))
#plt.title("FP pixels (min value)" + title)
#axis = plt.gca()
#axis.set_ylim([0, y_max])
#plt.plot([30, 30],[0, 200], 'r')
#plt.ylabel("Number of modules")
#plt.xlabel("Number of FP pixels")
#plt.show()
#
#fig, ax = plt.subplots()
#ax.plot(ss_values/1000, snr_values, '.')
#ax.set_title("SNR vs Signal strength" + title)
#ax.set_ylim([8, 35])
#ax.set_xlim([0.15, 0.85])
#ax.set_ylabel("SNR (dB)")
#ax.set_xlabel("Signal strength (fF)")
#plt.show()
#
#fig, ax = plt.subplots()
#ax.plot(uf_values, udr_values, '.')
#ax.set_title("UDR vs Uniformity" + title)
#ax.set_ylim([0.6, 1.05])
#ax.set_xlim([0.01, 0.15])
#ax.set_ylabel("UDR")
#ax.set_xlabel("Uniformity")
#plt.show()
#
#fig, ax = plt.subplots()
#ax.plot(rms_values, snr_values, '.')
#ax.set_title("SNR vs RMS" + title)
#ax.set_ylim([6, 35])
#ax.set_xlim([20, 50])
#ax.set_ylabel("SNR")
#ax.set_xlabel("RMS")
#plt.show()