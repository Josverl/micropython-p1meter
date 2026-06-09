#####################################################
# MQTT Stuff
#####################################################

import logging

import network
import uasyncio as asyncio
import ujson as json
from umqtt.simple import MQTTClient, MQTTException

from config import HOST_NAME, ROOT_TOPIC, broker, publish_as_json
from utilities import reboot
import wifi

# Logging
log = logging.getLogger('mqttclient')

# Running count of consecutive negative-errno socket errors.
# Triggers a reboot when it exceeds 10 (see connect()).
_conn_errors = 0

class MQTTClient2(object):
    """
    Async-friendly wrapper around umqtt.simple.MQTTClient.

    Credentials and TLS settings are read from config.broker:
        'server'     : broker hostname or IP address
        'port'       : integer port (1883 plain, 8883 TLS)
        'user'       : MQTT username
        'password'   : MQTT password
        'ssl'        : True to enable TLS (optional, default False)
        'ssl_params' : dict of keyword args for ussl.wrap_socket (optional)
    """

    def __init__(self):
        self.mqtt_client = None
        self.server = broker['server']
        self.user = broker['user']
        self.password = broker['password']
        self.port = broker['port']
        self.ssl = broker.get('ssl', False)
        self.ssl_params = broker.get('ssl_params', {})
        self.ping_failed = 0
        # Callbacks invoked after a successful (re)connection so that
        # dependent objects (e.g. P1Meter) can reset their cached state.
        self._reconnect_callbacks = []

    def add_reconnect_callback(self, callback):
        "Register a zero-argument callable to be called after each successful MQTT connect."
        self._reconnect_callbacks.append(callback)

    def healthy(self) -> bool:
        "Return True when the MQTT connection is believed to be up."
        state = True
        try:
            if wifi.wlan.status() != network.STAT_GOT_IP:
                log.debug('wlan.status != GOT_IP')
                state = False
            elif not self.mqtt_client:
                log.debug('mqtt_client = None')
                state = False
            elif self.mqtt_client.sock is None:
                log.debug('mqtt_client.sock = None')
                state = False
            else:
                try:
                    self.mqtt_client.ping()
                    self.ping_failed = 0
                except (OSError, MQTTException) as e:
                    log.warning('mqtt_client.ping() failed')
                    self.ping_failed += 10
                    if self.ping_failed > 50:
                        log.debug("Disconnecting due to ping fail count")
                        self.disconnect()

        except (OSError, MQTTException) as e:
            log.debug("error during health check: {} {}".format(type(e).__name__, e))
            if type(e) is type(OSError()):
                if e.args[0] == 128:
                    log.debug("Disconnecting")
                    self.disconnect()
            state = False

        if not state:
            log.warning('mqtt not healthy')
        return state

    def disconnect(self):
        "Disconnect and clear the client so ensure_mqtt_connected will reconnect."
        if self.mqtt_client:
            log.debug('disconnecting from mqtt')
            try:
                self.mqtt_client.disconnect()
            except BaseException as error:
                log.error("Oops while disconnecting MQTT : {}".format(error))
            finally:
                self.mqtt_client = None

    async def connect(self):
        """
        Connect (or reconnect) to the MQTT broker.

        This is a coroutine so that the event loop remains responsive between
        retry attempts.  On a failed attempt the method sleeps for 5 s before
        returning, giving other tasks a chance to run.
        """
        global _conn_errors
        if self.mqtt_client is None:
            log.info("create mqtt client {0}".format(self.server))
            self.mqtt_client = MQTTClient(
                HOST_NAME, self.server,
                port=self.port,
                user=self.user, password=self.password,
                keepalive=30,
                ssl=self.ssl, ssl_params=self.ssl_params,
            )
        if wifi.wlan_stable and wifi.wlan.status() == network.STAT_GOT_IP:
            try:
                log.info("connecting to mqtt server {0}".format(self.server))
                self.mqtt_client.connect()
                log.info("Connected to MQTT broker")
                _conn_errors = 0
                for cb in self._reconnect_callbacks:
                    try:
                        cb()
                    except Exception as e:
                        log.error("reconnect callback failed: {}".format(e))
            except (MQTTException, OSError) as e:
                if type(e) is type(MQTTException()):
                    if e.args[0] == 5:
                        log.error("MQTT error {}: check username/password".format(e))
                    elif e.args[0] == 2:
                        log.error("MQTT error {}: check server address or network".format(e))
                    else:
                        log.error("{} {}".format(type(e).__name__, e))
                else:
                    if int(e.args[0]) == -2:
                        log.error("OS Error {}: Host unreachable, check mDNS / server address".format(e))
                    elif e.args[0] in (113, 23):
                        log.error("OS Error {}: Host unreachable, check server address or network".format(e))
                    elif e.args[0] < 0:
                        _conn_errors += 1
                        if _conn_errors > 10:
                            log.error("OS Error {}: too many errors, attempting reboot".format(e))
                            reboot()
                        else:
                            log.error("OS Error {}".format(e))
                    else:
                        log.error("{} {}".format(type(e).__name__, e))
                # Back off before the next retry so the event loop stays live.
                await asyncio.sleep_ms(5000)
        else:
            log.warning('network not ready/stable, deferring MQTT connect')
            await asyncio.sleep_ms(1000)

    async def ensure_mqtt_connected(self):
        """
        Background task: reconnect to MQTT whenever the connection is lost.
        Runs forever; meant to be scheduled with asyncio.create_task().
        """
        while True:
            if self.mqtt_client is None or self.mqtt_client.sock is None:
                log.warning('need to (re)connect to MQTT broker')
                await self.connect()
            await asyncio.sleep(10)

    async def publish_readings(self, readings: list) -> bool:
        if publish_as_json:
            topic = ROOT_TOPIC + b"/json"
            if not self.publish_one(topic, json.dumps(readings)):
                log.warning("Could not publish {} meter readings as json".format(len(readings)))
                return False
            log.debug("Published {} meter readings as json".format(len(readings)))

        for meter in readings:
            topic = ROOT_TOPIC + b"/" + meter['meter'].encode()
            if not self.publish_one(topic, meter['reading']):
                log.warning("Could not publish {} meter readings".format(len(readings)))
                return False
        log.info("Published {} meter readings".format(len(readings)))
        return True

    def publish_one(self, topic, value) -> bool:
        "Publish a single value to a MQTT topic."
        if not self.healthy():
            return False
        r = True
        try:
            self.mqtt_client.publish(topic, value)
        except BaseException as error:
            log.error("Problem sending {} to MQTT : {}".format(topic, error))
            r = False
            self.disconnect()
        return r
