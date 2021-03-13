#pylint: disable=anomalous-backslash-in-string

from micropython import const
from  ubinascii import  hexlify
from machine import unique_id

#------------------------------------------------
# governs the overall debug logging 
DEBUG = True
#------------------------------------------------
# run the simulator for testing (using TX_PIN_NR)
RUN_SIM = False
#------------------------------------------------

INTERVAL_MEM = 600      # force mem cleanup every 10 minutes
INTERVAL_ALL = 300      # force sending all information at 5 m interval

#autodetect my test ESP32 - M5
if hexlify(unique_id())[-6:] == b'2598b4':
    RUN_SIM = True

# Base SSID to connect to
homenet = {'SSID': 'IoT', 'password': 'MicroPython'}

#the mqtt broker to connect to
#broker = {'server': 'homeassistant.local', 'user': 'sensor', 'password': 'SensorPassport'}
# Q&D Workaround for mDNS Failure
broker = {'server': '192.168.1.99', 'user': 'sensor', 'password': 'SensorPassport'}

# webrepl password: max 8 char length
webrepl = {'active': True, 'password': "4242"}

#Network ID
NETWORK_ID = b'p1_meter'

if RUN_SIM:
    NETWORK_ID += b'_' + hexlify(unique_id())[-6:]

#MQTT topic follows network ID
ROOT_TOPIC = NETWORK_ID

# Serial Pins for meter connection
# TX pin is only used for testing/simulation but needs to be specified
RX_PIN_NR = const(2)
TX_PIN_NR = const(18)
CTS_PIN_NR = const(5)

#also publish telegram as json
publish_as_json = False

#------------------------------------------------
# A few Leds - optional
# avoid 25 Speaker on M5Base 
NEOPIXEL_PIN = const(13)



#------------------------------------------------

# a list to translate the DSMR / OBIS codes into the ROOT_TOPIC names used to publish to mqtt
# each entry should consist of a 2-tuple
#     - a string or regex match
#     - the replacement string or regex
#         ("1-0:1.7.0","actual_consumption")                  # string replacement
#         ("(\d)-0:1.7.0","actual_consumption\device_\\1")    # regex replacement
# Note:
#     For readability the periods `.` have been used in the regex match strings.
#     While in the regex syntax the `.` will match any character, this does not cause any issues in practice.

#     Several codes are specified in the documentation as ending in .255, while in practice this seems optional.
#     therefore the regexes end in .* that matches both the ending `.255` and the shorter notation.

#     It is possible to use regex capture groups () in the match string,
#     and then use that value in the replacement string by specifying \\1 (or \\2 for the 2nd capture).

#     the equipment number for the equipment_id and the equipment_type appears to be different.

codetable = (
    ("1-3:0.2.8.*"          , "equipment/version"),
    ("0-0:1.0.0.*"          , "date_time"),                         # ASCII presentation of Time stamp with Year, Month, Day, Hour, Minute, Second, and an indication whether DST is active (X=S) or DST is not active (X=W)
    ("0-1:96.1.0.*"         , "equipment/p1_meter_id"),

    ("0-(\d):96.1.1.*"      , "equipment/m-bus_\\1_id"),            # extra connected meters
    ("0-(\d):24.1.0"        , "equipment/devicetype_id_\\1"),       # extra connected (gats/water) meters

    ("0-0:96.14.0.*"        , "tariff_indicator"),
                                                                # Total Use / production in kWH
    ("1-0:1.8.1"            , "total/consumption_low_tariff"),       # Meter Reading electricity delivered to client (Tariff1) in 0,001 kWh
    ("1-0:1.8.2"            , "total/consumption_high_tariff"),      # Meter Reading electricity delivered to client (Tariff 2) in 0,001 kWh

    ("1-0:2.8.1"            , "total/production_low_tariff"),        # Meter Reading electricity delivered by client (Tariff1) in 0,001 kWh
    ("1-0:2.8.2"            , "total/production_high_tariff"),       # Meter Reading electricity delivered by client (Tariff2) in 0,001 kWh

                                                                # Actual Use / production in kilo Watt
    ("1-0:1.7.0.*"          , "instant/consumption"),              # Actual electricity power delivered (+P) in 1 Wattresolution
    ("1-0:2.7.0.*"          , "instant/production"),               # Actual electricity power received  (-P) in 1 Wattresolution

    ("(\d)-1:24.2.1"        , "total/gas_meter"),
                                                                # consumption in Watt
    ("1-0:21.7.0"           , "instant/power_consumption/l1"),       # Instantaneous active power (+P) in W resolution
    ("1-0:41.7.0"           , "instant/power_consumption/l2"),
    ("1-0:61.7.0"           , "instant/power_consumption/l3"),
                                                                # production in Watt
    ("1-0:22.7.0.*"         , "instant/power_production/l1"),        # Instantaneous active power (-P) in W resolution
    ("1-0:42.7.0.*"         , "instant/power_production/l2"),
    ("1-0:62.7.0.*"         , "instant/power_production/l3"),
                                                                # actual current in Amp resolution.
    ("1-0:31.7.0.*"         , "instant/current/l1"),
    ("1-0:51.7.0.*"         , "instant/current/l2"),
    ("1-0:71.7.0.*"         , "instant/current/l3"),


    ("1-0:32.7.0"           , "instant/voltage/l1"),                 # Instantaneous volt-age in V resolution
    ("1-0:52.7.0"           , "instant/voltage/l2"),
    ("1-0:72.7.0"           , "instant/voltage/l3"),

    ("0-0:96.7.21"          , "outages/short_power_outages"),        # Number of power failures per phase
    ("0-0:96.7.9"           , "outages/long_power_outages"),

    ("1-0:32.32.0"          , "outages/short_power_drops"),          # Number of power drops per phase
    ("1-0:32.36.0"          , "outages/short_power_peaks"),


    ("1-0:32.32.0"          , "outages/voltage_sags/l1"),            # Number of voltage sags
    ("1-0:52.32.0"          , "outages/voltage_sags/l2"),
    ("1-0:72.32.0"          , "outages/voltage_sags/l3"),

    ("1-0:32.36.0"          , "outages/voltage_swells/l1"),          # Number of voltage swells
    ("1-0:52.36.0"          , "outages/voltage_swells/l2"),
    ("1-0:72.36.0"          , "outages/voltage_swells/l3"),

    ("1-0:99.97.0"          , "outages/power_failure_event_log"),

    ("0-0:96.13.(\d)"       , "message/\\1")
)
