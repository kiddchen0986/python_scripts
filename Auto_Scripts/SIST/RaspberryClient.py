#!/usr/bin/env python3
import subprocess
import requests
from hashlib import sha256

def getServerUrl():
    return 'http://FPC-MLM-WKS001:8080'


class Android(object):
    @staticmethod
    def isConnected():
        return True
    
    @staticmethod
    def getHardware():
        return "None"

    @staticmethod
    def getHWID():
        return "None"


class BEP(object):
    @staticmethod
    def isConnected():
        return False

    @staticmethod
    def getHardware():
        return "None"
    
    @staticmethod
    def getHWID():
        return "None"


def cache(data, file):
    try:
        if ( data != "None" ):
            with open(u'cached_'+file, 'wb') as file:
                file.write(data.encode('utf-8'))
            return data
        with open(u'cached_'+file, 'rb') as file: 
            return str(file.read(), 'UTF-8')
    except:
        return data


def auto_update_client():
    remote_version = requests.get(getServerUrl() + '/client/version').text.strip()
    local_version = cache("None", "client_version")

    if (local_version == "None" or local_version == ''):
        with open(u'do_report.py', 'rb') as file: 
            local_version = cache(sha256(file.read()).hexdigest(), "client_version")
    if (local_version != remote_version):
        with open(u'do_report.py', 'wb') as file:
            file.write(requests.get(getServerUrl() + '/client').text.encode('utf-8'))
        cache(remote_version, "client_version")


def report():
    hardware = "None"
    hwid = "None"
    
    if ( Android.isConnected() ):
        hardware = cache(Android.getHardware(), "android_hardware")
        hwid = cache(Android.getHWID(), "android_hwid")

    elif ( BEP.isConnected() ):
        hardware = cache(BEP.getHardware(), "bep_hardware")
        hwid = cache(BEP.getHWID(), "bep_hwid")

    environment = {'hardware' : hardware.strip(), 'sensor' : hwid.strip() }
    requests.put(getServerUrl(), json = environment )


if __name__=="__main__":
    # auto_update_client() # auto update is disabled since it has not been tested.
    report()
