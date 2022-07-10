#
# Copyright (c) 2018 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#

from ctl import mqt2
from fnmatch import fnmatch
import os

# FPC Product type information
"""
FPC_PRODUCT_TYPE1080         0
FPC_PRODUCT_TYPE1020         1
FPC_PRODUCT_TYPE1021         2
FPC_PRODUCT_TYPE1025         3
FPC_PRODUCT_TYPE1225         4
FPC_PRODUCT_TYPE1022         5
FPC_PRODUCT_TYPE1035         6
FPC_PRODUCT_TYPE1235         7
FPC_PRODUCT_TYPE1140         8
FPC_PRODUCT_TYPE1145         9
FPC_PRODUCT_TYPE1245        10
FPC_PRODUCT_TYPE1260        13
FPC_PRODUCT_TYPE1265        14
FPC_PRODUCT_TYPE1268        15
FPC_PRODUCT_TYPE1028        16
FPC_PRODUCT_TYPE1075        17
FPC_PRODUCT_TYPE1320        18
FPC_PRODUCT_TYPE1321        19
FPC_PRODUCT_TYPE1263        20
FPC_PRODUCT_TYPE1262        21
FPC_PRODUCT_TYPE1266        22
FPC_PRODUCT_TYPE1264        23
FPC_PRODUCT_TYPE1272        24
FPC_PRODUCT_TYPE1228        25
FPC_PRODUCT_TYPE1267        26
FPC_PRODUCT_TYPE1291_S      30
FPC_PRODUCT_TYPE1291_G175   31
FPC_PRODUCT_TYPE1291_G250   33
FPC_PRODUCT_TYPE1291_Z120   34
FPC_PRODUCT_TYPE1228_G175   36
FPC_PRODUCT_TYPE1228_Z      37
FPC_PRODUCT_TYPE1272_G175   38
FPC_PRODUCT_TYPE1272_Z      39
FPC_PRODUCT_TYPE1261_S      40
FPC_PRODUCT_TYPE1229_G175   41
FPC_PRODUCT_TYPE1511_S      42
FPC_PRODUCT_TYPE1024        43
"""

# Settings parameters to be included in settings_list
"""
crop_left,
crop_top,
crop_right,
crop_bottom,
bl_thresh,
bl_limit,
snr_pre,
snr_limit,
udr_limit,
fixed_p_enabled, (Boolean)
fixed_p_threshold,
fixed_p_limit,
is_static (Boolean)
"""

# Example of how to use the mqt2 wrapper #####################################

# Path to DLL. Example below
dll_path = 'C:\\python_scripts2\\python_scripts\\wrapper\\binaries\\MTT_16.0\\ctl_rerun_test_analysis.dll'

# Function parameters
hw_id = 0x0E11
product_type = 31

# Test settings
settings_list = [4, 4, 4, 4, 1.1e-6, 8, 5, 8.0, 0.25, True, 0.8, 40, False]

#output_dir = b'name_or_path_to_otuput_dir', exmaple below
output_dir = b'C:\jira\cet-97\out_algo_visual'

# root_dir = r'fmi input dir', example below
root_dir = r'C:\jira\cet-97\logs_20180504_algo_visual'

filelist = []
for path, subdirs, files in os.walk(root_dir):
    for name in files:
           if fnmatch(name, '*.fmi'):
               filelist.append(os.path.join(path, name))
filelist.sort()

# To correlate results with fmi file
with open("filelist.csv", "w") as f:
    for file in filelist:
        f.write(file)
        f.write("\n")

# Create test object
test_mqt2 = mqt2.ReRunMqt2(dll_path)

# Run tests
for file in filelist:
    byte_string = file.encode()
    print("tools status: ",
          test_mqt2(product_type, hw_id, settings_list, byte_string, output_dir, True))