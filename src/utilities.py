"16 bit Cyclic redundancy check (CRC)"
import re
from uctypes import UINT16
from timed_func import timed_function
from config import codetable

# @timed_function
def crc16(buf :bytearray) -> UINT16 :
    """CRC-16-ANSI calculated over the characters in the data message using the polynomial: x16 + x15 + x2 + 1

    note: in the p1 message replace `\\n` by `\\r\\n`"""
    # http://www.nodo-domotica.nl/images/8/86/DSMR.pdf
    # https://en.wikipedia.org/wiki/Cyclic_redundancy_check
    crc = 0x0000
    for c in buf:
        crc ^= c
        for i in range(8):
            if crc & 0x01:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc


@timed_function
def replace_codes(readings :list)-> list :
    "replace the codes by their topic as defined in the codetable"
    for reading in readings:
        for code in codetable:
            if re.match(code[0],reading['meter']):
                print( code[0], '--> ', end='')
                reading['meter'] = re.sub(code[0], code[1], reading['meter'])
                print(reading['meter'] )
                break
    return readings

