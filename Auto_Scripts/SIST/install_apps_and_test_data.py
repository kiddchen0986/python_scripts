import argparse
from AdbHandler import ADB
import os
import subprocess
import time
from RemoteRaspberry import RemoteRaspberry

ROOT_FOLDER = os.path.split(os.getcwd())[0]
TEST_APK_FOLDER = os.path.join(ROOT_FOLDER, "SI", "app", "build", "outputs", "apk", "debug")
TEST_APK_DEBUG_FOLDER = os.path.join(ROOT_FOLDER, "SI", "app", "build", "outputs", "apk", "androidTest", "debug")
APP_APK_FOLDER = os.path.join(ROOT_FOLDER, "artifacts", "APK")
TEST_DATA_FOLDER = os.path.join(ROOT_FOLDER, "SI", "artifacts", "binaries", "fingerprints")


def clean_up_phone(remote_adb):
    print("Cleaning up old files and folders")
    remote_adb.run_adb_command("shell rm -rf /data/system/users/0/fpdata")
    remote_adb.run_adb_command("shell rm -f /data/system/users/0/settings_fingerprint.xml")
    remote_adb.run_adb_command("shell rm -rf /storage/emulated/0/logs")
    remote_adb.run_adb_command("shell rm -rf /storage/emulated/0/injection")

    remote_adb.run_adb_command("shell rm -rf /data/anr")
    remote_adb.run_adb_command("shell rm -rf /data/tombstones")
    remote_adb.run_adb_command("shell rm -rf /data/diag_logs")
    remote_adb.run_adb_command("shell rm -rf /data/fpc/diag_logs")


def compile_tests():
    print("Compiling tests")
    subprocess.check_call("gradle assembleDebug assembleDebugAndroidTest", shell=True,
                          cwd=os.path.join(ROOT_FOLDER, "SI"))


def install_tests_and_apps(spi, install_apps, software, sensortest, remote_adb):
    print("Installing tests and apps")
    remote_adb.wait_for_system()
    remote_adb.install_app(os.path.join(ROOT_FOLDER, TEST_APK_FOLDER, "app-debug.apk"))

    remote_adb.wait_for_system()
    remote_adb.install_app(os.path.join(ROOT_FOLDER, TEST_APK_DEBUG_FOLDER, "app-debug-androidTest.apk"))

    if install_apps:
        if software == "SW22":
            install_test_app("ImageInterception", os.path.join(APP_APK_FOLDER, "ImageInterception"), remote_adb)
        else:
            install_test_app("ImageInjection", os.path.join(APP_APK_FOLDER, "ImageInjection"), remote_adb)

        if sensortest:
            install_test_app("ImageTool", os.path.join(APP_APK_FOLDER, "ImageTool"), remote_adb)

        install_test_app("SensorTestTool", os.path.join(APP_APK_FOLDER, "SensorTestTool"), remote_adb)
        install_test_app("ImageCollection", os.path.join(APP_APK_FOLDER, "ImageCollection"), remote_adb)
        install_test_app("ImageSubscription", os.path.join(APP_APK_FOLDER, "ImageSubscription"), remote_adb)


def install_test_app(name, folder, remote_adb):
    print("Installing %s" % name)
    for file in os.listdir(folder):
        # Can be serveral files and we just take one of them.
        remote_adb.run_adb_command("shell rm -rf /system/priv-app/%s" % name)
        remote_adb.adb_push(os.path.join(folder, file), "/system/priv-app/%s/%s.apk" % (name, name))
        #adb.run_adb_push(os.path.join(folder, file), "/system/priv-app/%s/" % name)
        #adb.run_adb_shell("mv /system/priv-app/{0}/*.apk /system/priv-app/{0}/{0}.apk".format(name))
        break
    else:
        print("[WARNING] Failed to find %s app" % name)


def set_permissions(spi, software, sensortest, remote_adb):
    print("Setting permissions for apps")
    remote_adb.wait_for_system()
    try:
        remote_adb.run_adb_command("shell pm grant com.fingerprints.si android.permission.READ_LOGS")
        remote_adb.run_adb_command("shell pm grant com.fingerprints.si android.permission.READ_EXTERNAL_STORAGE")
        remote_adb.run_adb_command("shell pm grant com.fingerprints.si android.permission.WRITE_EXTERNAL_STORAGE")
    except:
        print('[WARNING] Could not set permissions for com.fingerprints.si')

    try:
        if software == "SW22":
            remote_adb.run_adb_command("shell pm grant com.fingerprints.imageinterception android.permission.READ_EXTERNAL_STORAGE")
            remote_adb.run_adb_command("shell pm grant com.fingerprints.imageinterception android.permission.WRITE_EXTERNAL_STORAGE")
        else:
            remote_adb.run_adb_command("shell pm grant com.fingerprints.imageinjection android.permission.READ_EXTERNAL_STORAGE")
            remote_adb.run_adb_command("shell pm grant com.fingerprints.imageinjection android.permission.WRITE_EXTERNAL_STORAGE")
    except:
        print('[WARNING] Could not set permissions Image Interception/Injection')

    try:
        if sensortest:
            remote_adb.run_adb_command("shell pm grant com.fingerprints.sensortesttool android.permission.READ_EXTERNAL_STORAGE")
            remote_adb.run_adb_command("shell pm grant com.fingerprints.sensortesttool android.permission.WRITE_EXTERNAL_STORAGE")
    except:
        print('[WARNING] Could not set permissions for Sensor Test Tool')

    try:
        remote_adb.run_adb_command("shell pm grant com.fingerprints.imagecollection android.permission.READ_EXTERNAL_STORAGE")
        remote_adb.run_adb_command("shell pm grant com.fingerprints.imagecollection android.permission.WRITE_EXTERNAL_STORAGE")
    except:
        print('[WARNING] Could not set permissions for Image Collection')

    try:
        remote_adb.run_adb_command("shell pm grant com.fingerprints.imagetool android.permission.READ_EXTERNAL_STORAGE")
        remote_adb.run_adb_command("shell pm grant com.fingerprints.imagetool android.permission.WRITE_EXTERNAL_STORAGE")
    except:
        print('[WARNING] Could not set permissions for Image Tool')

    try:
        remote_adb.run_adb_command("shell pm grant com.fingerprints.imagesubscription android.permission.READ_EXTERNAL_STORAGE")
        remote_adb.run_adb_command("shell pm grant com.fingerprints.imagesubscription android.permission.WRITE_EXTERNAL_STORAGE")
    except:
        print('[WARNING] Could not set permissions for Image Subscription')


def push_test_data(software, sensor, remote_adb):
    print("Pushing test data")
    pushed = False
    attempt = 0
    while not pushed:
        try:
            remote_adb.adb_push(os.path.join(TEST_DATA_FOLDER, software, sensor) + "/", "/storage/emulated/0/Android/data/com.fingerprints.imageinjection/files/Pictures")
            pushed = True
        except Exception as e:
            print("Failed to push data, retry")
            time.sleep(5)
            attempt += 1
            if attempt > 3:
                print("Failed to push data 3 times: " + e)
                raise e


def get_software(branch):
    software = "DEV"
    install_apps = False
    if "sw22" in branch.lower():
        software = "SW22"
        install_apps = True
    if "sw23" in branch.lower():
        software = "SW23"
        install_apps = True
    if "sw24" in branch.lower():
        software = "SW24"
        install_apps = True
    if "sw25" in branch.lower():
        software = "SW25"
        install_apps = True
    if "sw26" in branch.lower():
        software = "SW26"
    if "sw27" in branch.lower():
        software = "SW27"
    if "sw28" in branch.lower():
        software = "SW28"
    if "sw29" in branch.lower():
        software = "SW29"
    if "sw30" in branch.lower():
        software = "SW30"
    if "sw31" in branch.lower():
        software = "SW31"
    if "sw32" in branch.lower():
        software = "SW32"
    if "sw33" in branch.lower():
        software = "SW33"

    return software, install_apps


def start(sensor, model, branch, sensortest, spi, rpi):
    remote_adb = ADB(rpi)
    remote_adb.root_device()
    clean_up_phone(remote_adb)
    compile_tests()
    remote_adb.root_device()
    software, install_apps = get_software(branch)
    install_tests_and_apps(spi, install_apps, software, sensortest, remote_adb)
    remote_adb.reboot_device()
    remote_adb.root_device()
    set_permissions(spi, software, sensortest, remote_adb)
    push_test_data(software, sensor, remote_adb)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--sensor', '-s', required=True, help='FPC Sensor on phone')
    parser.add_argument('--model', '-m', required=True, help='Target model')
    parser.add_argument('--manifest', '-mv', required=True, help='Manifest version')
    parser.add_argument('--sensortest', '-st', required=True, help='_SENSORTEST_')
    parser.add_argument('--spi', '-spi', required=True, help='_SPI_INTERCEPTION_')
    parser.add_argument('--ip', '-ip', required=True, help='IP to the Raspberry Pi')

    args = parser.parse_args()
    args.model = args.model.lower()
    args.sensor = args.sensor.lower()
    args.manifest = args.manifest.lower()
    rpi = RemoteRaspberry(args.ip)

    start(args.sensor, args.model, args.manifest, args.sensortest, args.spi, rpi)
    rpi.close()
