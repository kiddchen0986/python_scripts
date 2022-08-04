import argparse
import sys
import downloadapps
import flashandroid
import run_tests_and_collect_logs
import create_test_suite
import install_apps_and_test_data
from AdbHandler import ADB
from RemoteRaspberry import RemoteRaspberry
from HardwareHandler import request_hardware
from HardwareHandler import release_hardware
import create_xml

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--sensor', '-s', required=True, help='Sensor target')
    parser.add_argument('--model', '-m', required=True, help='Model target')
    parser.add_argument('--manifest', '-mv', required=True, help='Manifest version')
    parser.add_argument('--enroll', '-iae', required=True, help='_IDENTIFY_AT_ENROL_')
    parser.add_argument('--sensortest', '-st', required=True, help='_SENSORTEST_')
    parser.add_argument('--spi', '-spi', required=True, help='_SPI_INTERCEPTION_')
    parser.add_argument('--testcase', '-tc', required=False, help='Run specific test case(s)')
    parser.add_argument('--serverurl', '-url', required=True, help='HW Farm Server URL')

    try:
        test_run = False
        args = parser.parse_args()
        if args.serverurl[-1] == "/":
            args.serverurl = args.serverurl[:-1] # Remove '/' at end

        ip = request_hardware(args.model, args.sensor, args.serverurl)
        if ip is None:
            sys.exit(1)

        args.sensor = args.sensor.lower()
        args.model = args.model.lower()
        args.manifest = args.manifest.lower()

        rpi = RemoteRaspberry(ip)
        remote_adb = ADB(rpi)

        # Clear android folder on RPI
        rpi.run_command("rm -rf android")
        rpi.run_command("mkdir android")
        rpi.run_command("mkdir android/devicelogs")

        # Download all apps. Disabled because downloading apps is only necessary for SW26
        # and earlier. Those SW are not supported anymore
        # downloadapps.start(args.manifest, args.spi)

        # Flash SW
        flashed = flashandroid.start(args.model, args.sensor, rpi)
        if not flashed:
            sys.exit(1)

        # Create TestSuite.java
        create_test_suite.start(args.sensor, args.model, args.manifest, args.enroll, args.sensortest, args.testcase)

        # Clean phone, compile and install tests, install test apps and push test data
        install_apps_and_test_data.start(args.sensor, args.model, args.manifest, args.sensortest, args.spi, rpi)

        # Run tests and collect logs
        test_run = run_tests_and_collect_logs.start(args.model, rpi)

        # Create XML from test results
        create_xml.start()

        rpi.close()
    except Exception as e:
        print("Something went wrong: " + e)
    finally:
        if ip is not None:
            release_hardware(ip, args.serverurl)
            rpi.close()
        sys.exit(test_run)



