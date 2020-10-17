#####################################################
# MQTT Stuff
#####################################################

import logging
import network
import ujson as json
import uasyncio as asyncio
from umqtt.simple import MQTTClient, MQTTException
from wifi import wlan, wlan_stable

from config import broker , publish_as_json, NETWORK_ID, ROOT_TOPIC
from utilities import reboot

# Logging
log = logging.getLogger('mqttclient')
VERBOSE = False
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
        state = True
        try:
            if not self.mqtt_client:
                log.debug('mqtt_client = None')
                state = False
            elif self.mqtt_client.sock is None:
                log.debug('mqtt_client.sock = None')
                state = False
            if wlan.status() != network.STAT_GOT_IP:
                log.debug('wlan.status != GOT_IP')
                state = False
            # ? do server ping ?
        except (OSError, MQTTException) as e:
            log.debug('error during health check: {}'.format(e))
            state = False

        if not state:
            if VERBOSE:
                log.warning('mqtt not healthy')
            # todo: trigger reconnect ?
        return state

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

    def connect(self):
        if wlan.status() == network.STAT_GOT_IP:
            try:
                print("connecting to mqtt server {0}".format(self.server))
                self.mqtt_client.connect()
                print("Connected")
            except (MQTTException, OSError)  as e:
                # try to give a decent error for common problems
                if type(e) is type(MQTTException()):
                    if e.args[0] == 5: # EIO
                        log.error("MQTT server error {}: {}".format(e, "check username/password"))
                    elif e.args[0] == 2: # ENOENT
                        log.error("MQTT server error {}: {}".format(e, "server address or network"))
                    else:
                        log.error("{} {}".format(type(e).__name__, e ) )
                else:
                    ## OSError
                    if e.args[0] in (113, 23) : # EHOSTUNREACH
                        log.error("OS Error {}: {}".format(e, "Host unreachable, check server address or network"))
                    elif e.args[0] < 0 : # some negative socket error
                        log.error("OS Error {}: {}".format(e, "attempting reboot to fix"))
                        reboot()
                    else:
                        log.error("{} {}".format(type(e).__name__, e ) )
        else:
            log.warning('network not ready/stable')

    async def ensure_mqtt_connected(self):

        # also try/check for OSError: 118 when connecting, to avoid breaking the loop
        # repro: machine.reset()
        while True:
            if self.mqtt_client is None:
                log.info("create mqtt client {0}".format(self.server))
                self.mqtt_client  = MQTTClient(NETWORK_ID, self.server , user=self.user, password=self.password)
            if self.mqtt_client.sock is None:
                log.warning('need to start mqqt client')
                self.connect()

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
            topic = ROOT_TOPIC + b"/json"
            if not self.publish_one(topic, json.dumps(readings)):
                return False

        log.info("publish {} meter readings".format(len(readings)))
        #write readings 1 by one
        for meter in readings:
            topic = ROOT_TOPIC + b"/"+ meter['meter'].encode()
            if not self.publish_one(topic, meter['reading']):
                return False
        return True

    def publish_one(self, topic, value) -> bool:
        "Publish a single ROOT_TOPIC to MQTT"
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
