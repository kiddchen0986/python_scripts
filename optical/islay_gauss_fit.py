# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 09:37:09 2018

@author: petter.ostlund
"""

import numpy as np
import scipy as sp


# From scipy cookbook
def gaussian(A, x0, y0, xw, yw):
    """Returns a gaussian function with the given parameters"""
    xw = float(xw)
    yw = float(yw)
    return lambda x,y: A*np.exp(-(((x0-x)/xw)**2+((y0-y)/yw)**2)/2)


# From scipy cookbook
def moments(data):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution by calculating its
    moments """
    total = data.sum()
    X, Y = np.indices(data.shape)
    x = (X*data).sum()/total
    y = (Y*data).sum()/total
    col = data[:, int(y)]
    width_x = np.sqrt(np.abs((np.arange(col.size)-y)**2*col).sum()/col.sum())
    row = data[int(x), :]
    width_y = np.sqrt(np.abs((np.arange(row.size)-x)**2*row).sum()/row.sum())
    height = data.max()
    return height, x, y, width_x, width_y


# From scipy cookbook
def fitgaussian(data):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution found by a fit"""
    params = moments(data)
    errorfunction = lambda p: np.ravel(gaussian(*p)(*np.indices(data.shape)) -
                                 data)
    p, success = sp.optimize.leastsq(errorfunction, params)
    return p


# Draw white rectangles around sub areas
def drawRectangle(image, y, x, d):
    """ Draws a square around y, x with distance d pixels to sides
     No check that edges of square are inside image boundaries
     Assuming a 2D array"""
    image[y-d-1, x-d:x+d+1] = 255
    image[y+d-1, x-d:x+d+1] = 255
    image[y-d-1:y+d, x-d+1] = 255
    image[y-d-1:y+d, x+d+1] = 255
    return image


# Extract sub images from cropped HD OVT image
def extractSubImagesCropped(im, xs=297, ys=229, xs2=245, ys2=318, xp=102.8, yp=89, s=25,
                 rows=8, cols=14, no_sub=116):

    sub_images = np.zeros((2*s+1,2*s+1, no_sub), np.dtype(np.uint8))
    sub_in_block = 37  # with two rows
    im_vis = np.copy(im) # Image for visualization

    for nn in range(no_sub):
        block_no = nn // sub_in_block
        block_pos = nn % sub_in_block
        if block_pos < 18:  #First row in block
            x = int(xs + xp * block_pos)
            y = int(ys + block_no * 2 * yp)
        else:  # Second row in block
            x = int(xs2 + xp * (block_pos - 18))
            y = int(ys2 + block_no * 2 * yp)
        #print(x,y)
        sub_images[:,:,nn] = im[y-s:y+s+1, x-s:x+s+1]
        im_vis = drawRectangle(im_vis, y, x, s)

    return sub_images, im_vis

# Extract sub images from full HD OVT image
def extractSubImages(im, xs=89, ys=50, xs2=40, ys2=140, xp=102.8, yp=89, s=25,
                 rows=12, cols=18, no_sub=222):

    sub_images = np.zeros((2*s+1,2*s+1, no_sub), np.dtype(np.uint8))
    sub_in_block = 37  # with two rows
    im_vis = np.copy(im) # Image for visualization

    for nn in range(no_sub):
        block_no = nn // sub_in_block
        block_pos = nn % sub_in_block
        if block_pos < 18:  #First row in block
            x = int(xs + xp * block_pos)
            y = int(ys + block_no * 2 * yp)
        else:  # Second row in block
            x = int(xs2 + xp * (block_pos - 18))
            y = int(ys2 + block_no * 2 * yp)
        #print(x,y)
        sub_images[:,:,nn] = im[y-s:y+s+1, x-s:x+s+1]
        im_vis = drawRectangle(im_vis, y, x, s)

    return sub_images, im_vis
