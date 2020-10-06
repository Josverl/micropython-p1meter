#####################################################
# MQTT Stuff
#####################################################

import logging
import ubinascii
import machine
import network
import ujson as json
import uasyncio as asyncio
from umqtt.simple import MQTTClient, MQTTException
from wifi import wlan

from config import broker , publish_as_json


# Logging
log = logging.getLogger('mqttclient')

# Default MQTT server to connect to
CLIENT_ID = b'p1_meter_'+ubinascii.hexlify(machine.unique_id())
TOPIC = b"p1_meter"
mqtt_client = None

async def ensure_mqtt_connected(broker = broker):
    #todo: refactor to class to get rid of global
    global mqtt_client

    #todo: WaitFor / sync / semafore Wifi connected
    # also try/check for OSError: 118 when connecting, to avoid breaking the loop
    # repro: machine.reset()
    while True:
        if mqtt_client is None:
            log.info("create mqtt client {0}".format(broker['server']))
            mqtt_client  = MQTTClient(CLIENT_ID, broker['server'] , user=broker['user'], password=broker['password'])
        if mqtt_client.sock is None:
            log.warning('need to start mqqt client')
            # but only if the adapter has got an IP assigned // DHCP
            if wlan.status() == network.STAT_GOT_IP:
                try:
                    log.info("connecting to mqtt server {0}".format(broker['server']))
                    r = mqtt_client.connect()
                    log.info("Connected")
                    log.info("Connected :{}".format(r))
                except (MQTTException, OSError)  as e:
                    log.error(e)
                    # [Errno 104] ECONNRESET
                    # server reset : so possibly:
                    # - incorrect password
                    # - network blocked
            else:
                log.warning('network not ready')
        # check
        await asyncio.sleep(10)

# incorrect password
# INFO:mqttclient:connecting to mqtt server 192.168.1.99
# Traceback (most recent call last):
#   File "uasyncio/core.py", line 1, in run_until_complete
#   File "mqttclient.py", line 45, in ensure_mqtt_connected
#   File "umqtt/simple.py", line 99, in connect
# MQTTException: 5

#####################################################
#
#####################################################
async def publish_readings(readings: list) -> bool:
    if publish_as_json:
        log.debug("publish {} meter readings as json".format(len(readings)))
        #write readings as json
        topic = TOPIC + b"/json"
        if not publish_one(topic, json.dumps(readings)):
            return False

    log.info("publish {} meter readings".format(len(readings)))
    #write readings 1 by one
    for meter in readings:
        topic = TOPIC + b"/"+ meter['meter'].encode()
        if not publish_one(topic, meter['reading']):
            return False
    return True

def publish_one(topic, value) -> bool:
    global mqtt_client
    r = True
    try:
        mqtt_client.publish(topic, value)
    except BaseException as error:
        log.error("Error: sending json to MQTT : {}".format(error) )
        r = False
        try:
            mqtt_client.disconnect()
        except BaseException as error:
            log.error("Error: while disconnecting MQTT : {}".format(error) )
        finally:
            # flag reinit of MQTT client
            mqtt_client = None
    return r
