"16 bit Cyclic redundancy check (CRC)"
import machine
from uctypes import UINT16
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

#####################################################################
# create array of leds
#####################################################################
# [led_control(i, 100) for i in range(4) ]
#
# for i in range(4):
#     led_control(i, (i+1)*100 )
#####################################################################
led_pins = ( cfg.LED_PIN_RED, cfg.LED_PIN_YELLOW, cfg.LED_PIN_GREEN, cfg.LED_PIN_BLUE)
#     machine.Pin(pin, machine.Pin.OUT)

leds = [machine.PWM(machine.Pin(pin), freq=2000, duty=0) for pin in led_pins ]
# yellow, green , red , blue
LED_RED = 0
LED_YELLOW = 1
LED_GREEN = 2
LED_BLUE = 3

def led_control(n :int=0,bright :int=0, freq=2000):
    if n<0 or n>len(leds) or bright <0 or bright > 1000:
        return False
    #print(n,bright)
    leds[n].duty(bright)
    leds[n].freq(freq)
    return True

def led_toggle(n :int=0, bright :int=100):
    if n<0 or n>len(leds) or bright <0 or bright > 1000:
        return False
    # print(n,bright)
    leds[n].duty(0 if leds[n].duty() else bright)
