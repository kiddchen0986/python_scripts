# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#
import sys
import os

Getpath = input("Please enter log path:")
os.chdir(Getpath)
cwd = os.getcwd()
print("Changed current directory is: ", cwd)


def covert_raw_to_fmi(cwd):
    files = os.walk(cwd)
    n = 0
    for root, dir, files in files:
        for filename in files:
            portion = os.path.splitext(filename)
            if portion[1] == '.raw':
                rename = portion[0].split("_")
                for i in range(len(rename)):
                    if rename[i].startswith("2020"):
                        part1 = rename[i].split("-")[0] + rename[i].split("-")[1] + rename[i].split("-")[2]
                        part2 = rename[i+1].split("-")[0] + rename[i+1].split("-")[1] + rename[i+1].split("-")[2]

                newname = part1 + part2 + "_00_" + "{:0>3s}".format(str(n)) + ".fmi"
                os.rename(filename, newname)
                n = n + 1


if __name__ == "__main__":
    try:
        covert_raw_to_fmi(cwd)

    except Exception as e:
        print("Error {} caught in script".format(sys.exc_info()))