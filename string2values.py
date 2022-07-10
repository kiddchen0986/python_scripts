# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 10:09:27 2018

@author: petter.ostlund
"""

# Convert hexstring containing uniformity, signal strength and RMS

import struct



def hexstring2values(x):
    print("Uniformity = ", struct.unpack('>f',struct.pack('I',int(x[0:8],16)))[0])
    print("Signal strength = ", struct.unpack('>f',struct.pack('I',int(x[8:16],16)))[0])
    print("RMS = ", struct.unpack('>f',struct.pack('I',int(x[16:24],16)))[0])


string =  'D7D5E63D0000BD3E4496E240' 
# uniformity: 0.112712555, ss: 0.369140625, rms: 7.08084297

hexstring2values(string)