# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 10:19:52 2017

@author: petter.ostlund
"""
import log_tools as lt
import matplotlib.pyplot as plt

# Example/test code
#path = r'C:\Logs\FPC1291-G175_E1_P1_3_20171212\0895-01-MT'
#path = r'C:\Logs\FPC1291-G175_Ofilm_Xiaomi_20171127\1291-G175_ofilm_stage3_20171127'
#path = r'C:\Logs\FPC1291-G175_Ofilm_Xiaomi_20171127\1291-G175_ofilm_stage3_20171127\0836-04-MT-LOG-11-24-E1_white_glass'
#path = r'C:\Logs\FPC1291-G175_Ofilm_Xiaomi_20171127\1291-G175_ofilm_stage3_20171127\0836-06-MT-LOG-11-23-E1_black_glass'
#path = r'C:\jira\neo-29\F0138 LOG 1-24'
#path = r'C:\jira\prodp-321\DVT1Alog\FT1ME83Q'
#path = r'C:\jira\prodp-324\20180205'
#path = r'C:\jira\prodp-324\20180208'
#path = r'C:\jira\neo-49\61642'
path = r'C:\jira\tools-4573\1291-Z120-Ref'

logs = lt.MTTLogsMQT2() # Init logs object
logs(path, True) # Call function, arguments: rootdirector, sensor id
data_dict = logs.get_data()
test_results = logs.get_min_max_mean_array()


number_of_modules = len(data_dict)
print("Number of unique modules = ", number_of_modules )


#
#test_strings = ['snr', 'blobs', 'udr', 'uf', 'ss', 'rms', 'afd', 'def', 'otp', 'mqt2']
#



snr_pass  = len([x for x in test_results[:,0,1] if x > 5.0])
snr_total = len([x for x in test_results[:,0,1] if x != -1000])
snr_yield = snr_pass/snr_total
print("SNR yield = {0:0.4f}, ({1}/{2})".format(snr_yield, snr_pass, snr_total))


blob_fail  = len([x for x in test_results[:,1,0] if x > 7])
blob_total = len([x for x in test_results[:,1,0] if x != -1000])
blobs_yield = 1 - blob_fail/blob_total
print("Blobs yield = {0:0.4f}, (1-{1}/{2})".format(blobs_yield, blob_fail, blob_total))


udr_pass  = len([x for x in test_results[:,2,1] if x > 0.25])
udr_total = len([x for x in test_results[:,2,1] if x != -1000])
udr_yield = udr_pass/udr_total
print("UDR yield = {0:0.4f}, ({1}/{2})".format(udr_yield, udr_pass, udr_total))


afd_pass  = len([x for x in test_results[:,6,1] if x == 1])
afd_total = len([x for x in test_results[:,6,1] if x != -1000])
afd_yield = afd_pass/afd_total
print("Analog Finger Calibration yield = {0:0.4f}, ({1}/{2})".format(afd_yield, afd_pass, afd_total))


def_pass  = len([x for x in test_results[:,7,1] if x == 1])
def_total = len([x for x in test_results[:,7,1] if x != -1000])
def_yield = def_pass/def_total
print("Defective Pixel yield = {0:0.4f}, ({1}/{2})".format(def_yield, def_pass, def_total))


otp_pass  = len([x for x in test_results[:,8,1] if x == 1])
otp_total = len([x for x in test_results[:,8,1] if x != -1000])
otp_yield = otp_pass/otp_total
print("OTP Read yield = {0:0.4f}, ({1}/{2})".format(otp_yield, otp_pass, otp_total))


mqt2_pass  = len([x for x in test_results[:,9,1] if x == 1])
mqt2_total = len([x for x in test_results[:,9,1] if x != -1000])
mqt2_yield = mqt2_pass/mqt2_total
print("MQT2 yield = {0:0.4f}, ({1}/{2})".format(mqt2_yield, mqt2_pass, mqt2_total))


# Values for plotting
snr_values = test_results[:,0,1]  # Max
blob_values = test_results[:,1,0] # Min
udr_values = test_results[:,2,1] # Max
uf_values = test_results[:,3,0] # Min
ss_values = test_results[:,4,1] # Max
rms_values = test_results[:,5,1] # Max


print(len(snr_values))

title = ", FPC1291-G175, Lens Huawei, hwid=0x0E12"

y_max = 65
n, bins, patches = plt.hist(snr_values, 100, range=(4,20))
plt.title("SNR" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.plot([8, 8],[0, 100], 'r')
plt.ylabel("Number of modules")
plt.xlabel("SNR")
plt.show()

y_max = 65
n, bins, patches = plt.hist(udr_values, 100, range=(0,1))
plt.title("UDR" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.plot([0.25, 0.25],[0, 200], 'r')
plt.ylabel("Number of modules")
plt.xlabel("UDR")
plt.show()

y_max = 45
n, bins, patches = plt.hist(rms_values, 100, range=(0,25))
plt.title("RMS" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("RMS")
plt.show()

y_max = 60
n, bins, patches = plt.hist(uf_values, 100, range=(0,0.15))
plt.title("Uniformity" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("Uniformity")
plt.show()

y_max = 80
n, bins, patches = plt.hist(ss_values, 100, range=(0.2,0.9))
plt.title("Signal strength" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("Signal strength")
plt.show()

fig, ax = plt.subplots()
ax.plot(ss_values, snr_values, '.')
ax.set_title("SNR vs Signal strength" + title)
ax.set_ylim([0, 18])
ax.set_xlim([0.2, 0.9])
ax.set_ylabel("SNR (dB)")
ax.set_xlabel("Signal strength (fF)")
plt.show()

fig, ax = plt.subplots()
ax.plot(uf_values, udr_values, '.')
ax.set_title("UDR vs Uniformity" + title)
ax.set_ylim([0, 1.0])
ax.set_xlim([0.01, 0.15])
ax.set_ylabel("UDR")
ax.set_xlabel("Uniformity")
plt.show()

