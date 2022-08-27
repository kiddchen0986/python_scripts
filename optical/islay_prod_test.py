#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 13:09:27 2018

@author: petter.ostlund@fingerprints.com
"""

import os
from fnmatch import fnmatch
import numpy as np
import skimage as si
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import scipy.ndimage.filters as filters


def plot_data(data, ymin, ymax, xlabel, ylabel, title):
        plt.plot(data)
        _min = np.min(data)
        _max = np.max(data)
        _mean = np.mean(data)
        print("Mean sigma =", _mean)
        print("Min = ", _min)
        print("Max = ", _max)
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


class TestImage():
    """Collects all sub images from an input image and places
    them in an array and. All tests included"""

    def draw_rectangle(self, image, y, x, d):
        """ Draws a square around y, x with distance d pixels to sides
         No check that edges of square are inside image boundaries
         Assuming a 2D array"""
        image[y-d, x-d:x+d] = 180
        image[y+d, x-d:x+d] = 180
        image[y-d:y+d, x-d] = 180
        image[y-d:y+d, x+d] = 180
        return image

    def draw_rectangle2(self, image, no, d):
        """ Draws a square around sub image number "no" with size 2d x 2d.
         Purpose is to be able to visualize failing area/sub image
         for different tests. Assuming a "diamond" shape."""

        block = self.cols*2 + 1
        x_pos = no % block
        y_pos = no // block

        if x_pos < self.cols: # Even row?
            x = self.xs1 + int(x_pos * self.xp)
            y = self.ys1 + int(y_pos * 2 * self.yp)
        else:
            x = self.xs2 + int((x_pos - self.cols) * self.xp)
            y = self.ys2 + int(y_pos * 2 * self.yp)

        image[y-d, x-d:x+d] = 255
        image[y+d, x-d:x+d] = 255
        image[y-d:y+d, x-d] = 255
        image[y-d:y+d, x+d] = 255

        return image

# SOI values
#    def __init__(self, im, name, xs=40, ys=35, xs2=94, ys2=130, xp=109.1, yp=94.5, s=22,
#                 rows=8, cols=12, no_sub=92):
    # OVT2710
    def __init__(self, im, name, xs1=89, ys1=50, xs2=40, ys2=140, xp=102.8, yp=89, s=17,
                 rows=12, cols=18, no_sub=222):
        """ Positions and size of the sub images. Add them if there is need
        to adjust them. """
        self.name = name      # Filename for example
        self.im_in = im       # Input image
        self.xs1 = xs1         # x start even row
        self.ys1 = ys1         # y start even row
        self.xs2 = xs2        # x start odd row
        self.ys2 = ys2        # y start odd row
        self.xp = xp          # x period
        self.yp = yp          # y period
        self.s = s            # Rectangles, 2s x 2s, collected as sub images
        self.rows = rows      # Rows of sub images
        self.cols = cols      # Cols of sub images
        self.no_sub = no_sub  # No of sub images

        print(np.max(im.flatten()))
        print(np.min(im.flatten()))

        print("Side (pixels) = ", 2*self.s+1)

        # OV2710 + Visera
        # Collect sub images
        self.sub_images = np.zeros((2*s+1,2*s+1, no_sub), np.dtype(np.uint8))
        sub_in_block = 37  # with two rows
        im_vis = np.copy(self.im_in) # Image for visualization

        for nn in range(no_sub):
            block_no = nn // sub_in_block
            block_pos = nn % sub_in_block
            #print(block_no, block_pos)
            if block_pos < 18:  #First row in block
                x = int(xs1 + xp * block_pos)
                y = int(ys1 + block_no * 2 * yp)
            else:  # Second row in block
                x = int(xs2 + xp * (block_pos - 18))
                y = int(ys2 + block_no * 2 * yp)
            #print(x,y)#,"\n")
            self.sub_images[:,:,nn] = self.im_in[y-s:y+s+1, x-s:x+s+1]
            im_vis = self.draw_rectangle(im_vis, y, x, s)

        #plt.imshow(im_vis, cmap='gray', vmin=0, vmax=255)
        #plt.show()
        si.io.imsave("sub_areas_test.png", im_vis) #, cmap='gray') #, vmin=0, vmax=255)

    def test_uf_max(self, threshold):
        """ Counts the number of sub images with a max value below
        a threshold of the max value for all sub images. This tests
        the uniformity of the max values in the sub images"""
        n = 8  # Check median of 8 highest pixels to remove outliers 
        im_test_uf_max = np.copy(self.im_in)  # Image for visualization
        res = np.zeros((self.no_sub))
        for i in range(self.no_sub):
            res[i] = np.median(np.sort(self.sub_images[:,:,i].flatten())[-n:])
        glob_max = np.max(res)
        #print(res, glob_max)
        number_failed = 0
        for i in range(self.no_sub):
            if (res[i] / glob_max) < threshold:
                number_failed += 1
                im_test_uf_max = self.draw_rectangle2(im_test_uf_max,
                                                      i,
                                                      self.s)
        plt.imshow(im_test_uf_max, cmap='gray')
        title = "Test UF max, threshold = " + str(threshold)
        plt.title(title)
        plt.show()
        plt.imsave("_" + self.name + "_test_uf_max_th_" + str(threshold)+".png",
                   im_test_uf_max, cmap='gray')
        return number_failed

    def test_uf_mean(self, threshold):
        """ Counts the number of sub images with average value below
        a threshold of the maximum average value"""
        im_test_uf_mean = np.copy(self.im_in)  # Image for visualization
        res = np.zeros((self.no_sub))
        for i in range(self.no_sub):
            res[i] = np.mean(self.sub_images[:,:,i].flatten())
        glob_mean = np.mean(res)
        #print(res, glob_max)
        number_failed = 0
        for i in range(self.no_sub):
            if (np.abs(res[i] - glob_mean)) > threshold:
                number_failed += 1
                im_test_uf_mean = self.draw_rectangle2(im_test_uf_mean,
                                                      i,
                                                      self.s)
        #plt.imshow(im_test_uf_mean, cmap='gray')
        #title = "Test UF mean, threshold = " + str(threshold)
        #plt.title(title)
        #plt.show()
        #plt.imsave(self.name+"_test_uf_mean_th_" + str(threshold)+".png",
        #           im_test_uf_mean, cmap='gray')
        return number_failed

    def test_offset(self, k, max_offset):
        """ Calculate the average position for pixels values higher 
        than the k:th highest pixels, to indicate if lens is positioned 
        incorrect compared to where it is suppossed to be"""
        im_test_offset = np.copy(self.im_in)
        x_off = np.zeros((self.no_sub))
        y_off = np.zeros((self.no_sub))

        x0 = int(self.s) # Local center of sub image
        y0 = int(self.s)
        number_failed = 0
        # Find the k highest pixel value for each sub and their positions
        for i in range(self.no_sub):
            th = int(np.sort(self.sub_images[:,:,i].flatten())[-k])  # Threshold
            #print(np.sort(self.sub_images[:,:,i].flatten())[-k:-1])
            x, y = np.where(self.sub_images[:,:,i] >= th)
            x_off[i] = np.mean(np.subtract(x, x0))
            y_off[i] = np.mean(np.subtract(y, y0))
            if x_off[i] > max_offset or y_off[i] > max_offset:
                number_failed += 1
                im_test_offset = self.draw_rectangle2(im_test_offset,
                                                      i,
                                                      self.s)
        plt.imshow(im_test_offset, cmap='gray')
        title = "Test offset, max_offset = " + str(max_offset)
        plt.title(title)
        plt.show()
        plt.imsave(self.name+"_test_offset_maxo_ffset_" + str(max_offset)+".png",
                   im_test_offset, cmap='gray')
        return number_failed

    def test_edge(self, th):
        """Check for edges where the pixel to pixel difference is 
        larger than th, in x or y direction"""
        im_test_edge = np.copy(self.im_in)
        number_failed = 0
        for i in range(self.no_sub):
            y_diff = np.max(np.abs(np.diff(self.sub_images[:,:,i])))
            x_diff = np.max(np.abs(np.diff(np.transpose(self.sub_images[:,:,i]))))
            #print(y_diff, x_diff)
            if x_diff > th or y_diff > th:
                number_failed += 1
                im_test_edge = self.draw_rectangle2(im_test_edge,
                                                        i,
                                                        self.s)
        plt.imshow(im_test_edge, cmap='gray')
        title = "Test edge, threshold = " + str(th) + " adc values"
        plt.title(title)
        plt.show()
        plt.imsave(self.name+"_test_edge_th_" + str(th)+".png",
                   im_test_edge, cmap='gray')
        return number_failed

    def test_contrast(self, th_rms, th_p2p):
        """Calculate the contrast as RMS (Root Mean Square) for
        each sub image. Mark the ones with contrast lower than
        'threshold' of max contrast as failing"""
        im_test_contrast = np.copy(self.im_in)
        rms = np.zeros((self.no_sub))
        p2p = np.zeros((self.no_sub))
        for i in range(self.no_sub):
            rms[i] = np.std(self.sub_images[:,:,i].flatten())
            p2p[i] = np.max(self.sub_images[:,:,i].flatten())\
                    -np.min(self.sub_images[:,:,i].flatten())
        number_failed = 0
        for i in range(self.no_sub):
            #print(rms[i], p2p[i])
            if rms[i] < th_rms or p2p[i] < th_p2p:
                number_failed += 1
                print("position = ", i)
                im_test_contrast = self.draw_rectangle2(im_test_contrast,
                                                        i,
                                                        self.s)
        plt.imshow(im_test_contrast, cmap='gray')
        title = "Test contrast, threshold_rms = " + str(th_rms)
        plt.title(title)
        plt.show()
        plt.imsave(self.name.rstrip(".png")+"_test_contrast_th_rms_" + str(th_rms)+".png",
                   im_test_contrast, cmap='gray')

        plot_data(rms, 20, 50, "Sub image", "RMS",\
                  "RMS, 35x35 pixels sub images")
        plot_data(p2p, 80, 200, "Sub image", "P2P",\
                  "Peak to Peak, 35x35 pixels sub images")

        plt.plot(rms, p2p, 'o', )
        plt.xlabel("RMS")
        plt.ylabel("p2p")
        plt.title("Correlation between p2p and RMS")
        ax = plt.gca()
        ax.set_xlim([25, 45])
        ax.set_ylim([90, 180])

        return number_failed

    def fft2(self, sub_im):
        freq_im = np.fft.fft2(sub_im, norm='ortho')
        print(freq_im)
        fig, ax = plt.subplots()
        ax.scatter(freq_im.real, freq_im.imag)
        plt.show()

    def plot_line(self, sub_im, line):
        #print(sub_im.shape)
        xpoints = len(sub_im[line,:])
        y_gauss = filters.gaussian_filter(sub_im[line,:], 5)
        x = np.linspace(0, xpoints-1, xpoints, endpoint=True)
        f = interp1d(x, sub_im[line,:])
        xnew = np.linspace(0, xpoints-1, xpoints*4, endpoint=True)
        ynew = f(xnew)
#        sub_im_interp = np.interp(range(len(sub_im[line,:])), sub_im[line,:])
        plt.plot(x, sub_im[line,:], 'o', xnew, ynew, '-', y_gauss, '-')
        plt.xlabel("pixels")
        plt.ylabel("intensity")
        title = "Diffraction pattern (Intensity) at center along x-axis"
        plt.title(title)
        plt.show()
        y_no_svea = sub_im[line,:] - y_gauss
        plt.plot(filters.gaussian_filter(y_no_svea, 3), '-')
        plt.xlabel("pixels")
        plt.ylabel("intensity variation")
        plt.ylim([-10, 10])
        title = "Center diffraction pattern along x-axis"
        plt.title(title)
        plt.show()

#### Tests with diffuse light source #########################################

#root_dir = r"C:\python_scripts2\python_scripts\optical\p1_images\test"
#root_dir = r'C:\Logs\FPC1610_hana_micron_stage1_malmo_20181004\from_shanghai\images_shanghai_20181010'
#root_dir = r'C:\Logs\FPC1610_hana_micron_stage1_malmo_20181004\from_shanghai\50pcs_shanghai_drop2_20181012'
#
#filelist = []
#for path, subdirs, files in os.walk(root_dir):
#    for name in files:
#        if fnmatch(name, '*Image.png'):
#            filelist.append(os.path.join(path, name))
#filelist.sort()
#
#uf_ranking = []
#
#count = 1
#for file in filelist:
#
#    im_in = si.io.imread(file)
#    #print("Input file size= ", im_in.shape)
#    test_object = TestImage(im_in, file)
#    #test_object.lens_shape()
#    uf_mean_failed = test_object.test_uf_mean(20)
#    print("Image number = ", count)
#    print("Image uf failed = ", uf_mean_failed)
#    uf_ranking.append((count, uf_mean_failed))
#    #print("UF mean failed = ", uf_mean_failed)
##    offset_failed = test_object.test_offset(8, 2)
##    print("Offset failed = ", offset_failed)
##    edge_failed = test_object.test_edge(20)
##    print("Edge failed = ", edge_failed)
#    count += 1
#
#
#uf_ranking.sort(key=lambda tup: tup[1])
#for m,u in uf_ranking:
#    print("Module number = ", m, u)

##############################################################################

#### Contrast test

root_dir = r'C:\python_scripts2\python_scripts\optical\contrast_images\#3'

filelist = []
for path, subdirs, files in os.walk(root_dir):
    for name in files:
        if fnmatch(name, '*CapturedImage.png'):
            filelist.append(os.path.join(path, name))
filelist.sort()

for file in filelist:

    im_in = si.io.imread(file)
    #print("Input file size= ", im_in.shape)
    test_object = TestImage(im_in, file)
    test_object.test_contrast(31, 0)

##############################################################################

#test_object = TestImage(im_in, "Number2")
##uf_max_failed = test_object.test_uf_max(0.9)
##print("UF max failed = ", uf_max_failed)
#
#uf_mean_failed = test_object.test_uf_mean(0.9)
#print("UF mean failed = ", uf_mean_failed)
#
##contrast_failed = test_object.test_contrast(0.7)
##print("Contrast failed = ", contrast_failed)
#
#offset_failed = test_object.test_offset(8, 2)
#print("Offset failed = ", offset_failed)
#
#edge_failed = test_object.test_edge(20)
#print("Edge failed = ", edge_failed)

#### Testing diffraction based magnification calculation
#im_in = si.io.imread('C:\optical\Cal_new_2\Ceramic.png')
#test_object = TestImage(im_in, "oled_and_ceramic")
##for i in range(10):
##    test_object.fft2(test_object.sub_images[i])
#
#for i in range(10):
#    print(test_object.sub_images[:,:,0].shape)
#    test_object.plot_line(test_object.sub_images[:,:,0+i], 34)
#
##print(test_object.sub_images[0].shape)
#
#uf_mean_failed = test_object.test_uf_mean(0.9)
#print("UF mean failed = ", uf_mean_failed)