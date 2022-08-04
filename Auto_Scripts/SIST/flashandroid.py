import os
import argparse
from RemoteRaspberry import RemoteRaspberry
from AdbHandler import ADB

ROOT_FOLDER = os.path.split(os.getcwd())[0]
IMAGE_FOLDER = os.path.join(ROOT_FOLDER, "artifacts", "images")
_adb = None
_rpi = None
_model = ''


def start(model, sensor, rpi):
    """
    Looks for the correct FW and flashes a device.
    :return: True if successful, false otherwise.
    """
    global _adb
    global _rpi
    global _model
    _adb = ADB(rpi)
    _rpi = rpi
    _model = model

    print("Flashing %s" % _model)
    # Find firmware matching model and (sensor or multi)
    for firmware in os.listdir(IMAGE_FOLDER):
        if firmware.lower().find(_model) > -1 and (firmware.lower().find(sensor) > -1 or firmware.lower().find('multi') > -1):
            print("Flashing %s" % firmware)

            # For Hikey we need to extract images from the firmware zip file
            if _model == "hikey":
                os.chdir(IMAGE_FOLDER)
                os.system("jar xvf %s boot_fat.uefi.img" % firmware)
                os.system("jar xvf %s system.img" % firmware)
                os.chdir(ROOT_FOLDER)

            if _model == "hikey960":
                 os.chdir(IMAGE_FOLDER)
                 if os.path.getsize(firmware)/(1024*1024) < 30:
                       os.system("jar xvf %s system" % firmware)
                       _model = _model + 'Temp'
                       os.chdir(ROOT_FOLDER)
                 else:
                       os.system("jar xvf %s boot.img" % firmware)
                       os.system("jar xvf %s system.img" % firmware)
                       os.system("jar xvf %s cache.img" % firmware)
                       os.system("jar xvf %s userdata.img" % firmware)
                       os.system("jar xvf %s dt.img" % firmware)
                       os.chdir(ROOT_FOLDER)

            # Create ImageTarget.txt file containing the name of the firmware
            file = open(os.path.join(ROOT_FOLDER, "ImageTarget.txt"), "w")
            file.write(firmware.replace(".zip", ""))
            file.close()

            # Start flashing, giving it 3 attempts
            flashed = False
            flash_attempt = 0
            while not flashed:
                try:   
                     if _model != "hikey960Temp":                      
                        _adb.run_adb_command('reboot bootloader') # Make sure phone is not in fastboot
                        
                        '''try:
                            _adb.run_fastboot_command("erase userdata", retry=False)
                        except Exception:
                            print("Phone did not contain userdata partition, ignoring")'''
                        
                        '''try:
                            _adb.run_fastboot_command("erase cache", retry=False)
                        except Exception:
                            print("Phone did not contain cache partition, ignoring")'''
                        
                        if _model == "hikey":
                            __flash_hikey()
                        elif _model == "hikey960":
                            __flash_hikey960()
                        elif _model == "hammerhead":
                            __flash_hammerhead(firmware)
                        else:
                            print("Unsupported platform")
                            return False 
                     else: 
                        __flash_hikey960Temp()
						
                     _adb.wait_for_device()						
                     flashed = True   
                                
                except Exception as e:
                    print(e)
                    flash_attempt += 1
                    if flash_attempt > 2:
                        __remove_firmware(firmware)  # Remove files after failed 3 flash attempts
                        print("Failed to flash phone after three attempts, aborting")
                        return False
                    print("Something went wrong during flash, rebooting and flashing again: " + e)
                    _adb.reboot_device()
            __remove_firmware(firmware)  # Remove files after successful flash
            return True

    print("Failed to find any images to upload")
    return False


def __flash_hammerhead(firmware):
    """
    Executes the actual flash for a hammerhead.
    :param firmware: name of the file to flash
    """
    _rpi.upload(os.path.join(IMAGE_FOLDER, firmware), "android/" + firmware)
    _adb.run_fastboot_command("-w update {}".format("android/" + firmware))


def __flash_hikey():
    """
    Executes the actual flash for a hikey.
    """
    boot = "boot_fat.uefi.img"
    system = "system.img"
    _rpi.upload(os.path.join(IMAGE_FOLDER, boot), "android/" + boot)
    _rpi.upload(os.path.join(IMAGE_FOLDER, system), "android/" + system)
    _adb.run_fastboot_command("flash boot {}".format("android/" + boot))
    _adb.run_fastboot_command("flash -w system {}".format("android/" + system))
    _adb.reboot_device()


def __flash_hikey960():
    """
    Executes the actual flash for a hikey960.
    """
    boot = "boot.img"
    system = "system.img"
    cache = "cache.img"
    userdata = "userdata.img"
    dts = "dt.img"
    _rpi.upload(os.path.join(IMAGE_FOLDER, boot), "android/" + boot)
    _rpi.upload(os.path.join(IMAGE_FOLDER, system), "android/" + system)
    _rpi.upload(os.path.join(IMAGE_FOLDER, cache), "android/" + cache)
    _rpi.upload(os.path.join(IMAGE_FOLDER, userdata), "android/" + userdata)
    _rpi.upload(os.path.join(IMAGE_FOLDER, dts), "android/" + dts)
    _adb.run_fastboot_command("flash boot {}".format("android/" + boot))
    _adb.run_fastboot_command("flash system {}".format("android/" + system))
    _adb.run_fastboot_command("flash cache {}".format("android/" + cache))
    _adb.run_fastboot_command("flash userdata {}".format("android/" + userdata))
    _adb.run_fastboot_command("flash dts {}".format("android/" + dts))
    _adb.reboot_device()


def __flash_hikey960Temp():
    """
    Executes the actual flash for a hikey960.
    """
    _rpi.upload(os.path.join(IMAGE_FOLDER, "system") + "/", "android/system")
    _adb.root_device()
    _adb.run_adb_command("push android/system/ " + "system")
    _adb.run_adb_command("uninstall com.fingerprints.si")
    _adb.run_adb_command("uninstall com.fingerprints.si.test")
    _adb.run_adb_command('reboot')


def __remove_firmware(firmware):
    """
    Removes the FW file.
    :param firmware: name of the file to remove
    """
    os.unlink(os.path.join(IMAGE_FOLDER, firmware))  # Remove file after failed flash
    if _model == "hikey":
        os.unlink(os.path.join(IMAGE_FOLDER, "boot_fat.uefi.img"))  # Remove file after failed flash
        os.unlink(os.path.join(IMAGE_FOLDER, "system.img"))  # Remove file after failed flash

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--sensor', '-s', required=True, help='Sensor target')
    parser.add_argument('--model', '-m', required=True, help='Model target')
    parser.add_argument('--ip', '-ip', required=True, help='IP to the Raspberry Pi')

    args = parser.parse_args()
    rpi = RemoteRaspberry(args.ip)

    start(args.model.lower(), args.sensor.lower(), rpi)
