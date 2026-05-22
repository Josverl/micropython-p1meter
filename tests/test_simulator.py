"""
test_simulator.py — unit tests for P1MeterSIM.fake_message().

Run on MicroPython Unix port:
    micropython tests/test_simulator.py

Run on a connected ESP32 (copy tests/ to the board first):
    mpremote run tests/test_simulator.py
"""
import sys
import os

_here = os.path.dirname(__file__)
if not _here:
    _here = '.'
sys.path.insert(0, _here + '/stubs')
sys.path.insert(1, _here + '/../src/lib')
sys.path.insert(2, _here + '/../src')

import unittest
from p1meter_sym import P1MeterSIM
from utilities import crc16


class TestFakeMessage(unittest.TestCase):

    def setUp(self):
        # Generate once; many tests re-use the same message.
        self.msg = P1MeterSIM.fake_message()

    def test_returns_string(self):
        "fake_message() must return a str, not bytes."
        self.assertTrue(isinstance(self.msg, str))

    def test_starts_with_slash(self):
        "Telegram header must start with '/'."
        self.assertTrue(self.msg.startswith('/'))

    def test_ends_with_crlf(self):
        "Message must end with \\r\\n."
        self.assertTrue(self.msg.endswith('\r\n'))

    def test_contains_exclamation(self):
        "Telegram footer must contain '!'."
        self.assertIn('!', self.msg)

    def test_crc_is_four_hex_digits(self):
        "The 4 characters before the final \\r\\n must be uppercase hex."
        crc_str = self.msg[-6:-2]
        self.assertEqual(len(crc_str), 4)
        # Must be valid hex
        int(crc_str, 16)

    def test_crc_is_valid(self):
        """
        The 4-character hex CRC appended to the message must match the
        CRC-16/ARC computed over the body (everything up to and including '!').
        """
        # Body = everything before the 4-char CRC + CRLF
        body = self.msg[:-6]          # ends with '!'
        crc_in_msg = self.msg[-6:-2]  # 4 hex chars
        crc_computed = "{0:04X}".format(crc16(bytearray(body, 'utf8')))
        self.assertEqual(crc_in_msg, crc_computed)

    def test_contains_obis_codes(self):
        "Simulated telegram must contain at least one recognisable OBIS code."
        self.assertIn('1-0:1.7.0', self.msg)

    def test_multiple_calls_are_independent(self):
        "Each call may return different power values (random), but both are valid."
        msg1 = P1MeterSIM.fake_message()
        msg2 = P1MeterSIM.fake_message()
        # Both must be valid strings starting with /
        self.assertTrue(msg1.startswith('/'))
        self.assertTrue(msg2.startswith('/'))
        # Both CRCs must be valid
        for msg in (msg1, msg2):
            body = msg[:-6]
            crc_in = msg[-6:-2]
            crc_exp = "{0:04X}".format(crc16(bytearray(body, 'utf8')))
            self.assertEqual(crc_in, crc_exp)


if __name__ == '__main__':
    unittest.main()
