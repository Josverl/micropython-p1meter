#####################################################
# MQTT Stuff
#####################################################

from micropython import const
import time
import ubinascii
import machine
from umqtt.simple import MQTTClient
from machine import Pin
import network
import logging
from wifi import wlan
import uasyncio as asyncio
import ujson as json

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
        if mqtt_client == None:
            log.info("create mqtt client {0}".format(broker['server']))
            mqtt_client  = MQTTClient(CLIENT_ID, broker['server'] , user=broker['user'], password=broker['password'])
        if mqtt_client.sock == None:
            log.warning('need to start mqqt client')
            # but only if the adapter has got an IP assigned // DHCP
            if wlan.status() == network.STAT_GOT_IP:
                try: 
                    log.info("connecting to mqtt server {0}".format(broker['server']))
                    r = mqtt_client.connect()
                    log.info("Connected")
                    log.info("Connected :{}".format(r))
                except OSError as e:
                    log.error(e)
                    pass
            else:
                log.warning('network not ready')
        # check 
        await asyncio.sleep(10)



#####################################################
#
#####################################################
async def publish_readings(readings: list):
    log.info("considering {} meter readings for mqtt publication".format(len(readings)))

    if publish_as_json:
        #write readings as json 
        topic = TOPIC + b"/json"
        try:
            mqtt_client.publish(topic, json.dumps(readings)) 
        except BaseException as error:  
            log.error("Error: sending to MQTT : {}".format(error) )
            #todo: flag reinit of MQTT client 

    #write readings 1 by one 
    for meter in readings:
        topic = TOPIC + b"/"+ meter['meter'].encode()
        try:
            mqtt_client.publish(topic, meter['reading']) 
        except BaseException as error:  
            log.error("Error: sending to MQTT : {}".format(error) )
            break
            #todo: flag reinit of MQTT client 
    return

