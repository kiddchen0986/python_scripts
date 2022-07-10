#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 16:05:38 2017

@author: petter.ostlund
"""

import log_tools as lt
import matplotlib.pyplot as plt



# Example/test code
path = r'C:\Logs\FPC1228_primax_oppo_120zr_prodp-187\primax_logs'


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
print("SNR yield = ", snr_yield)


afd_yield = len([x for x in test_results[:,4,1] if x == 1.0])/\
len([x for x in test_results[:,4,1] if x != -1000])
print("AFD yield = ", afd_yield)

uf_yield = 1 - len([x for x in test_results[:,0,0] if x > 0.15])/\
    len([x for x in test_results[:,0,0] if x != -1000])
print("uf yield = ", uf_yield)

ss_yield = 1 - len([x for x in test_results[:,1,0] if x > 1.55])/\
    len([x for x in test_results[:,1,0] if x != -1000])
print("ss yield = ", ss_yield)

blobs_yield = 1 - len([x for x in test_results[:,2,0] if x > 14])/\
    len([x for x in test_results[:,2,0] if x != -1000])
print("Blobs yield = ", blobs_yield)



#dead_pixel_yield = len([x for x in test_results[:,5,1] if x == 1.0])/\
#len([x for x in test_results[:,5,1] if x != -1000])
#print("Dead pixel yield = ", dead_pixel_yield)

# Mean values for plotting
snr_values = test_results[:,3,1]
uf_values = test_results[:,0,0]
ss_values = test_results[:,1,2]
blob_values = test_results[:,2,0]

print(len(snr_values))

y_max = 160
n, bins, patches = plt.hist(snr_values, 100, range=(5,20))
plt.title("SNR, FPC1264 , O-film, hwid=0x0311")
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("SNR")
plt.show()


y_max = 50
n, bins, patches = plt.hist(uf_values, 100, range=(0.02,0.16))
plt.title("Uniformity,FPC1264, O-film, hwid=0x0311")
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("Uniformity")
plt.show()

y_max = 140
n, bins, patches = plt.hist(ss_values, 100, range=(0.3,1.7))
plt.title("Signal strength, FPC1264 , O-film, hwid=0x0311")
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("Signal strength")
plt.show()

y_max = 30
n, bins, patches = plt.hist(blob_values, 100, range=(0,20))
plt.title("Blobs, FPC1264 , O-film, hwid=0x0311")
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("Number of blobs")
plt.show()

fig, ax = plt.subplots()
ax.plot(ss_values, snr_values, 'o')
ax.set_title("SNR vs Signal strength, FPC1264 , O-film")
ax.set_ylim([8, 20])
ax.set_xlim([0.3, 1.6])
ax.set_ylabel("SNR (dB)")
ax.set_xlabel("Signal strength (fF)")
plt.show()



