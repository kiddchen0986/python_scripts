#!/usr/bin/env python3
import os
import argparse
# #####################################################################
# Download apps (ImageInjection, ImageTool, ImageCollection,
# ImageSubscription, SensorTestTool and SpiMaster) from artifactory
#
# #####################################################################


def start(manifest, spi_interception):

    imageinjection = "ImageInjection"
    software = "sw26 or higher"

    if manifest.lower().find("sw22") > -1:
        software = "sw22"
        imageinjection = "ImageInterception"
    if manifest.lower().find("sw23.1") > -1:
        software = "sw23.1"
    if manifest.lower().find("sw23.2") > -1:
        software = "sw23.2"
    if manifest.lower().find("sw24") > -1:
        software = "sw24"
    if manifest.lower().find("sw25") > -1:
        software = "sw25.0"

    os.chdir("../")

    # Only download apps for SW below SW26
    if software != "sw26 or higher":
        print("python -m appdownload  -n imagetool -s %s -t release -f %s" % (software, os.path.join("artifacts", "APK", "ImageTool")))
        if os.system("python -m appdownload  -n imagetool -s %s -t release -f %s" % (software, os.path.join("artifacts", "APK", "ImageTool"))) == 1:
            print("[WARNING] Could not download Image Tool from Artifactory")

        print("python -m appdownload  -n imagecollection -s %s -t release -f %s" % (software, os.path.join("artifacts", "APK", "ImageCollection")))
        if os.system("python -m appdownload  -n imagecollection -s %s -t release -f %s" % (software, os.path.join("artifacts", "APK", "ImageCollection"))) == 1:
            print("[WARNING] Could not download Image Collection from Artifactory")

        print("python -m appdownload  -n imagesubscription -s %s -t release -f %s" % (software, os.path.join("artifacts", "APK", "ImageSubscription")))
        if os.system("python -m appdownload  -n imagesubscription -s %s -t release -f %s" % (software, os.path.join("artifacts", "APK", "ImageSubscription"))) == 1:
            print("[WARNING] Could not download Image Subscription from Artifactory")

        print("python -m appdownload  -n %s -s %s -t release -f %s" % (imageinjection.lower(), software, os.path.join("artifacts", "APK", imageinjection)))
        if os.system("python -m appdownload  -n %s -s %s -t release -f %s" % (imageinjection.lower(), software, os.path.join("artifacts", "APK", imageinjection))) == 1:
            print('[WARNING] Could not download', imageinjection.lower(),  'from Artifactory')

        print("python -m appdownload  -n sensortesttool -s %s -t release -f %s" % (software, os.path.join("artifacts", "APK", "SensorTestTool")))
        if os.system("python -m appdownload  -n sensortesttool -s %s -t release -f %s" % (software, os.path.join("artifacts", "APK", "SensorTestTool"))) == 1:
            print("[WARNING] Could not download Sensor Test Tool from Artifactory")

    if spi_interception == "true":
        print("python -m appdownload  -n spimaster -s %s -t release -f %s" % ("sw26", os.path.join("artifacts", "APK", "SpiMaster")))
        if os.system("python -m appdownload  -n spimaster -s %s -t release -f %s" % ("sw26", os.path.join("artifacts", "APK", "SpiMaster"))) == 1:
            print("[WARNING] Could not download Spi Master from Artifactory")

    os.chdir("SI")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', '-mv', required=True, help='Manifest version')
    parser.add_argument('--spi', '-spi', required=True, help='_SPI_INTERCEPTION_')

    args = parser.parse_args()
    args.manifest = args.manifest.lower()

    start(args.manifest, args.spi)
