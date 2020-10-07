#####################################################
# MQTT Stuff
#####################################################

import logging
import network
import ujson as json
import uasyncio as asyncio
from umqtt.simple import MQTTClient, MQTTException
from wifi import wlan

from config import broker , publish_as_json, CLIENT_ID, TOPIC

# Logging
log = logging.getLogger('mqttclient')

class MQTTClient2(object):
    """
    docstring
    """
    def __init__(self):
        # TODO: broker is imported directly 
        self.mqtt_client = None
        self.server = broker['server']
        self.user = broker['user']
        self.password = broker['password']

    def healthy(self) -> bool:
        "is the client healthy?"
        ok = True
        try: 
            if not self.mqtt_client:
                log.debug('mqtt_client = None')
                ok = False
            elif self.mqtt_client.sock is None:
                log.debug('mqtt_client.sock = None')
                ok = False
            if wlan.status() != network.STAT_GOT_IP:
                log.debug('wlan.status != GOT_IP')
                ok = False
            # ? do server ping ?
        except (OSError, MQTTException) as e:
            log.debug('error during health check: {}'.format(e))
            ok = False

        if not ok:
            log.warning('mqtt not healthy')
            # todo: trigger reconnect ?
        return ok
    
    def disconnect(self):
        "disconnect and close"
        if self.mqtt_client:
            log.debug('disconnecting from mqtt')
            try:
                self.mqtt_client.disconnect()
            except BaseException as error:
                log.error("Oops while disconnecting MQTT : {}".format(error) )
            finally:
                # flag re-init of MQTT client
                self.mqtt_client = None

    def connect(self, parameter_list):
        """
        docstring
        """
        pass

    async def ensure_mqtt_connected(self):

        # also try/check for OSError: 118 when connecting, to avoid breaking the loop
        # repro: machine.reset()
        while True:
            if self.mqtt_client is None:
                log.info("create mqtt client {0}".format(self.server))
                self.mqtt_client  = MQTTClient(CLIENT_ID, self.server , user=self.user, password=self.password)
            if self.mqtt_client.sock is None:
                log.warning('need to start mqqt client')
                # but only if the adapter has got an IP assigned // DHCP
                if wlan.status() == network.STAT_GOT_IP:
                    try:
                        log.info("connecting to mqtt server {0}".format(self.server))
                        r = self.mqtt_client.connect()
                        log.info("Connected")
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
        # MQTTException: 5 (access denied ?) 

    async def publish_readings(self, readings: list) -> bool:
        if publish_as_json:
            log.debug("publish {} meter readings as json".format(len(readings)))
            #write readings as json
            topic = TOPIC + b"/json"
            if not self.publish_one(topic, json.dumps(readings)):
                return False

        log.info("publish {} meter readings".format(len(readings)))
        #write readings 1 by one
        for meter in readings:
            topic = TOPIC + b"/"+ meter['meter'].encode()
            if not self.publish_one(topic, meter['reading']):
                return False
        return True

    def publish_one(self, topic, value) -> bool:
        "Publish a single topic to MQTT"
        if not self.healthy():
            return False
        r = True
        try:
            self.mqtt_client.publish(topic, value)
        except BaseException as error:
            log.error("Problem sending json to MQTT : {}".format(error) )
            r = False
            self.disconnect()
        return r
