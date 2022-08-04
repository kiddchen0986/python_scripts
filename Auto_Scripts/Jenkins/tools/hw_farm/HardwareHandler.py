#!/usr/bin/env python3
# #####################################################################
# Manage Raspberry HW test devices
#
# External libraries used:
#   - requests
#
# #####################################################################


import requests
import argparse
import sys
import time


def request_hardware(hardware, sensor, url):
    """Request hardware capabilities
    Returns IP on success otherwise None
    """
    try:
        payload = {'hardware': hardware,
                   'sensor': sensor}
        response = requests.post(url, json=payload)

        if response.status_code == 409:
            print("Device busy, waiting")

        while response.status_code == 409:
            time.sleep(60)
            response = requests.post(url, json=payload)

    except Exception as e:
        print("Exception: {}".format(e))
        return None

    if response.status_code == 200:
        print("Device {} with sensor {} allocated on {}".format(hardware, sensor,
                                                                response.json()['ip']))
        return response.json()['ip']

    elif response.status_code == 404:
        print("Device {} with sensor {} not found, aborting".format(hardware, sensor))
    elif response.status_code == 409:
        print("Device {} with sensor {} not available in time, aborting".format(hardware,
                                                                                sensor))
    else:
        print("Unexpected response from server")

    return None


def release_hardware(ip, url):
    """Release hardware"""

    try:
        response = requests.delete(url + "/" + ip)
        if response.status_code == 200:
            print("{} released".format(ip))
        elif response.status_code == 405:
            print("[INFO] Hardware with ip {} is not attached to server".format(ip))
        else:
            print("Unexpected response from server")

    except Exception as e:
        print("Exception: {}".format(e))
        return 1

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Request or release Raspberry HW test devices")
    parser.add_argument('--function', '-f', required=True, choices=['request', 'release'],
                        help='request or release"')
    parser.add_argument('--hardware', '-hw', required=False, help='Hammerhead/Hikey/Bep"')
    parser.add_argument('--sensor', '-s', required=False, help='FPC Sensor')
    parser.add_argument('--ip', '-ip', required=False, help='IP to release')
    parser.add_argument('--url', '-url', required=True, help='HW Farm Server URL')
    args = parser.parse_args()

    exit_code = 1

    if args.function.lower() == 'request':
        if not args.hardware or not args.sensor:
            parser.error("Request requires --hardware, --sensor and --url")
        else:
            ip = request_hardware(args.hardware, args.sensor, args.url)
            if ip:
                # Print IP to stderr so it is not combined with regular prints
                sys.stderr.write(ip)
                exit_code = 0

    elif args.function.lower() == 'release':
        if not args.ip:
            parser.error("Release requires both --ip and --url")
        else:
            exit_code = release_hardware(args.ip, args.url)

    sys.exit(exit_code)
