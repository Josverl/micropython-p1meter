import uasyncio as asyncio
import sys
import network
import utime as time
import machine
from config import homenet
import logging

wlan = network.WLAN(network.STA_IF) 

# Logging
log = logging.getLogger(__name__)

async def ensure_connected():
    while True:
        if not (wlan.active() and wlan.isconnected()):
            log.warning('found wifi not connected')
            await connect()
        # check 
        await asyncio.sleep(10)

async def connect():
    # create station interface - Standard WiFi client
    if not wlan.active():
        log.info("Activating Wlan {0}".format(homenet['SSID']))
        # activate the interface
        wlan.active(True)
        # connect to a known WiFi ( from config file) 
        wlan.connect(homenet['SSID'], homenet['password'])

        while wlan.status() == network.STAT_CONNECTING:
            await asyncio.sleep(1)
        t = time.ticks_ms()
        timeout = 50 # self.timeout
        log.info('Checking WiFi stability for {}ms'.format(2 * timeout))
        # Timeout ensures stable WiFi and forces minimum outage duration
        while wlan.isconnected() and time.ticks_diff(time.ticks_ms(), t) < 2 * timeout:
            await asyncio.sleep(1)

    else:
        log.debug("Wlan already active")

    # Note that this may take some time, so we need to wait
    # Wait 5 sec or until connected
    tmo = 50
    while not wlan.isconnected():
        await asyncio.sleep_ms(100)
        tmo -= 1
        if tmo == 0:
            break

    # prettyprint the interface's IP/netmask/gw/DNS addresses
    config = wlan.ifconfig()
    log.info("Connected to Wifi with IP:{0}, Network mask:{1}, Router:{2}, DNS: {3}".format( *config ))
