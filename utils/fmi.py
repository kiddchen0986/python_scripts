"""Tool to extract data from .fmi files.
https://fpc-confluence.fingerprint.local/confluence/display/FSD/The+FMI+file+format
Creator: Petter Ostlund
"""
#! /usr/bin/env python3
# File: fmi.py
# Description: Internal tool to extract fmi data 
# https://fpc-confluence.fingerprint.local/confluence/display/FSD/The+FMI+file+format
# Creator: Petter Ostlund, Fingerprint Cards
# Updated: 2016-10-30

# Modules needed: scipy and numpy

import os
import sys
from fnmatch import fnmatch
import numpy as np
import scipy.misc as misc


def save_meta(filename, meta, metatype, size):
    """Method to save meta"""
    print('save_meta')
    values = np.frombuffer(meta, dtype='u4',count=int(size/4), offset=0)
    with open(filename, 'a') as f:
        f.write('\n'+metatype+'\n')
        for index,value in enumerate(values):
            f.write('meta'+str(index)+' = '+str(value)+'\n')


def save_image(filename, im):
    """Method to save image"""
    print('save_image')
    w = np.frombuffer(im, dtype='u4', count=1, offset=0)[0]
    h = np.frombuffer(im, dtype='u4', count=1, offset=4)[0]
    bits = np.frombuffer(im, dtype='u4', count=1, offset=8)[0]
    rot = np.frombuffer(im, dtype='u4', count=1, offset=12)[0]
    channel = np.frombuffer(im, dtype='u4', count=1, offset=16)[0]
    stride = np.frombuffer(im, dtype='u4', count=1, offset=20)[0]
    if bits == 8:
      pixels = np.frombuffer(im, dtype='u1', count=w*h, offset=24)
    elif bits == 16:
      pixels = np.frombuffer(im, dtype='u2', count=w*h, offset=24)
    print(w,h,bits,rot,channel,stride,len(pixels))
    misc.imsave(filename, pixels.reshape(h,w))


def extract_fpcimagedata(data, filename):
    """Method to extract data from FpcImageData"""
    datasize = len(data)
    print('Size of FpcImageData = ' + str(datasize))
    count = 0

    version = np.frombuffer(data, dtype='u4', count=1, offset=count)[0]
    flags = np.frombuffer(data, dtype='u4', count=1, offset=count+4)[0]
    print('Version = '+str(version))
    print('Flags = '+str(flags))
    print('\n')

    magic_offset = 8 # Unknown header!
    count = count + magic_offset

    while count < datasize:  # Check end of FpcImageData
        type_ = np.frombuffer(data, dtype='u4', count=1, offset=count)[0]
        capacity = np.frombuffer(data, dtype='u4', count=1, offset=count+4)[0]
        size = np.frombuffer(data, dtype='u4', count=1, offset=count+8)[0]
        # print(type_)
        if type_ == 0:                     # Meta common
            print('Type = '+str(type_)+' = Meta Common')
            meta = np.frombuffer(data, dtype='u1', count = size,\
                                 offset = count + 12)
            save_meta(filename.rstrip('.fmi')+'_meta.txt',\
                      meta, 'Meta common', size)
            count = count + 3*4 + capacity
        elif type_ == 1:                   # Dead pixels
            print('Type = '+str(type_)+' = Dead pixels')
            count = count + 3*4 + capacity

        elif type_ == 14:                   # Pixels_CAC or pixels_0
            print('Type = '+str(type_)+' = Pixels_CAC or pixels_0')
            im = np.frombuffer(data, dtype='u1', count=capacity, offset=count+12)
            save_image(filename.rstrip('.fmi')+'_cac_0.png', im)
            count = count + 3*4 + capacity

        elif type_ == 15:                   # Meta CAC or 0
            print('Type = '+str(type_)+' = Meta CAC or 0')
            meta = np.frombuffer(data, dtype='u1', count = size,\
                                 offset = count + 12)
            save_meta(filename.rstrip('.fmi')+'_meta.txt',\
                      meta, 'Meta CAC or 0', size)
            count = count + 3*4 + capacity

        elif type_ == 12:                  # Pixels fallback
            print('Type = '+str(type_)+' = Pixels fallback')
            im = np.frombuffer(data, dtype='u1', count=capacity, offset=count+12)
            save_image(filename.rstrip('.fmi')+'_fallback.png', im)

            count = count + 3*4 + capacity

        elif type_ == 13:                  # Meta fallback
            print('Type = '+str(type_)+' = Meta fallback')
            meta = np.frombuffer(data, dtype='u1', count = size,\
                                 offset = count + 12)
            save_meta(filename.rstrip('.fmi')+'_meta.txt',\
                      meta, 'Meta fallback', size)
            count = count + 3*4 + capacity

        elif type_ == 8:                  # Pixels APNS
            print('Type = '+str(type_)+' = Pixels APNS')
            im = np.frombuffer(data, dtype='u1', count=capacity, offset=count+12)
            save_image(filename.rstrip('.fmi')+'_apns.png', im)
            count = count + 3*4 + capacity

        elif type_ == 9:                  # Meta APNS
            print('Type = '+str(type_)+' = Meta APNS')
            meta = np.frombuffer(data, dtype='u1', count = size,\
                                 offset = count + 12)
            save_meta(filename.rstrip('.fmi')+'_meta.txt',\
                      meta, 'Meta APNS', size)
            count = count + 3*4 + capacity


        elif type_ == 10:                  # Pixels APNS weight
            print('Type = '+str(type_)+' = Pixels APNS weight')
            im = np.frombuffer(data, dtype='u1', count=capacity, offset=count+12)
            save_image(filename.rstrip('.fmi')+'_apns_weight.png', im)
            count = count + 3*4 + capacity

        elif type_ == 11:                  # Meta APNS weight
            print('Type = '+str(type_)+' = Meta APNS weight')
            meta = np.frombuffer(data, dtype='u1', count = size,\
                                 offset = count + 12)
            save_meta(filename.rstrip('.fmi')+'_meta.txt',\
                      meta, 'Meta APNS weight', size)
            count = count + 3*4 + capacity

        else:
            break

        print('Capacity = '+str(capacity))
        print('size = '+str(size))
        print('\n')


def extract_from_blocks(block_list, filename):
    """Method to extract data from blocks"""
    for block in block_list:
        type_format = np.frombuffer(block, dtype='u2', count=1, offset=0)[0]
        type_id = np.frombuffer(block, dtype='u2', count=1, offset=2)[0]
        payloadsize = np.frombuffer(block, dtype='u4', count=1, offset=4)[0]
        data = np.frombuffer(block, dtype='u1', count=payloadsize, offset=8)
        # print(type_format)
        # print(type_id)
        # print(payloadsize)
        # print(data)

        if type_format == 1:  # FpcImageData
            print('Type Format = FpcImageData')
            extract_fpcimagedata(data, filename)
        elif type_format == 2:  # ASCII
            with open(filename.rstrip('.fmi')+'.txt', 'w') as f:
                data.tofile(f, sep=" ", format="%s")
            print('Type Format = ASCII')
        elif type_format == 3:  # PNG file
            print('Type Format = PNG')
            with open(filename.rstrip('.fmi')+'.png', 'w') as f:
                data.tofile(f)
        elif type_format == 4:  # Binary
            print('Type Format = Binary')
            misc.imsave(filename.rstrip('.fmi')+'_bin.png',data.reshape(176,64))
        elif type_format == 5:  # Proprietary
            print('Type Format = Proprietary')
            misc.imsave(filename.rstrip('.fmi')+'_prop.png',data.reshape(176,64))


def read_fmi(filename):
    """Open and read file, and extract data blocks"""
    with open(filename, 'rb') as f:
        buffer = f.read()
    file_size = len(buffer)  # Total size of the fmi-file
    print('\n' + 'Extracting ' + filename + ', filesize = ' + str(file_size) + ' bytes')
    header_signature = np.frombuffer(buffer, dtype='u1', count=4)
    print('Header signature = ' + "".join(map(chr, header_signature)))
    header_size = np.frombuffer(buffer, dtype='u4', count=1, offset=4)[0]
    print('Header size = ' + str(header_size))
    version_major = np.frombuffer(buffer, dtype='u2', count=1, offset=8)[0]
    version_minor = np.frombuffer(buffer, dtype='u2', count=1, offset=10)[0]
    print('Version = ' + str(version_major) + '.' + str(version_minor))

    # Loop through all data blocks and put them in a list
    byte_counter = 8 + header_size
    data_blocks = []
    byte_list = []
    while byte_counter < file_size:  # Check if
        block_size = 8 + np.frombuffer(buffer, dtype='u4', count=1, offset=byte_counter + 4)[0]
        # print('Block size = ' + str(block_size))
        data_blocks.append(np.frombuffer(buffer, dtype='u1', count=block_size, offset=byte_counter))

        byte_list.append(block_size)

        byte_counter = byte_counter + block_size

    print('Header = 12 bytes, Block sizes = ' + str(byte_list))

    return extract_from_blocks(data_blocks, filename)


def block_print():
    """Disables print output"""
    sys.stdout = open(os.devnull, 'w')


def enable_print():
    """Enables print output"""
    sys.stdout = sys.__stdout__

if __name__ == "__main__":
    rootdir = os.path.dirname(os.path.realpath(__file__))

    fmi_raw_filelist = []
    for path, subdirs, files in os.walk(rootdir):
        for name in files:
            if fnmatch(name, '*.fmi.raw'):
                fmi_raw_filelist.append(os.path.join(path, name))

    for filename in fmi_raw_filelist:
        with open(filename, 'rb') as f:
            buffer = f.read()
        im = np.frombuffer(buffer, dtype='u1', count=176 * 64)
        misc.imsave(filename.rstrip('.fmi.raw') + '_fmi_raw.png', im.reshape(176, 64))

    # List all files in rootdir
    fmi_filelist = []
    for path, subdirs, files in os.walk(rootdir):
        for name in files:
            if fnmatch(name, '*.fmi'):
                fmi_filelist.append(os.path.join(path, name))

    if len(fmi_filelist) == 0:
        print('File list is empty')

    # Loop through the filelist and extract data blocks
    for filename in fmi_filelist:
        read_fmi(filename)



