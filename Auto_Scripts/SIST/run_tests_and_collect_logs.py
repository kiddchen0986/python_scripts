import os
import sys
import argparse
from RemoteRaspberry import RemoteRaspberry
from AdbHandler import ADB


INSTRUMENATION_APP = "com.fingerprints.si.test/android.support.test.runner.AndroidJUnitRunner"
ROOT_FOLDER = os.path.split(os.getcwd())[0]
LOG_FOLDER = os.path.join(ROOT_FOLDER, "devicelogs")


def clear_logcat(remote_adb):
    remote_adb.run_adb_command("logcat -b crash -c")
    remote_adb.run_adb_command("logcat -b main -c")
    remote_adb.run_adb_command("logcat -b events -c")


def fixate_screen(remote_adb):
    print("Disabling screen rotation")
    remote_adb.run_adb_command("shell content insert --uri content://settings/system "
                      "--bind name:s:accelerometer_rotation --bind value:i:0 ")
    remote_adb.run_adb_command("shell content insert --uri content://settings/system "
                      "--bind name:s:user_rotation --bind value:i:0 ")


def disable_password(remote_adb):
    print("Disabling locksreen password")
    remote_adb.run_adb_command(
            "shell sqlite3 /data/system/locksettings.db \"UPDATE locksettings "
            "SET value=0 WHERE name='lockscreen.password_type\'\";")
    remote_adb.run_adb_command(
            "shell sqlite3 /data/system/locksettings.db \"UPDATE locksettings "
            "SET value=0 WHERE name='lockscreen.disabled\'\";")


def enable_kpi(model, remote_adb):
    print("Enabling KPI log")
    if model == "hikey" or model == "hikey960":
        print("Making a diag_logs folder in data folder for the hikey")
        #Creating two folders, which one will be used depends on the android version
        remote_adb.run_adb_command("shell mkdir /data/diag_logs")
        remote_adb.run_adb_command("shell mkdir /data/fpc/diag_logs")

    kpi_command = "setprop vendor.fpc.kpi.enable 1"
    kpi_command1 = "setprop fpc_kpi 1"
    remote_adb.run_adb_command("shell " + kpi_command)
    remote_adb.run_adb_command("shell " + kpi_command1)


def disable_vibration(remote_adb):
    print("Disabling vibration")
    remote_adb.run_adb_command("shell mkdir -p /sys/class/timed_output/vibrator")
    remote_adb.run_adb_command(
        "shell echo \"0 > /sys/class/timed_output/vibrator/amp\"")


def stay_awake(remote_adb):
    print("Enabling stay awake")
    remote_adb.run_adb_command("shell settings put global stay_on_while_plugged_in 3")


def all_tests_executed():
    current_found = False
    numtest_found = False
    num_testcases = -1
    executed_testscases = 0
    for line in reversed(open("android/testReport.txt").readlines()):
        if "current=" in line and not current_found:
            executed_testscases = line.split("=")[1]
            current_found = True
        if "numtests=" in line and not numtest_found:
            num_testcases = line.split("=")[1]
            numtest_found = True
        if current_found and numtest_found: break

    return num_testcases == executed_testscases


def is_ui_automation_connected():
    for line in open("android/testReport.txt").readlines():
        if "UiAutomation not connected" in line:
            return False

    return True


def run_tests(remote_adb, rpi):
    print("Running tests")
    attempts = 0
    while True:
        _, s_out, s_err = remote_adb.run_adb_command("shell pm list instrumentation")
        if (s_out + s_err).find("com.fingerprints.si.test") == -1:
            raise Exception("Failed to find instrumenation app")

        command = "shell am instrument -w -r -e class com.fingerprints.automation.testcases.TestSuite " \
                  "%s > android/testReport.txt" % (INSTRUMENATION_APP)

        _, stdout, stderr = remote_adb.run_adb_command(command)

        if stdout.find("am start: start an Activity.  Options are") == -1:
            print("Downloading testReport.txt")
            rpi.download("android/testReport.txt")

            #Check test report for UiAutomation not connected
            if is_ui_automation_connected():
                # Check in testReport.txt that all test cases were executed
                if (all_tests_executed()):
                    print("All tests in suite executed")
                    return True
                else:
                    print("[ERROR] All tests were not executed")
                    return False
            else:
                attempts += 1
                if attempts >= 2:
                    print("[ERROR] UIAutomator not connected second time aborting")
                    return False
                else:
                    print("[WARNING] UIAutomator not connected found, retrying")
                    #Delete testReport.txt
                    os.remove("android/testReport.txt")
                    #Delete logs on device
                    remote_adb.run_adb_command("shell rm /storage/emulated/0/logs/*.*")
                    #Delete logs in android/androidlogs/ on RPI
                    rpi.run_command("rm -rf android/devicelogs/*.*")

        else:
            print("Failed to run test application")
            print(stderr + stdout)
            return False

def collect_logs(remote_adb, rpi):
    remote_adb.run_adb_command("logcat -d -b crash > android/devicelogs/LOGCAT_crash.log")
    remote_adb.run_adb_command("logcat -d -b main > android/devicelogs/LOGCAT_main.log")
    remote_adb.run_adb_command("logcat -d -b events > android/devicelogs/LOGCAT_events.log")
    remote_adb.run_adb_command("shell dmesg > android/devicelogs/DMESG.log")
    remote_adb.run_adb_command("shell getprop > android/devicelogs/prop.log")
    remote_adb.run_adb_command("pull /storage/emulated/0/logs android/devicelogs")

    try:
        remote_adb.run_adb_command("pull /data/anr android/devicelogs", retry=False)
    except Exception as _:
        print("/data/anr/ does not exist")

    try:
        remote_adb.run_adb_command("pull /data/tombstones android/devicelogs", retry=False)
    except Exception as _:
        print("/data/tombstones/ does not exist")

    try:
        remote_adb.run_adb_command("pull /data/diag_logs android/devicelogs", retry=False)
    except Exception as _:
        print("/data/diag_logs/ does not exist")

    try:
        remote_adb.run_adb_command("pull /data/fpc/diag_logs android/devicelogs", retry=False)
    except Exception as _:
        print("/data/fpc/diag_logs/ does not exist")

    # rpi.download

    rpi.sftp.chdir("android")

    os.chdir("../")

    rpi.download("devicelogs")

    os.chdir("SI")

    rpi.sftp.chdir()



def start(model, rpi):
    remote_adb = ADB(rpi)
    remote_adb.run_adb_command("logcat -G 1M")
    print("Getting startup logcat")
    destination = "android/devicelogs/LOGCAT_startup.log"
    remote_adb.run_adb_command("logcat -d > {}".format(destination))
    print("Clear logcat")
    clear_logcat(remote_adb)
    fixate_screen(remote_adb)
    # disable_password()
    enable_kpi(model, remote_adb)
    remote_adb.run_adb_command("shell \"echo performance > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor\"")
    disable_vibration(remote_adb)
    # Stop hikey from sleeping
    if model == "hikey" or model == "hikey960":
        stay_awake(remote_adb)

        remote_adb.run_adb_command("root")
        remote_adb.run_adb_command("remount")
        remote_adb.wait_for_device()
        os.chdir("SI")
		
    test_run_ok = run_tests(remote_adb, rpi)
    collect_logs(remote_adb, rpi)

    return test_run_ok


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--sensor', '-s', required=True, help='FPC Sensor on phone')
    parser.add_argument('--model', '-m', required=True, help='Target model')
    parser.add_argument('--manifest', '-mv', required=True, help='Manifest version')
    parser.add_argument('--ip', '-ip', required=True, help='IP to the Raspberry Pi')

    args = parser.parse_args()
    args.model = args.model.lower()
    args.sensor = args.sensor.lower()
    args.manifest = args.manifest.lower()
    rpi = RemoteRaspberry(args.ip)

    result = start(args.model, rpi)
    #sys.exit(0 if result else 1)
