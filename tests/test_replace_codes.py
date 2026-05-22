"""
test_replace_codes.py — unit tests for replace_codes() in p1meter.py.

Run on MicroPython Unix port:
    micropython tests/test_replace_codes.py

Run on a connected ESP32 (copy tests/ to the board first):
    mpremote run tests/test_replace_codes.py
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
from p1meter import replace_codes


def _reading(meter, reading='0', unit=None):
    "Helper: create a reading dict."
    return {'meter': meter, 'reading': reading, 'unit': unit}


class TestReplaceCodes(unittest.TestCase):

    # ------------------------------------------------------------------
    # Basic OBIS → topic substitutions
    # ------------------------------------------------------------------

    def test_instant_consumption(self):
        "1-0:1.7.0 → instant/consumption (with kW unit appended)."
        readings = [_reading('1-0:1.7.0', '00.317', 'kW')]
        result = replace_codes(readings)
        self.assertEqual(result[0]['meter'], 'instant/consumption_kW')

    def test_instant_production(self):
        "1-0:2.7.0 → instant/production."
        readings = [_reading('1-0:2.7.0', '00.000', 'kW')]
        result = replace_codes(readings)
        self.assertEqual(result[0]['meter'], 'instant/production_kW')

    def test_version_no_unit(self):
        "1-3:0.2.8 → equipment/version, no unit appended."
        readings = [_reading('1-3:0.2.8', '42')]
        result = replace_codes(readings)
        self.assertEqual(result[0]['meter'], 'equipment/version')

    def test_date_time_with_wildcard(self):
        "0-0:1.0.0.255 matches the .* wildcard."
        readings = [_reading('0-0:1.0.0.255', '200909224846S')]
        result = replace_codes(readings)
        self.assertEqual(result[0]['meter'], 'date_time')

    def test_total_consumption_low_tariff(self):
        "1-0:1.8.1 → total/consumption_low_tariff_kWh."
        readings = [_reading('1-0:1.8.1', '009248.534', 'kWh')]
        result = replace_codes(readings)
        self.assertEqual(result[0]['meter'], 'total/consumption_low_tariff_kWh')

    def test_tariff_indicator(self):
        "0-0:96.14.0 → tariff_indicator."
        readings = [_reading('0-0:96.14.0', '0002')]
        result = replace_codes(readings)
        self.assertEqual(result[0]['meter'], 'tariff_indicator')

    # ------------------------------------------------------------------
    # Regex capture-group substitutions
    # ------------------------------------------------------------------

    def test_mbus_device_id_capture(self):
        "0-1:96.1.1 → equipment/m-bus_1_id (capture group \\1 = 1)."
        readings = [_reading('0-1:96.1.1', '4730...')]
        result = replace_codes(readings)
        self.assertEqual(result[0]['meter'], 'equipment/m-bus_1_id')

    def test_gas_meter_dutch(self):
        "0-1:24.2.1 → total/gas_meter_m3 (Dutch OBIS code)."
        readings = [_reading('0-1:24.2.1', '05907.828', 'm3')]
        result = replace_codes(readings)
        self.assertEqual(result[0]['meter'], 'total/gas_meter_m3')

    # ------------------------------------------------------------------
    # Voltage sags/swells — no more short_power_drops duplicate
    # ------------------------------------------------------------------

    def test_voltage_sag_l1(self):
        "1-0:32.32.0 → outages/voltage_sags/l1 (not short_power_drops)."
        readings = [_reading('1-0:32.32.0', '00000')]
        result = replace_codes(readings)
        self.assertEqual(result[0]['meter'], 'outages/voltage_sags/l1')

    def test_voltage_sag_l2(self):
        readings = [_reading('1-0:52.32.0', '00000')]
        result = replace_codes(readings)
        self.assertEqual(result[0]['meter'], 'outages/voltage_sags/l2')

    def test_voltage_sag_l3(self):
        readings = [_reading('1-0:72.32.0', '00000')]
        result = replace_codes(readings)
        self.assertEqual(result[0]['meter'], 'outages/voltage_sags/l3')

    def test_voltage_swell_l1(self):
        "1-0:32.36.0 → outages/voltage_swells/l1 (not short_power_peaks)."
        readings = [_reading('1-0:32.36.0', '00000')]
        result = replace_codes(readings)
        self.assertEqual(result[0]['meter'], 'outages/voltage_swells/l1')

    def test_voltage_swell_l2(self):
        readings = [_reading('1-0:52.36.0', '00000')]
        result = replace_codes(readings)
        self.assertEqual(result[0]['meter'], 'outages/voltage_swells/l2')

    def test_voltage_swell_l3(self):
        readings = [_reading('1-0:72.36.0', '00000')]
        result = replace_codes(readings)
        self.assertEqual(result[0]['meter'], 'outages/voltage_swells/l3')

    # ------------------------------------------------------------------
    # Unknown / unmapped codes
    # ------------------------------------------------------------------

    def test_unknown_code_unchanged(self):
        "An OBIS code that is not in the table is left unchanged."
        readings = [_reading('9-9:99.99.9', '0')]
        result = replace_codes(readings)
        self.assertEqual(result[0]['meter'], '9-9:99.99.9')

    # ------------------------------------------------------------------
    # Unit appending behaviour
    # ------------------------------------------------------------------

    def test_no_unit_not_appended(self):
        "When unit is None the meter name has no trailing underscore."
        readings = [_reading('1-3:0.2.8', '42', None)]
        result = replace_codes(readings)
        self.assertFalse(result[0]['meter'].endswith('_'))

    def test_empty_unit_not_appended(self):
        "When unit is an empty string it is not appended."
        readings = [_reading('1-3:0.2.8', '42', '')]
        result = replace_codes(readings)
        self.assertFalse(result[0]['meter'].endswith('_'))

    def test_multiple_readings_all_replaced(self):
        "All readings in a list are processed."
        readings = [
            _reading('1-0:1.7.0', '00.317', 'kW'),
            _reading('1-0:2.7.0', '00.000', 'kW'),
        ]
        result = replace_codes(readings)
        self.assertEqual(result[0]['meter'], 'instant/consumption_kW')
        self.assertEqual(result[1]['meter'], 'instant/production_kW')


if __name__ == '__main__':
    unittest.main()
