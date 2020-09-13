from . driver_base import DriverBase, ChannelOrder
from .. import log
import sys
import time
import os
import traceback
from enum import Enum
try:
    import serial
    import serial.tools.list_ports
except ImportError as e:
    error = "Please install pyserial 3.4+! pip install pyserial"
    log.error(error)
    raise ImportError(error)

from distutils.version import LooseVersion

if LooseVersion(serial.VERSION) < LooseVersion('3.4'):
    error = "pyserial v{} found, please upgrade to v3.4+! pip install pyserial --upgrade".format(
        serial.VERSION)
    log.error(error)
    raise ImportError(error)

class Serial(DriverBase):
    """Main driver for Serial based LED strips"""
    foundDevices = []
    deviceIDS = {}
    deviceVers = []

    def __init__(self, type, dev="", hardwareID="1D50:60AB", SPISpeed=2, restart_timeout=3, deviceID=None, **kwds):
        """
        Args:
            type:  LED type from `LEDTYPE`
            dev: Device path such as /dev/ttyACM0 or COM2
            hardwareID: USB Vendor ID, Product ID pair (no need to change for AllPixel)
            SPISpeed: SPI speed in MHz for SPI-type LEDs
            restart_timeout: Wait time before reconnect attempt after reconfigure
            **kwds:  keywords passed to `spixel.drivers.driver_base.DriverBase`.
        """
        super(Serial, self).__init__(**kwds)

        if SPISpeed < 1 or SPISpeed > 24 or not (type in SPIChipsets):
            SPISpeed = 1

        self._hardwareID = hardwareID
        self._SPISpeed = SPISpeed
        self._com = None
        self._type = type
        self._bufPad = 0
        self.dev = dev
        self.devVer = 0
        self.restart_timeout = restart_timeout
        self.deviceID = None
        if self.deviceID is not None and (self.deviceID < 0 or self.deviceID > 255):
            raise ValueError("deviceID must be between 0 and 255")
        
    def setup(self, pixels):
        super().setup(pixels)
        resp = self._connect()
        if resp == RETURN_CODES.REBOOT:  # reboot needed
            log.info(
                "Reconfigure and reboot needed, waiting for controller to restart...")
            self._com.close()
            time.sleep(self.restart_timeout)
            resp = self._connect()
            if resp != RETURN_CODES.SUCCESS:
                Serial._printError(resp)
            else:
                log.info("Reconfigure success!")
        elif resp != RETURN_CODES.SUCCESS:
            Serial._printError(resp)

        if type in SPIChipsets:
            log.info("Using SPI Speed: %sMHz", self._SPISpeed)

    def __exit__(self, type, value, traceback):
        if self._com is not None:
            log.info("Closing connection to: %s", self.dev)
            self._com.close()

    @staticmethod
    def findSerialDevices(hardwareID="1D50:60AB"):
        hardwareID = "(?i)" + hardwareID  # forces case insensitive
        if len(Serial.foundDevices) == 0:
            Serial.foundDevices = []
            Serial.deviceIDS = {}
            for port in serial.tools.list_ports.grep(hardwareID):
                id = Serial.getDeviceID(port[0])
                ver = Serial.getDeviceVer(port[0])
                if id >= 0:
                    Serial.deviceIDS[id] = port[0]
                    Serial.foundDevices.append(port[0])
                    Serial.deviceVers.append(ver)

        return Serial.foundDevices

    @staticmethod
    def _printError(error):
        msg = "Unknown error occured."
        if error == RETURN_CODES.ERROR_SIZE:
            msg = "Data packet size incorrect."
        elif error == RETURN_CODES.ERROR_UNSUPPORTED:
            msg = "Unsupported configuration attempted."
        elif error == RETURN_CODES.ERROR_PIXEL_COUNT:
            msg = "Too many pixels specified for device."
        elif error == RETURN_CODES.ERROR_BAD_CMD:
            msg = "Unsupported protocol command. Check your device version."

        log.error("%s: %s", error, msg)
        raise BiblioSerialError(msg)

    @staticmethod
    def _comError():
        error = "There was an unknown error communicating with the device."
        log.error(error)
        raise IOError(error)

    def _connect(self):
        try:
            if(self.dev == "" or self.dev is None):
                Serial.findSerialDevices(self._hardwareID)

                if self.deviceID is not None:
                    if self.deviceID in Serial.deviceIDS:
                        self.dev = Serial.deviceIDS[self.deviceID]
                        self.devVer = 0
                        try:
                            i = Serial.foundDevices.index(self.dev)
                            self.devVer = Serial.deviceVers[i]
                        except:
                            pass
                        log.info("Using COM Port: %s, Device ID: %s, Device Ver: %s",
                                 self.dev, self.deviceID, self.devVer)

                    if self.dev == "" or self.dev is None:
                        error = "Unable to find device with ID: {}".format(
                            self.deviceID)
                        log.error(error)
                        raise ValueError(error)
                elif len(Serial.foundDevices) > 0:
                    self.dev = Serial.foundDevices[0]
                    self.devVer = 0
                    try:
                        i = Serial.foundDevices.index(self.dev)
                        self.devVer = Serial.deviceVers[i]
                    except:
                        pass
                    devID = -1
                    for id in Serial.deviceIDS:
                        if Serial.deviceIDS[id] == self.dev:
                            devID = id

                    log.info("Using COM Port: %s, Device ID: %s, Device Ver: %s",
                             self.dev, devID, self.devVer)

            try:
                self._com = serial.Serial(self.dev, timeout=5)
            except serial.SerialException as e:
                ports = Serial.findSerialDevices(self._hardwareID)
                error = "Invalid port specified. No COM ports available."
                if len(ports) > 0:
                    error = "Invalid port specified. Try using one of: \n" + \
                        "\n".join(ports)
                log.info(error)
                raise BiblioSerialError(error)

            packet = Serial._generateHeader(CMDTYPE.SETUP_DATA, 4)
            packet.append(self._type)  # set strip type
            byteCount = self.buf_byte_count
            if self._type in BufferChipsets:
                if self._type == LEDTYPE.APA102 and self.devVer >= 2:
                    pass
                else:
                    self._bufPad = BufferChipsets[self._type](self.numLEDs) * 3
                    byteCount += self._bufPad

            packet.append(byteCount & 0xFF)  # set 1st byte of byteCount
            packet.append(byteCount >> 8)  # set 2nd byte of byteCount
            packet.append(self._SPISpeed)
            self._com.write(packet)

            resp = self._com.read(1)
            if len(resp) == 0:
                Serial._comError()

            return ord(resp)

        except serial.SerialException as e:
            error = "Unable to connect to the device. Please check that it is connected and the correct port is selected."
            log.error(traceback.format_exc())
            log.error(error)
            raise e

    @staticmethod
    def _generateHeader(cmd, size):
        packet = bytearray()
        packet.append(cmd)
        packet.append(size & 0xFF)
        packet.append(size >> 8)
        return packet

    @staticmethod
    def setDeviceID(dev, id):
        if id < 0 or id > 255:
            raise ValueError("ID must be an unsigned byte!")

        try:
            com = serial.Serial(dev, timeout=5)

            packet = Serial._generateHeader(CMDTYPE.SETID, 1)
            packet.append(id)
            com.write(packet)

            resp = com.read(1)
            if len(resp) == 0:
                Serial._comError()
            else:
                if ord(resp) != RETURN_CODES.SUCCESS:
                    Serial._printError(ord(resp))

        except serial.SerialException:
            log.error("Problem connecting to serial device.")
            raise IOError("Problem connecting to serial device.")

    @staticmethod
    def getDeviceID(dev):
        packet = Serial._generateHeader(CMDTYPE.GETID, 0)
        try:
            com = serial.Serial(dev, timeout=5)
            com.write(packet)
            resp = ord(com.read(1))
            return resp
        except serial.SerialException:
            log.error("Problem connecting to serial device.")
            return -1

    @staticmethod
    def getDeviceVer(dev):
        packet = Serial._generateHeader(CMDTYPE.GETVER, 0)
        try:
            com = serial.Serial(dev, timeout=0.5)
            com.write(packet)
            ver = 0
            resp = com.read(1)
            if len(resp) > 0:
                resp = ord(resp)
                if resp == RETURN_CODES.SUCCESS:
                    ver = ord(com.read(1))
            return ver
        except serial.SerialException:
            log.error("Problem connecting to serial device.")
            return 0

    def set_master_brightness(self, brightness):
        """Set master brightness value for entire device"""
        packet = Serial._generateHeader(CMDTYPE.BRIGHTNESS, 1)
        packet.append(brightness)
        self._com.write(packet)
        resp = ord(self._com.read(1))
        if resp != RETURN_CODES.SUCCESS:
            Serial._printError(resp)
            return False
        else:
            return True

    # Push new data to strand
    def _update(self, data):
        count = self.buf_byte_count + self._bufPad
        packet = Serial._generateHeader(CMDTYPE.PIXEL_DATA, count)

        self.fix_data(data)

        packet.extend(self._buf)
        packet.extend([0] * self._bufPad)
        self._com.write(packet)

        resp = self._com.read(1)
        if len(resp) == 0:
            Serial._comError()
        if ord(resp) != RETURN_CODES.SUCCESS:
            Serial._printError(ord(resp))

        self._com.flushInput()


class BiblioSerialError(Exception):
    pass

class LEDTYPE:
    """Enumeration of valid LED types"""
    GENERIC = 0  # Use if the serial device only supports one chipset
    LPD8806 = 1
    WS2801 = 2
    # These are all the same
    WS2811 = 3
    WS2812 = 3
    WS2812B = 3
    NEOPIXEL = 3
    APA104 = 3
    # 400khz variant of above
    WS2811_400 = 4

    TM1809 = 5
    TM1804 = 5
    TM1803 = 6
    UCS1903 = 7
    SM16716 = 8
    APA102 = 9
    LPD1886 = 10
    P9813 = 11

SPIChipsets = [
    LEDTYPE.LPD8806,
    LEDTYPE.WS2801,
    LEDTYPE.SM16716,
    LEDTYPE.APA102,
    LEDTYPE.P9813
]

# Chipsets here require extra pixels padded at the end
# Key must be an LEDTYPE
# value a lambda function to calc the value based on numLEDs
BufferChipsets = {
    LEDTYPE.APA102: lambda num: (int(num / 64.0) + 1)
}

class CMDTYPE:
    SETUP_DATA = 1  # config data (LED type, SPI speed, num LEDs)
    PIXEL_DATA = 2  # raw pixel data will be sent as [R1,G1,B1,R2,G2,B2,...]
    BRIGHTNESS = 3  # data will be single 0-255 brightness value, length must be 0x00,0x01
    GETID = 4
    SETID = 5
    GETVER = 6
    SYNC = 7


class RETURN_CODES:
    SUCCESS = 255  # All is well
    REBOOT = 42  # Device reboot needed after configuration
    ERROR = 0  # Generic error
    ERROR_SIZE = 1  # Data receieved does not match given command length
    ERROR_UNSUPPORTED = 2  # Unsupported command
    ERROR_PIXEL_COUNT = 3  # Too many pixels for device
    ERROR_BAD_CMD = 4  # Unknown Command

__pdoc__ = {}
__pdoc__['CMDTYPE'] = False
__pdoc__['RETURN_CODES'] = False

__pdoc__['Serial.deviceIDS'] = False
__pdoc__['Serial.deviceVers'] = False
__pdoc__['Serial.foundDevices'] = False