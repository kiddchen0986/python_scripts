#!/usr/bin/env/python3
"""
Created on Wed Apr 25 17:36:07 2018

@author: petter.ostlund@fingerprints.com
"""

import sys
import numpy as np
import imageio
import matplotlib.pyplot as plt

# White balance with 'gray-world' method
def wb_gray_world(image):
    ch1 = np.median(image[0::2,0::2].flatten())
    ch2 = np.median(image[1::2,0::2].flatten())
    ch3 = np.median(image[0::2,1::2].flatten())
    ch4 = np.median(image[1::2,1::2].flatten())
    ch = [ch1, ch2, ch3, ch4]
    m = np.max(ch)
    #print(m, ch1, ch2, ch3, ch4)
    #print(m, ch1/m, ch2/m, ch3/m, ch4/m)
    image[0::2,0::2] = np.multiply(image[0::2,0::2], ch1/m)
    image[0::2,0::2] = np.multiply(image[0::2,0::2], ch2/m)
    image[0::2,0::2] = np.multiply(image[0::2,0::2], ch3/m)
    image[0::2,0::2] = np.multiply(image[0::2,0::2], ch4/m)
    return image

def main(argv):
    try:
        file = sys.argv[1]
        width = int(sys.argv[2])
        height = int(sys.argv[3])
        stride = int(sys.argv[4])
        bits = int(sys.argv[5])
    except:
        print("Usage: readRawVideo.py <inputfile> <width> <height> <stride> <bitdepth>")
        sys.exit(2)
    print("File=",file, " width=", width, " height=", height, " stride=", stride, " bitdepth=", bits)

    # Calculate number of frames
    with open(file, 'rb') as f:
        buffer = f.read()
        frames = int(len(buffer)/(stride*height))
        print("Number of frames = ", frames)

    with open(file, 'rb') as f:

        # Read data for each frame
        for i in range(frames):
            data = np.memmap(f,
                             dtype='u1',
                             offset=i*stride*height,
                             mode='r',
                             shape=stride*height)

            if bits == 10:
                data = data.astype('u2')
                image = np.zeros((height, width), 'u2')
                for r in range(height):
                    start = r*stride
                    stop = int(start + width*5/4)
                    b = data[start+4:stop+4:5]
                    image[r, 0::4] = np.add(np.left_shift(data[start+0:stop+0:5], 8), np.left_shift(np.bitwise_and(b, 0b00000011), 6)) 
                    image[r, 1::4] = np.add(np.left_shift(data[start+1:stop+1:5], 8), np.left_shift(np.bitwise_and(b, 0b00001100), 4))
                    image[r, 2::4] = np.add(np.left_shift(data[start+2:stop+2:5], 8), np.left_shift(np.bitwise_and(b, 0b00110000), 2))
                    image[r, 3::4] = np.add(np.left_shift(data[start+3:stop+3:5], 8), np.left_shift(np.bitwise_and(b, 0b11000000), 0))
                image = wb_gray_world(image)

            elif bits == 8:
                image = np.zeros((height, width), 'u1')
                image = data.reshape(height, stride)
                image = image[:,0:width]

            #print(image.dtype)
            # Histogram plotting
#            y_max = 350000
#            n, bins, patches = plt.hist(image.flatten(), 100, range=(0,65535))
#            plt.title("One image")
#            axis = plt.gca()
#            axis.set_ylim([0, y_max])
#            plt.ylabel("Number of pixels")
#            plt.xlabel("Value")
#            plt.show()
            image = np.rot90(image)
            imageio.imwrite(file.rstrip(".raw")+"_"+str(i)+".png", image, compress_level=0)

if __name__ == "__main__":
   main(sys.argv[1:])