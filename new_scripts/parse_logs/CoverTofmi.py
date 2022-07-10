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
    files = os.listdir(cwd)
    for filename in files:
        portion = os.path.splitext(filename)
        if portion[1] == '.raw':
            newname = portion[0] + '.fmi'
            os.rename(filename, newname)


def get_valid_data(cwd):
    files = os.listdir(cwd)
    for filename in files:
        with open(filename, 'rb+') as fr:
            text = fr.read()[:-12]
        with open(filename, 'wb+') as fw:
            fw.write(text)


if __name__ == "__main__":
    try:
        covert_raw_to_fmi(cwd)
        get_valid_data(cwd)

    except Exception as e:
        print("Error {} caught in script".format(sys.exc_info()))
    finally:
        print("Covert successfully!")
