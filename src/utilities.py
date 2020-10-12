"16 bit Cyclic redundancy check (CRC)"
import machine
from machine import Pin
from uctypes import UINT16
from neopixel import NeoPixel
import esp32
import config as cfg

# @timed_function
def crc16(buf :bytearray) -> UINT16 :
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



def enable_rts(enable:bool=True):
    _pin_rts = Pin(5, Pin.OUT, enable)
    _pin_rts.value(enable)




class Feedback():
    "simple feedback via 3 neopixel leds"
    # fb = Feedback()
    # fb.update(0,fb.GREEN)

    L_P1 = 0
    L_MQTT = 1
    L_NET = 2

    BLACK=(0,0,0)
    WHITE=(20,20,20)
    RED=(64,0,0)
    GREEN=(0,32,0)
    BLUE=(0,0,64)
    YELLOW=(64,64,0)
    PURPLE=(64,0,64)
    np = None

    def __init__(self):
        _pin_np = Pin(cfg.NEOPIXEL_PIN, Pin.OUT)        # set to output to drive NeoPixels
        self.np = NeoPixel(_pin_np, 3)                  # create NeoPixel driver for 3 pixels
        self.np.write()

    def update(self, n:int=2, color: tuple=(64,64,64)):
        if self.np:
            self.np[n]=color    #pylint: disable= unsupported-assignment-operation
            self.np.write()

    def clear(self, color: tuple=(0,0,0)):
        for n in range(3):
            self.np[n]=color    #pylint: disable= unsupported-assignment-operation
            self.np.write()
