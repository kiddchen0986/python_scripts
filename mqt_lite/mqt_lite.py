# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 14:36:06 2018

@author: petter.ostlund
"""

import os
import numpy as np
import skimage as si
import matplotlib.pyplot as plt

def calcRMS(image):
    return np.std(image.flatten())


def calcP2P(image):
    return np.max(image.flatten()) - np.min(image.flatten())

def plotData(data, ymin, ymax, xlabel, ylabel, title):
        plt.plot(data, 'o-')
        _min = np.min(data)
        _max = np.max(data)
        _mean = np.mean(data)
        print("Mean sigma =", _mean)
        plt.title(title)
        plt.plot([0, len(data)], [_min, _min], 'r--')
        plt.plot([0, len(data)], [_max, _max], 'r--')
        plt.plot([0, len(data)], [_mean, _mean], 'b-')
        ax = plt.gca()
        ax.set_xlim([0, len(data)])
        ax.set_ylim([ymin, ymax])
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.show()

def subAreas(image, hor, ver):
    """ Visualize sub areas in an image
        with hor "horizontal" sub image and
        ver "vertical" sub images"""

    x, y = image.shape
    print(x, y)
    step_x = int(x/hor)
    step_y = int(y/ver)
    # Draw vertical lines
    for i in range(ver):
        image[i * step_x, :] = 255
    # Draw horizontal lines
    for j in range(hor):
        image[:, j * step_y] = 255
    plt.imshow(image, cmap='gray')
    si.io.imsave("subareas.png", image)

# Most simple version, only one image, 4 regions
# Normal image
test_image = r'\images\man\FPC1321-MKN4NBW-2018-11-20_141857735.png'
# Defect bottom left
test_image_ll = r'\images\man\FPC1321-MKN4NBW-2018-11-20_144640458.png'
curr_dir = os.getcwd()

im_in = si.io.imread(curr_dir+test_image)


rms_g = calcRMS(im_in)
p2p_g = calcP2P(im_in)
print("RMS global = ", rms_g)
print("P2P global = ", p2p_g)

# n x n areas, FPC1321, 160x160 => s = 160/n
s = 20
n = 8
rms = []
p2p = []
for i in range(n):
    for j in range(n):
        rms.append(calcRMS(im_in[i*s:(i+1)*s, j*s:(j+1)*s]))
        p2p.append(calcP2P(im_in[i*s:(i+1)*s, j*s:(j+1)*s]))

print("\nResults")
print("Mean value = ", np.mean(rms))
print("Min value = ", np.min(rms))
print("Max value = ", np.max(rms))


plt.plot(rms, p2p, 'o')
plt.xlabel("RMS")
plt.ylabel("p2p")
plt.title("Correlation between p2p and RMS")
plt.show()

title = "RMS values, " + str(n) + "x" + str(n) + " sub areas"
plotData(rms, 0, 50, "Sub area", "RMS", title)
subAreas(im_in, 8, 8)
