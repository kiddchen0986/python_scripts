# -*- coding: utf-8 -*-
"""
Created on Mon May 14 12:06:22 2018

@author: petter.ostlund@fingerprints.com
"""

import os
from fnmatch import fnmatch
import re

# Conversion tool from ASIC simulation log-files, TestLog.txt, to MTT
# recommended settings format in 'test_vectors.c'
# The script collects all TestLog.txt file under this folder
#root_dir = r'C:\python_scripts\asic_rec_settings\testfiles'
root_dir = r'C:\python_scripts2\python_scripts\asic_rec_settings\testfiles_shanghai_1_1_0'


filelist = []
for path, subdirs, files in os.walk(root_dir):
    for name in files:
           if fnmatch(name, '*Log.txt'):
               filelist.append(os.path.join(path, name))

# Dictionary with all the tests (TestLog.txt) and its SPI writes
test_vectors = {}

for file in filelist:
    with open(file, 'r') as f:
        buffer = f.read()

    try:
        # Check for test name in top of file
        test_name = re.search('(\*\*\* )([a-z_]+)', buffer).group(2)
        print("\nTest name: ", test_name)
        test_vectors[test_name] = []

        # Find all 'spi.send' in file
        spi_writes = re.findall('(wdata =)([ 0x\S\S]+)', buffer)

        # Loop through and skip unwanted writes
        for _, values in spi_writes:
            # Remove image write, ends with 'ff'
            if values[-2:] == 'ff':
                print("    Skip Image write")
            # Remove InterruptsWithClear write
            elif values == ' 0x1c 0x00':
                print("    Skip InterruptsWithClear write")
            else:
                val = " " + values.upper().replace("X", "x").strip().replace(" ", ", ")
                print("   " + val)
                test_vectors[test_name].append(val)

    except:
        print("Error reading values from: ", file)


# Test look up dictionary, add more tests below
test_name = {'test_image_swing_cb': 'SWINGING_CHECKERBOARD',
             'test_image_swing_icb': 'SWINGING_INVERTED_CHECKERBOARD',
             'adc_comparator_input_cm': 'ADC_COMPARATOR_INPUT_CM',
             'adc_comparator_noise_and_offset': 'ADC_COMPARATOR_NOISE_AND_OFFSET',
             'adc_range_and_gain': 'ADC_RANGE_AND_GAIN',
             'clkbist': 'CLKBIST',
             'clkbist_check': 'CLKBIST_CHECK',
             'comparator_bandwidth_setting': 'COMPARATOR_BANDWIDTH_SETTING',
             'otp_read': 'OTP_READ',
             'otp_write': 'OTP_WRITE',
             'ramp_up_time_short_diff': 'RAMP_UP_TIME_SHORT_DIFF',
             'ramp_up_time_trim': 'RAMP_UP_TIME_TRIM',
             'test_image_constant': 'TEST_IMAGE_CONSTANT',
             'test_image_drive': 'TEST_IMAGE_DRIVE'}

# Shanghai=0x1011, Shanghai 2nd=0x1012, Shenzhen=0x1021
line_out = "static uint8_t PRODUCT_TYPE1511_S_0X1012_{0}_{1}[] = {{{2} }};\n"

# Save vectors to a text_file
with open("test_vectors.txt", 'w') as f:
    location = "Recommended settings from: " + root_dir + "\n"
    f.write(location)
    for test, values in test_vectors.items():
        f.write("\n")
        f.write(test)
        f.write("\n")
        i = 1
        for writes in values:
            line = line_out.format(test_name[test], i, writes)
            f.write(line)
            i += 1