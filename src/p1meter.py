import binascii
import uasyncio as asyncio
from machine import UART
import ure as re
import ujson as json
import logging
from wifi import wlan
from config import broker

# Logging
log = logging.getLogger('p1meter')

# ------------------------
# decode bytearray
# ------------------------
def decode(a:bytearray):
    "bytearray to string"
    return binascii.hexlify(a).decode()


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
t : dict = None
async def publish_readings(telegram: dict):
    t = telegram
    if telegram['readings']:
        log.info("considering {} meter readings for mqtt publication".format(len(telegram['readings'])))

        if 1:
            #write readings as json 
            topic = TOPIC + b"/json"
            try:
                mqtt_client.publish(topic, json.dumps(telegram['readings'])) 
            except BaseException as error:  
                log.error("Error: sending to MQTT : {}".format(error) )
                #todo: flag reinit of MQTT client 

        #write readings 1 by one 
        for meter in telegram['readings']:
            topic = TOPIC + b"/"+ meter['meter'].encode()
            try:
                mqtt_client.publish(topic, meter['reading']) 
            except BaseException as error:  
                log.error("Error: sending to MQTT : {}".format(error) )
                break
                #todo: flag reinit of MQTT client 
    return

#####################################################
async def receiver(uart_rx: UART):
    sreader = asyncio.StreamReader(uart_rx)
    #start with an empty telegram, explicit to avoid references 
    # possible solution : copy.deepcopy(dict1) not on micropython
    # copy by hydrate from json ?
    # create class -- TMO 

    tele = {'header': '', 'data': [], 'readings': [],  'footer': ''}
    while True:
        line = await sreader.readline()
        log.debug("raw: {}".format(line))
        if line:
            # to string and remove last character : \n
            try:
                line = line.decode()
                line = line[:-1]
            except BaseException as error:  # pylint: disable=unused-variable
                line = "--noise--"
            # log.debug("clean".format(line))
            if line[0] == '/':
                log.debug('header found')
                tele = {'header': '', 'data': [], 'readings': [],  'footer': ''}

            elif line[0] == '!':
                log.debug('footer found')
                tele['footer'] = line
                # todo: -check CRC 
                await publish_readings(tele)
                # publish_readings(tele)

            elif line != "--noise--":
                tele['data'].append(line)
                # split data into readings
                out = re.match('(.*?)\((.*)\)', line)
                if out:
                    lineinfo = {'meter': out.group(1), 'reading':None, 'unit': None}

                    reading = out.group(2).split('*')
                    if len(reading) == 2:
                        lineinfo['reading'] = reading[0]
                        lineinfo['unit'] = reading[1]
                    else:
                        lineinfo['reading'] = reading[0]
                    log.debug(lineinfo)
                    tele['readings'].append(lineinfo )
    



