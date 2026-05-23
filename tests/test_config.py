"""
test_config.py — regression tests for config.py values.

These tests document the expected types and constraints for every
important configuration knob.  A failing test here points to a bug
in config.py.

Run on MicroPython Unix port:
    micropython tests/test_config.py

Run on a connected ESP32 (copy tests/ to the board first):
    mpremote run tests/test_config.py
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
import config as cfg


class TestBrokerConfig(unittest.TestCase):

    def test_broker_port_is_integer(self):
        "broker['port'] must be int — passing a str to MQTTClient causes a type error."
        self.assertTrue(isinstance(cfg.broker['port'], int),
                        "broker['port'] is '{}' ({}), expected int".format(
                            cfg.broker['port'], type(cfg.broker['port']).__name__))

    def test_broker_server_is_string(self):
        self.assertTrue(isinstance(cfg.broker['server'], str))

    def test_broker_ssl_is_bool(self):
        self.assertTrue(isinstance(cfg.broker.get('ssl', False), bool))

    def test_broker_port_in_valid_range(self):
        port = cfg.broker['port']
        self.assertTrue(1 <= port <= 65535,
                        "port {} is outside the valid TCP range".format(port))


class TestIntervalConstants(unittest.TestCase):

    def test_interval_min_positive(self):
        self.assertTrue(cfg.INTERVAL_MIN > 0)

    def test_interval_mem_positive(self):
        self.assertTrue(cfg.INTERVAL_MEM > 0)

    def test_interval_all_positive(self):
        self.assertTrue(cfg.INTERVAL_ALL > 0)

    def test_interval_sim_positive(self):
        self.assertTrue(cfg.INTERVAL_SIM > 0)

    def test_interval_all_greater_than_min(self):
        "INTERVAL_ALL must be larger than INTERVAL_MIN to guarantee at least one suppress."
        self.assertTrue(cfg.INTERVAL_ALL > cfg.INTERVAL_MIN)


class TestNetworkConfig(unittest.TestCase):

    def test_root_topic_is_bytes(self):
        self.assertTrue(isinstance(cfg.ROOT_TOPIC, bytes))

    def test_host_name_is_bytes(self):
        self.assertTrue(isinstance(cfg.HOST_NAME, bytes))

    def test_homenet_has_ssid_and_password(self):
        self.assertIn('SSID', cfg.homenet)
        self.assertIn('password', cfg.homenet)


class TestCodetable(unittest.TestCase):

    def test_no_duplicate_obis_codes(self):
        "Each OBIS pattern should appear at most once in the codetable."
        patterns = [entry[0] for entry in cfg.codetable]
        seen = set()
        duplicates = []
        for p in patterns:
            if p in seen:
                duplicates.append(p)
            seen.add(p)
        self.assertEqual(duplicates, [],
                         "Duplicate OBIS patterns found: {}".format(duplicates))

    def test_codetable_entries_are_2_tuples(self):
        "Every entry must be a 2-tuple (pattern, replacement)."
        for entry in cfg.codetable:
            self.assertEqual(len(entry), 2,
                             "Entry {} is not a 2-tuple".format(entry))

    def test_version_constant_exists(self):
        "A VERSION constant must be defined."
        self.assertTrue(hasattr(cfg, 'VERSION'))
        self.assertTrue(isinstance(cfg.VERSION, str))
        self.assertTrue(len(cfg.VERSION) > 0)


if __name__ == '__main__':
    unittest.main()
