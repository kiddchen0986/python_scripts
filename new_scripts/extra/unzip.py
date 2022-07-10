# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#
import sys
import os
import zipfile

Getpath = input("Please enter log path:")
os.chdir(Getpath)
cwd = os.getcwd()
print("Changed current directory is: ", cwd)


def unzip(cwd):
    files = os.walk(cwd)

    for _, _, filenames in files:
        for filename in filenames:
            portion = os.path.splitext(filename)
            if portion[1] == '.zip':
                fz = zipfile.ZipFile(filename, 'r')
                for file in fz.namelist():
                    fz.extract(file)


if __name__ == "__main__":
    try:
        unzip(cwd)

    except Exception as e:
        print("Error {} caught in script".format(sys.exc_info()))
