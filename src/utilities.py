"16 bit Cyclic redundancy check (CRC)"
from uctypes import UINT16

# @timed_function
def crc16(buf :bytearray) -> UINT16 :
    """CRC-16-ANSI calculated over the characters in the data message using the polynomial: x16 + x15 + x2 + 1

    note: in the p1 message replace `\\n` by `\\r\\n`"""
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



