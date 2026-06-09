"""
test_crc16.py — unit tests for the CRC-16/ARC implementation in utilities.py.

Run on MicroPython Unix port:
    micropython tests/test_crc16.py

Run on a connected ESP32 (copy tests/ to the board first):
    mpremote run tests/test_crc16.py
"""
import sys
import os

_here = os.path.dirname(__file__)
if not _here:
    _here = '.'
sys.path.insert(0, _here + '/mocks')
sys.path.insert(1, _here + '/../src/lib')
sys.path.insert(2, _here + '/../src')

import unittest
from utilities import crc16


class TestCRC16(unittest.TestCase):

    def test_empty_buffer_is_zero(self):
        "CRC of an empty buffer must be 0 (initial value with no data)."
        self.assertEqual(crc16(b''), 0x0000)

    def test_standard_check_value(self):
        "CRC-16/ARC check value for ASCII '123456789' is 0xBB3D."
        self.assertEqual(crc16(b'123456789'), 0xBB3D)

    def test_single_byte(self):
        "CRC of a single null byte is deterministic."
        result = crc16(b'\x00')
        self.assertTrue(isinstance(result, int))
        self.assertEqual(result, crc16(b'\x00'))   # idempotent

    def test_deterministic(self):
        "The same input always produces the same output."
        data = b'/XMX5LGBBFG1012650850\r\n1-3:0.2.8(42)\r\n!'
        self.assertEqual(crc16(data), crc16(data))

    def test_different_inputs_differ(self):
        "Different inputs produce different CRCs (no trivial collision)."
        self.assertNotEqual(crc16(b'hello'), crc16(b'world'))

    def test_returns_int(self):
        "Return type must be int."
        self.assertTrue(isinstance(crc16(b'test'), int))

    def test_result_fits_in_16_bits(self):
        "Result must be in the range 0x0000–0xFFFF."
        for data in (b'', b'a', b'123456789', b'\xff\xff\xff'):
            result = crc16(data)
            self.assertTrue(0 <= result <= 0xFFFF)

    def test_bytearray_input(self):
        "Should accept bytearray as well as bytes."
        self.assertEqual(crc16(bytearray(b'123456789')), 0xBB3D)


if __name__ == '__main__':
    unittest.main()
