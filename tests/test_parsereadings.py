"""
test_parsereadings.py — unit tests for P1Meter.parsereadings().

Run on MicroPython Unix port:
    micropython tests/test_parsereadings.py

Run on a connected ESP32 (copy tests/ to the board first):
    mpremote run tests/test_parsereadings.py
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

# Import only the parsereadings method — instantiate a minimal object to avoid
# hardware initialisation.  The stubs handle machine/neopixel/etc. imports.
from p1meter import P1Meter
from mqttclient import MQTTClient2
from utilities import Feedback


def _make_meter():
    "Return a P1Meter instance backed by stub hardware."
    return P1Meter(mq_client=MQTTClient2(), fb=Feedback())


class TestParseReadings(unittest.TestCase):

    def setUp(self):
        self.meter = _make_meter()

    # ------------------------------------------------------------------
    # Happy-path tests
    # ------------------------------------------------------------------

    def test_line_with_unit(self):
        "Numeric reading with a unit (e.g. kW) is split into reading + unit."
        lines = ["1-0:1.7.0(00.317*kW)\r\n"]
        result = self.meter.parsereadings(lines)
        self.assertEqual(len(result), 1)
        r = result[0]
        self.assertEqual(r['meter'], '1-0:1.7.0')
        self.assertEqual(r['reading'], '00.317')
        self.assertEqual(r['unit'], 'kW')

    def test_line_without_unit(self):
        "Version / integer reading has no unit."
        lines = ["1-3:0.2.8(42)\r\n"]
        result = self.meter.parsereadings(lines)
        self.assertEqual(len(result), 1)
        r = result[0]
        self.assertEqual(r['meter'], '1-3:0.2.8')
        self.assertEqual(r['reading'], '42')
        self.assertIsNone(r['unit'])

    def test_compound_reading_uses_last_value(self):
        "Gas meter lines have compound format; only the last segment is used."
        lines = ["0-1:24.2.1(200909220000S)(05907.828*m3)\r\n"]
        result = self.meter.parsereadings(lines)
        self.assertEqual(len(result), 1)
        r = result[0]
        self.assertEqual(r['reading'], '05907.828')
        self.assertEqual(r['unit'], 'm3')

    def test_empty_reading(self):
        "Empty parentheses produce an empty string reading and no unit."
        lines = ["0-0:96.13.0()\r\n"]
        result = self.meter.parsereadings(lines)
        self.assertEqual(len(result), 1)
        r = result[0]
        self.assertEqual(r['reading'], '')
        self.assertIsNone(r['unit'])

    def test_kw_energy_reading(self):
        "kWh reading parses correctly."
        lines = ["1-0:1.8.1(009248.534*kWh)\r\n"]
        result = self.meter.parsereadings(lines)
        self.assertEqual(len(result), 1)
        r = result[0]
        self.assertEqual(r['meter'], '1-0:1.8.1')
        self.assertEqual(r['reading'], '009248.534')
        self.assertEqual(r['unit'], 'kWh')

    def test_current_ampere_reading(self):
        "Ampere current reading parses correctly."
        lines = ["1-0:31.7.0(002*A)\r\n"]
        result = self.meter.parsereadings(lines)
        self.assertEqual(len(result), 1)
        r = result[0]
        self.assertEqual(r['reading'], '002')
        self.assertEqual(r['unit'], 'A')

    def test_multiple_lines(self):
        "Multiple lines are all parsed in one call."
        lines = [
            "1-0:1.7.0(00.317*kW)\r\n",
            "1-0:2.7.0(00.000*kW)\r\n",
            "1-3:0.2.8(42)\r\n",
        ]
        result = self.meter.parsereadings(lines)
        self.assertEqual(len(result), 3)

    # ------------------------------------------------------------------
    # Edge-case / error tests
    # ------------------------------------------------------------------

    def test_header_line_ignored(self):
        "Lines that do not match the OBIS pattern (e.g. /header) are skipped."
        lines = ["/XMX5LGBBFG1012650850\r\n"]
        result = self.meter.parsereadings(lines)
        self.assertEqual(len(result), 0)

    def test_noise_line_ignored(self):
        "Noise / malformed lines that do not match are silently skipped."
        lines = ["--noise--\r\n", "garbage"]
        result = self.meter.parsereadings(lines)
        self.assertEqual(len(result), 0)

    def test_empty_input(self):
        "Empty list input returns empty list."
        self.assertEqual(self.meter.parsereadings([]), [])


if __name__ == '__main__':
    unittest.main()
