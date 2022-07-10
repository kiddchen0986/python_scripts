import ctypes as c
import time
import argparse
from functools import wraps

FPC_SUCCESS = 0
SWING_SPI_FREQUENCY_HZ = 5000000

def timing(oldFunc):
    @wraps(oldFunc)
    def insider(*args, **kwargs):
        start = time.time()
        status = oldFunc(*args, **kwargs)
        end = time.time()
        print('%r (%r, %r) %2.2f sec' % (oldFunc.__name__, args, kwargs, end - start))

        return status

    return insider

def logging(oldFunc):
    @wraps(oldFunc)
    def insider(*args, **kwargs):
        with open("logging.txt", 'a') as f:
            status = oldFunc(*args, **kwargs)
            f.write('%r (%r, %r): %s\n' % (oldFunc.__name__, args, kwargs, str(status)))
            return status

    return insider

class GpioCtrl(c.Structure):
    __field__= [
        ("led_override", c.c_bool),
        ("directions", c.c_int * 3),
        ("levels", c.c_int * 3)
    ]

class FpcHalDeviceHandle_t(c.Structure):
    __fields__ = [
        ("comm_handle", c.c_void_p),
        ("device_type", c.c_int),
        ("log_callback", c.c_void_p),
        ("gpio_ctrl", GpioCtrl),
        ("hal_func", c.c_void_p),
        ("hal_func_handle", c.c_void_p)
    ]

class HAL(object):
    def __init__(self, hal_library_name):
        self.hal_library_name = hal_library_name
        self.hal_dll = c.CDLL(hal_library_name)
        assert self.hal_dll != None

    def setup_interface(self):
        self.OpenDevice = self.hal_dll.HalOpenDevice
        self.SetResetLow = self.hal_dll.HalSetResetLow
        self.WriteReadSpi = self.hal_dll.HalWriteReadSpi
        self.ReadIrq = self.hal_dll.HalReadIrq
        self.SetResetHigh = self.hal_dll.HalSetResetHigh
        self.SetLedIndicators = self.hal_dll.HalSetLedIndicators
        self.SetSpiFrequency = self.hal_dll.HalSetSpiFrequency
        self.CloseDevice = self.hal_dll.HalCloseDevice

    def __str__(self):
        return self.hal_library_name + ": " + str(self.hal_dll)
@logging
@timing
def SetUpDevice(MyHal, device):
    str_format = None
    status = MyHal.OpenDevice(c.pointer(device), str_format)
    if status != FPC_SUCCESS:
        print("OpenDevice fail:", status)
        return status

    status = MyHal.SetSpiFrequency(c.pointer(device), SWING_SPI_FREQUENCY_HZ)
    if status != FPC_SUCCESS:
        print("OpenDevice fail:", status)
        return status

    status = MyHal.SetResetLow(c.pointer(device))
    if status != FPC_SUCCESS:
        print("SetResetLow fail:", status)
        return status

    time.sleep(0.1)

    status = MyHal.SetResetHigh(c.pointer(device))
    if status != FPC_SUCCESS:
        print("SetResetHigh fail:", status)
        return status

    status = MyHal.SetLedIndicators(c.pointer(device), True, True, True)
    if status != FPC_SUCCESS:
        print("SetResetHigh fail:", status)
        return status

    time.sleep(0.1)

    status = MyHal.SetLedIndicators(c.pointer(device), False, False, False)
    if status != FPC_SUCCESS:
        print("SetResetHigh fail:", status)
        return status

    irq = c.create_string_buffer(1)

    status = MyHal.ReadIrq(c.pointer(device), irq)
    if status != FPC_SUCCESS:
        print("SetResetHigh fail:", status)
        return status

    if irq.raw == b'\x01':
        return FPC_SUCCESS
    else:
        print("Incorrect IRQ", irq.raw)
        return -1

@logging
def RunSPI(op, data, device):
    values = data.split(",")

    if op == "read":
        value = int(values[0], 16) if values[0].strip().startswith('0x') else int(values[0])
        if value == 4 or value == 8:
            cmd = (c.c_uint8 * 2)()
            cmd[0] = value
            cmd[1] = int(values[1], 16) if values[1].strip().startswith('0x') else int(values[1])
        else:
            cmd = c.c_uint8(value)

        read_buffer_len = int(values[-1], 16) if values[-1].strip().startswith('0x') else int(values[-1])
        #read_buffer = c.create_string_buffer(read_buffer_len)
        read_buffer = (c.c_uint8 * read_buffer_len)()
        status = MyHal.WriteReadSpi(c.pointer(device), c.byref(cmd), 1, read_buffer, read_buffer_len)
        if status != FPC_SUCCESS:
            print("Read", values, "fail:", status)
        else:
            #print("Read", values, "success, buffer:", read_buffer.raw)
            print("Read", values, "success, buffer:", c.cast(read_buffer, c.POINTER(c.c_uint8))[0:read_buffer_len])

    elif op == "write":
        write_buffer_len = len(values)
        cmd = (c.c_uint8 * write_buffer_len)()
        for i, val in enumerate(values):
            cmd[i] = int(val, 16) if val.strip().startswith('0x') else int(val)

        status = MyHal.WriteReadSpi(c.pointer(device), c.byref(cmd), write_buffer_len, None, 0)

        if status != FPC_SUCCESS:
            print("Write", values, "fail:", status)
        else:
            print("Write", values, "success")

    return status

def to_hex_string(values):
  "convert list of values to a hex string"
  return ", ".join('%02x' % value for value in values)

def ReadSPI(device, command):
    read_data = command.split("-r")
    if len(read_data) > 1:
        for val in read_data[1].strip().split(";"):
            RunSPI("read", val, device)

def WriteSPI(device, command):
    write_data = command.split("-w")
    if len(write_data) > 1:
        for val in write_data[1].strip().split(";"):
            status = RunSPI("write", val, device)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", help="Hal library name, default hal_ftdi.dll", type=str, default="hal_ftdi.dll")

    args = parser.parse_args()

    print("Hal Library name: ", args.d)

    MyHal = HAL(args.d)
    MyHal.setup_interface()

    device = FpcHalDeviceHandle_t()

    try:
        status = SetUpDevice(MyHal, device)

        if status == FPC_SUCCESS:
            print("Open device succeed")
            while(True):
                print("-------------------")
                command = input("You could input -r 0x14,8;0xfc,2 to read spi or -w 0x34 to write spi\n-q to quit\n")
                if '-q' in command:
                    break

                if '-r' in command and '-w' in command:
                    print("Only support -r or -w alone")
                    continue

                if '-r' in command:
                    ReadSPI(device, command)
                elif '-w' in command:
                    WriteSPI(device, command)

    finally:
        MyHal.CloseDevice(c.pointer(device))


