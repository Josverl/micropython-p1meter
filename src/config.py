#pylint: disable=anomalous-backslash-in-string

from micropython import const

# Base SSID to connect to
homenet = {'SSID': 'IoT', 'password': 'MicroPython'}
broker = {'server': '192.168.1.99', 'user': 'sensor', 'password': 'SensorPassport'}

#also publish as json
publish_as_json = False


# Serial Pins for meter connection
RX_PIN_NR = const(2)
# TX = Only for simulation
TX_PIN_NR = const(5)

"""a list to translate the ... codes into the topic names used to publish to mqtt
each entry should consist of a 2-tuple
    - a string or regex match
    - the replacement string or regex
        ("1-0:1.7.0","actual_consumption")                  # string replacement
        ("(\d)-0:1.7.0","actual_consumption\device_\\1")    # regex replacement

Note:
    For readbility the periods `.` have been used in the regex match strings.
    While in the regex syntax the `.` will match any character, this does not cause any issues in practice.

    Several codes are specified in the documentation as ending in .255, while in practice this seems optional.
    therefore the regexes end in .* that matches both the ending `.255` and the shorter notation.

    It is possible to use regex capture groups () in the match string,
    and then use that value in the replacement string by specifying \\1 (or \\2 for the 2nd capture).

    the equipment number for the equipment_id and the equipment_type appears to be different.
"""
codetable = (
    ("1-3:0.2.8.*"          , "version"),
    ("0-0:1.0.0.*"          , "date_time"),
    ("0-1:96.1.0.*"         , "equipment_id/p1_meter"),
    ("0-0:96.14.0.*"        , "tariff_indicator"),
    ("1-0:1.8.1"            , "consumption_low_tarif"),
    ("1-0:1.8.2"            , "consumption_high_tarif"),

    ("1-0:2.8.1"            , "production_low_tarif"),
    ("1-0:2.8.2"            , "production_high_tarif"),

    ("1-0:1.7.0.*"          , "actual_consumption"),
    ("1-0:2.7.0.*"          , "actual_produced"),

    ("1-0:21.7.0"           , "instant_power_usage/l1"),
    ("1-0:41.7.0"           , "instant_power_usage/l2"),
    ("1-0:61.7.0"           , "instant_power_usage/l3"),

    ("1-0:31.7.0"           , "instant_power_current/l1"),
    ("1-0:51.7.0"           , "instant_power_current/l2"),
    ("1-0:71.7.0"           , "instant_power_current/l3"),

    ("0-0:96.14.0"          , "actual_tarif_group"),

    ("0-0:96.7.21"          , "short_power_outages"),
    ("0-0:96.7.9"           , "long_power_outages"),

    ("1-0:32.32.0"          , "short_power_drops"),
    ("1-0:32.36.0"          , "short_power_peaks"),

    ("1-0:22.7.0.*"         , "instantanious_active_power/l1"),
    ("1-0:42.7.0.*"         , "instantanious_active_power/l2"),
    ("1-0:62.7.0.*"         , "instantanious_active_power/l3"),

    ("1-0:32.7.0"           , "instant_voltage/l1"),
    ("1-0:52.7.0"           , "instant_voltage/l2"),
    ("1-0:72.7.0"           , "instant_voltage/l3"),

    ("1-0:32.32.0"          , "voltage_sags/l1"),
    ("1-0:52.32.0"          , "voltage_sags/l2"),
    ("1-0:72.32.0"          , "voltage_sags/l3"),

    ("1-0:32.36.0"          , "voltage_swells/l1"),
    ("1-0:52.36.0"          , "voltage_swells/l2"),
    ("1-0:72.36.0"          , "voltage_swells/l3"),

    ("1-0:99.97.0"          , "power_failure_event_log"),

    ("0-(\d):96.1.1.*"      , "equipment_id/m-bus_\\1"),
    ("0-(\d):24.1.0"        , "equipment_type/id_\\1"),

    ("(\d)-1:24.2.1"        , "gas_meter_m3"),
    ("0-0:96.13.(/d)"       , "message/\\1")

)
