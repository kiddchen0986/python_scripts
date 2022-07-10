# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 14:23:42 2018

@author: petter.ostlund
"""

import os
from fnmatch import fnmatch
import optical_production_tests as opt
import matplotlib.pyplot as plt
import numpy as np
import skimage as si

# Folder where images are
#root_dir = r'C:\python_scripts2\python_scripts\optical\testimage'
#root_dir = r'C:\python_scripts2\python_scripts\optical\from_hanna\pre_HTS test 2.81V battery'
#root_dir = r'C:\python_scripts2\python_scripts\optical\from_hanna\postHTS test 65hrs 150C 2.83V battery'

#root_dir = r'C:\python_scripts2\python_scripts\optical\from_hanna\bad_contrast_module_20181022'

# Plasma_cleaned
#root_dir = r'C:\python_scripts2\python_scripts\optical\from_hanna\plasma_cleaned'

# 250h in 150 degrees
#root_dir = r'C:\python_scripts2\python_scripts\optical\from_hanna\MTT results 250 hrs @ 150 degrees_P1'

# All measurements from Hanna
#root_dir = r'C:\python_scripts2\python_scripts\optical\from_hanna'

# From Hana-Micron
#root_dir = r'C:\Logs\FPC1610_hana_micron_20181106\5A_A_X_strip_MTT_v181029'

# From Hana-Micron 2018-11-15
#root_dir = r'C:\Logs\FPC1610_Hana_micron_2018-11-15\5A_new_settings_TC(-55_to_125)_new_LED'

# From Hana-Micron 2018-11-16
#root_dir = r'C:\Logs\FPC1610_hana_micron_20181116'

# From Hana-Micron 2018-11-21
#root_dir = r'C:\Logs\FPC1610_hana_micron_20181121'

# From Hana-Micron 2018-11-27
#root_dir = r'C:\Logs\FPC1610_hana_micron_20181127\3A_TC(-50_to_150)'

# From Hana-Micron 2018-11-27
#root_dir = r'C:\Logs\FPC1610_hana_micron_20181127\3A_TC(-40_to_85)'

# From Hana-Micron 2018-11-29
root_dir = r'C:\Logs\FPC1610_hana_micron_20181129\3A_HTSL_+85'
root_dir = r'C:\Logs\FPC1610_hana_micron_20181129\3A_HTSL_+125'
root_dir = r'C:\Logs\FPC1610_hana_micron_20181129\3A_HTSL_+150'

filelist = []
for path, subdirs, files in os.walk(root_dir):
    for name in files:
        if fnmatch(name, '*CapturedImage.png'):
            filelist.append(os.path.join(path, name))
filelist.sort()


def plot_data(data, ymin, ymax, xlabel, ylabel, title):
        plt.plot(data)
        _min = np.min(data)
        _max = np.max(data)
        _mean = np.mean(data)
        print("Mean sigma =", _mean)
        plt.title(title)
        plt.plot([0, no], [_min, _min], 'r--')
        plt.plot([0, no], [_max, _max], 'r--')
        plt.plot([0, no], [_mean, _mean], 'b-')
        ax = plt.gca()
        ax.set_xlim([0, no])
        ax.set_ylim([ymin, ymax])
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.show()


# Create a list with sub lists with all data
summary = []

# Run Gaussian fit for images
for file in filelist:
    print("\n\nFilename: ",file)
    with open(file, 'r') as f:
        im_in = si.io.imread(file)
        print(im_in.dtype)
        print(im_in.shape)
        #sub_im, im_vis = opt.extractSubImagesCropped(im_in)
        sub_im, im_vis = opt.extractSubImages(im_in)
        #plt.imshow(im_vis)
        #plt.show()
        #plt.imsave("testing.png", im_vis, cmap='gray')

        (side_x, side_y, no) = sub_im.shape
        lens_data = np.zeros((5, no)) # No sub = 222 in OV2710
        print(no)

        for ii in range(no):
            params = opt.fitgaussian(sub_im[:,:,ii])
            fit = opt.gaussian(*params)
            lens_data[:,ii] = params
            #print(params)

        summary.append([file,
                        np.mean(lens_data[0,:]),
                        np.mean(lens_data[1,:]),
                        np.mean(lens_data[2,:]),
                        np.mean(lens_data[3,:]),
                        np.mean(lens_data[4,:]),
                        np.mean(lens_data[3,:])/np.mean(lens_data[0,:]),
                        np.mean(lens_data[4,:])/np.mean(lens_data[0,:])])

        # Plot the intensity
        plot_data(lens_data[0,:], 0, 260, "Sub_image", "Value", "Amplitude")
#
#        # Plot variation in x width
#        plot_data(lens_data[3,:], 20, 24, "Sub_image", "Standard deviation",\
#                  "Image width in x-direction")
#
#        # Plot variation in y width
#        plot_data(lens_data[4,:], 20, 24, "Sub_image", "Standard deviation",\
#                  "Image width in y-direction")
#
#        # Plot width difference for each sub image.
#        plot_data(np.abs(np.subtract(lens_data[3,:], lens_data[4,:])),\
#                  0, 1.2, "Sub image", "Abs value",\
#                  "Width difference, abs(sigma_x - sigma_y)", )

        # Plot sigma_x normalized with amplitude
        plot_data(np.divide(lens_data[3,:], lens_data[0,:]), 0.02, 0.21,\
                  "Sub image", "$\sigma_x/A$", "Normalized x-width")
        
        # Plot sigma_x normalized with amplitude
        plot_data(np.divide(lens_data[4,:], lens_data[0,:]), 0.02, 0.21,\
                  "Sub image", "$\sigma_y/A$", "Normalized y-width")




# Create csv-file with all the data
with open("test_data.csv", 'w') as f:
    title = "File name" + ";" + "A_mean" + ";" + "x0" + ";" + "y0" + ";" +\
            "sigma_x" + ";" + "sigma_y"+ ";" + "sigma_x/A" + ";" + "sigma_y/A\n"
    f.write(title)
    for d in summary:
        f.write("{0}; {1:.1f}; {2:.3f}; {3:.3f}; {4:.3f}; {5:.3f}; {6:.3f}; {7:.3f}"
              .format(d[0][37:], d[1], d[2], d[3], d[4], d[5], d[6], d[7]))
        f.write("\n")
