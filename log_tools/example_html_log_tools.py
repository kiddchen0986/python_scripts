# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 14:55:50 2017

@author: petter.ostlund
"""

import matplotlib.pyplot as plt
import log_tools as lt
import numpy as np

#path = r'C:\jira\prodp-300\881log\881log\0881-60-MT'
#path = r'C:\jira\paris-8\0950第一次测试LOG-20171222'
# 1, path = r'C:\jira\AC-81\Ofilm log-FPC1228-G175 & G175+\Ofilm log-FPC1228-G175 & G175+\1\FTW-0887-60-MT-linshi'
# 2, path = r'C:\jira\AC-81\Ofilm log-FPC1228-G175 & G175+\Ofilm log-FPC1228-G175 & G175+\2\FTW-0887-60-MT-linshi'
# 3, path = r'C:\jira\AC-81\Ofilm log-FPC1228-G175 & G175+\Ofilm log-FPC1228-G175 & G175+\3\FTW-0887-60-MT-linshi'
# 4, path = r'C:\jira\AC-81\Ofilm log-FPC1228-G175 & G175+\Ofilm log-FPC1228-G175 & G175+\4\FTW-0887-60-MT-linshi'
# 5, path = r'C:\jira\AC-81\Ofilm log-FPC1228-G175 & G175+\Ofilm log-FPC1228-G175 & G175+\5\FTW-0887-60-MT-linshi'

#path = r'C:\jira\AC-81\Ofilm log-FPC1228-G175 & G175+\Ofilm log-FPC1228-G175 & G175+\6\FTW-0887-60-MT-linshi'
#path = r'C:\jira\paris-13\FPC-SNR'

#path = r'C:\jira\ccb-263\1023+logo Matt surface_log 20180308\1021-00-OQC'
path = r'C:\Logs\1228_oppo_20180309\Score test fail'
#path = r'C:\Logs\1228_oppo_20180309\Score test pass'

logs = lt.MTTLogsHtml()
logs(path)

data_dict = logs.get_data()
test_results = logs.get_min_max_mean_array()

number_of_modules = len(data_dict)
print("Number of unique logs = ", number_of_modules )


# Yield values (based on max values)
snr_yield = len([x for x in test_results[:,3,1] if x > 8.0])/\
    len([x for x in test_results[:,3,1] if x != -1000])
print("SNR yield = ", snr_yield)


#afd_yield = len([x for x in test_results[:,4,1] if x == 1.0])/\
#len([x for x in test_results[:,4,1] if x != -1000])
#print("AFD yield = ", afd_yield)

#uf_yield = 1 - len([x for x in test_results[:,0,0] if x > 0.10])/\
#    len([x for x in test_results[:,0,0] if x != -1000])
#print("uf yield (limit=10.0%) = ", uf_yield)

#ss_yield = 1 - len([x for x in test_results[:,1,0] if x > 1.55])/\
#    len([x for x in test_results[:,1,0] if x != -1000])
#print("ss yield = ", ss_yield)

#blobs_yield = 1 - len([x for x in test_results[:,2,0] if x > 7])/\
#    len([x for x in test_results[:,2,0] if x != -1000])
#print("Blobs yield = ", blobs_yield)

dead_pixel_yield = len([x for x in test_results[:,5,1] if x == 1.0])/\
len([x for x in test_results[:,5,1] if x != -1000])
print("Dead pixel yield = ", dead_pixel_yield)

# Mean values for plotting
snr_values = test_results[:,3,2]
uf_values = test_results[:,0,0]
ss_values = test_results[:,1,2]
blob_values = test_results[:,2,0]

print(np.min(test_results[:,3,2]))
print(np.max(test_results[:,3,2]))

title = ', FPC1228 O-film, Oppo, "Score test fail"'

y_max = 12
n, bins, patches = plt.hist(snr_values, 100, range=(0,20))
plt.title("SNR" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("SNR")
plt.show()


y_max = 12
n, bins, patches = plt.hist(uf_values, 100, range=(0.02,0.16))
plt.title("Uniformity" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("Uniformity")
plt.show()

y_max = 12
n, bins, patches = plt.hist(ss_values, 100, range=(0.3,1.7))
plt.title("Signal strength" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("Signal strength")
plt.show()

y_max = 12
n, bins, patches = plt.hist(blob_values, 100, range=(0,20))
plt.title("Blobs" + title)
axis = plt.gca()
axis.set_ylim([0, y_max])
plt.ylabel("Number of modules")
plt.xlabel("Number of blobs")
plt.show()

fig, ax = plt.subplots()
ax.plot(ss_values, snr_values, 'o')
ax.set_title("SNR vs Signal strength" + title)
ax.set_ylim([8, 20])
ax.set_xlim([0.3, 1.6])
plt.plot([0, 1.1],[12.5, 12.5], 'r')
plt.plot([1.1, 1.1],[12.5, 20], 'r')
ax.set_ylabel("SNR (dB)")
ax.set_xlabel("Signal strength (fF)")
plt.show()

fig, ax = plt.subplots()
ax.plot(uf_values, snr_values, 'o')
ax.set_title("SNR vs uniformity" + title)
ax.set_ylim([8, 20])
ax.set_xlim([0, 0.18])
ax.set_ylabel("SNR (dB)")
ax.set_xlabel("Uniformity")
plt.show()

