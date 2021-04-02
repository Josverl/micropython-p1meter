"16 bit Cyclic redundancy check (CRC)"
import utime as time
import machine
from machine import Pin
from uctypes import UINT16
from neopixel import NeoPixel
import esp32
import ntptime
import config as cfg

# @timed_function
def crc16(buf: bytearray) -> UINT16:
    """CRC-16-ANSI calculated over the characters in the data message using the polynomial: x16 + x15 + x2 + 1
    """
    # http://www.nodo-domotica.nl/images/8/86/DSMR.pdf
    # https://en.wikipedia.org/wiki/Cyclic_redundancy_check
    crc = 0x0000
    for c in buf:
        crc ^= c
        for i in range(8):          # pylint: disable=unused-variable
            if crc & 0x01:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

def cpu_temp()->float:
    "read internal ESP32 CPU temperature in Celsius"
    try:
        tf = esp32.raw_temperature()
        tc = (tf-32.0)/1.8
    except OSError:
        tc = -1
    # print("T = {0:4d} deg F or {1:5.1f}  deg C".format(tf,tc))
    return tc

def reboot(delay: int = 3):
    fb = Feedback()            # reboot after x seconds stopped when in production
    print('Rebooting in {} seconds, Ctrl-C to abort'.format(3*delay))
    for n in range(3):
        fb.update(n, fb.PURPLE)
        time.sleep(delay)
        fb.update(n, fb.BLUE)
    print('Rebooting now...')
    machine.reset()

# ref: https://forum.micropython.org/viewtopic.php?f=2&t=4034
def getntptime():
    "sync CET time from ntp server"
    try:
        year = time.localtime()[0]       #get current year      # 1st run uses null year 2020
        now = ntptime.time()
        HHMarch   = time.mktime((year, 3, (31-(int(5*year/4+4))%7), 1, 0, 0, 0, 0, 0)) #Time of March change to CEST
        HHOctober = time.mktime((year, 10, (31-(int(5*year/4+1))%7), 1, 0, 0, 0, 0, 0)) #Time of October change to CET
        if now < HHMarch:                # we are before last sunday of march
            ntptime.NTP_DELTA = 3155673600-1*3600 # CET:  UTC+1H
        elif now < HHOctober:            # we are before last sunday of october
            ntptime.NTP_DELTA = 3155673600-2*3600 # CEST: UTC+2H
        else:                            # we are after last sunday of october
            ntptime.NTP_DELTA = 3155673600-1*3600 # CET:  UTC+1H
        # set the rtc datetime from the remote server
        ntptime.settime()
    except (OSError, OverflowError):
        pass

class Feedback():
    "simple feedback via 3 neopixel leds"
    # fb = Feedback()
    # fb.update(0,fb.GREEN)

    LED_MQTT = 0
    LED_NETWORK = 1
    LED_P1METER = 2

    BLACK = (0, 0, 0)
    WHITE = (20, 20, 20)
    RED = (64, 0, 0)
    GREEN = (2, 16, 2)      # dim green
    BLUE = (0, 0, 64)
    YELLOW = (64, 64, 0)
    PURPLE = (64, 0, 64)
    np = None

    def __init__(self):
        _pin_np = Pin(cfg.NEOPIXEL_PIN, Pin.OUT)        # set to output to drive NeoPixels
        self.np = NeoPixel(_pin_np, 3)                  # create NeoPixel driver for 3 pixels
        self.np.write()

    def update(self, n: int = 2, color: tuple = PURPLE):
        if self.np:
            self.np[n] = color    #pylint: disable= unsupported-assignment-operation
            self.np.write()

    def clear(self, color: tuple = BLACK):
        for n in range(3):
            self.np[n] = color    #pylint: disable= unsupported-assignment-operation
            self.np.write()
