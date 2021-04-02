import logging
import uasyncio as asyncio
import network
import utime as time
import webrepl
import config as cfg
import uftpd
from config import webrepl as config_webrepl
from utilities import getntptime

wlan = network.WLAN(network.STA_IF)
wlan_stable = False

#wait until wifi is connected
uftpd.stop()

# Logging
log = logging.getLogger(__name__)

async def ensure_connected():
    global wlan_stable
    # check state and sync time on first call.
    if check_stable():
        log_ifconfig()
        getntptime()

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
    if not wlan.active():
        wlan.active(True)
        wlan.config(dhcp_hostname=cfg.NETWORK_ID)
    if not wlan.isconnected():
        log.info("Activating Wlan {0}".format(cfg.homenet['SSID']))
        wlan.connect(cfg.homenet['SSID'], cfg.homenet['password'])

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
    else:
        log.debug("Wlan already active")

    await check_stable(duration=100)
    if wlan_stable:
        log_ifconfig()
    else:
        cause = 'reason unknown'
        if wlan.status() == network.STAT_WRONG_PASSWORD:
            cause = 'wrong password'
        elif wlan.status() == network.STAT_NO_AP_FOUND:
            cause = 'SSID not found'
        elif wlan.status() == network.STAT_ASSOC_FAIL:
            cause = 'assoc fail'
        elif wlan.status() == network.STAT_CONNECTING:
            cause = 'cannot find SSID'
        #deactivate ( to re-activate later)
        wlan.active(False)
        wlan_stable = False
        log.error("Unable to connect to Wlan {}; {}".format(cfg.homenet['SSID'], cause))


def log_ifconfig():
    # prettyprint the interface's IP/netmask/gw/DNS addresses
    config = wlan.ifconfig()
    log.info("Wifi IP:{0}, Network mask:{1}, Router:{2}, DNS: {3}".format(*config))


async def check_stable(duration: int = 2000)->bool:
    global wlan_stable
    t = time.ticks_ms()
    log.info('Checking WiFi stability for {} ms'.format(duration))
    # Timeout ensures stable WiFi and forces minimum outage duration
    while wlan.isconnected() and time.ticks_diff(time.ticks_ms(), t) < duration:
        await asyncio.sleep_ms(10)
    # connected and IP
    wlan_stable = wlan.isconnected() and wlan.status() == network.STAT_GOT_IP
    uftpd.restart()
    log.info('ftp server restarted')
    try:
        if config_webrepl["active"]:
            log.info('start webrepl')
            webrepl.start(password=config_webrepl["password"])
    except ValueError as e:
        log.warning('webrepl password > 8 characters{}'.format(e))
    except OSError as e:
        log.warning('Unable to start webrepl{}'.format(e))

    return wlan_stable

