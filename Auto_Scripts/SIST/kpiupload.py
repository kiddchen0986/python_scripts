#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 22 14:34:30 2017

@author: andreas.wiberg
"""

import requests, os, argparse
from pathlib import Path

parser = argparse.ArgumentParser(description="sends oddc file to webserver \"metriccollection\"")
parser.add_argument("-f", "--sensor", help="specify sensor name.")
parser.add_argument("-m", "--model", help="specify model.")
parser.add_argument("-b", "--branch", help="specify branch.")
parser.add_argument("-e", "--extras", help="specify any additional arguments.")
parser.add_argument("-d", "--debug", action="store_true", help="for debugging only.")
parser.add_argument("-l", "--liveness", help="specify liveness version.")

args = parser.parse_args()
print("Uploading KPI data")
parcel = dict()

for arg in args.__dict__.items():
    parcel[arg[0]] = arg[1]

dirpath = ".." + os.path.sep + "devicelogs" #path to oddc directory
for filename in os.listdir(dirpath): #find csv file
    if(filename.endswith(".csv")):
        CSV_PATH=dirpath+"/"+filename
        break

software = "DEV"
if args.branch.lower().find("sw22") > -1:
    software = "SW22"
if args.branch.lower().find("sw23.1") > -1:
    software = "SW23.1"
if args.branch.lower().find("sw23.2") > -1:
    software = "SW23.2"
if args.branch.lower().find("sw24") > -1:
    software = "SW24"
if args.branch.lower().find("sw25") > -1:
    software = "SW25.0"
parcel['branch'] = software

contents = Path(CSV_PATH).read_text() #send file to webserver
parcel['data'] = contents
parcel['filename'] = filename

r = requests.post("http://fpc-metriccollection001.fingerprint.local/certs/jenkins.php", data=parcel)

if(args.debug):
    print(r.text) #print response for debugging purposes