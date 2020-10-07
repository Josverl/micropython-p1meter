import uasyncio as asyncio
import sys
import network
import utime as time
import machine
from config import homenet
import logging

wlan = network.WLAN(network.STA_IF)
wlan_stable = False

# Logging
log = logging.getLogger(__name__)

async def ensure_connected():
    global wlan_stable
    # check state on first call.
    if check_stable():
        ifconfig()
    while True:
        if not wlan or not wlan.active() or not wlan.isconnected():
            wlan_stable = False
            log.warning('found wifi not connected')
            await connect_as()
        # check
        await asyncio.sleep(10)

def activate():
    "only start the wifi connection"
    # connect to a known WiFi ( from config file)
    log.debug('step 1')
    if not wlan.active():
        log.debug('step 1.1')
        wlan.active(True)
    log.debug('step 1.2')
    if not wlan.isconnected():
        log.debug('step 2')
        log.info("Activating Wlan {0}".format(homenet['SSID']))
        wlan.connect(homenet['SSID'], homenet['password'])

async def connect_as():
    global wlan_stable
    log.debug("create station interface - Standard WiFi client")
    if not wlan.isconnected():
        log.debug('activate')
        activate()
        # Note that this may take some time, so we need to wait
        await asyncio.sleep_ms(500)
        # Wait 5 sec or until connected
        t = time.ticks_ms()
        timeout = 5000
        while wlan.status() == network.STAT_CONNECTING and time.ticks_diff(time.ticks_ms(), t) < timeout:
            log.debug('connecting...')
            await asyncio.sleep_ms(200)
        log.debug('step 3')

    else:
        log.debug("Wlan already active")

    wlan_stable = await check_stable(duration =100)
    if wlan_stable:
        ifconfig()
    else: 
        log.warning("Unable to connect to Wlan {0}".format(homenet['SSID']))

def ifconfig():
    # prettyprint the interface's IP/netmask/gw/DNS addresses
    config = wlan.ifconfig()
    log.info("Connected to Wifi with IP:{0}, Network mask:{1}, Router:{2}, DNS: {3}".format( *config ))    

async def check_stable(duration: int = 2000):
        t = time.ticks_ms()
        log.info('Checking WiFi stability for {} ms'.format(duration))
        # Timeout ensures stable WiFi and forces minimum outage duration
        while wlan.isconnected() and time.ticks_diff(time.ticks_ms(), t) < duration:
            await asyncio.sleep_ms(10)
        return wlan.isconnected()

def check_stable2(duration: int = 100):
        t = time.ticks_ms()
        log.info('Checking WiFi stability for {} ms'.format(duration))
        # Timeout ensures stable WiFi and forces minimum outage duration
        while wlan.isconnected() and time.ticks_diff(time.ticks_ms(), t) < duration:
            time.sleep_ms(1)
        return wlan.isconnected()
