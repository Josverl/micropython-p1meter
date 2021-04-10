import logging

import ujson as json #used for deepcopy of dict
import ure as re
import utime as time
from machine import UART, Pin
import uasyncio as asyncio
from utilities import  crc16, Feedback, seconds_between

from mqttclient import MQTTClient2
import config as cfg


# Logging
log = logging.getLogger('p1meter')
#set level no lower than ..... for this log only
#log.level = min(logging.DEBUG, logging._level) #pylint: disable=protected-access
VERBOSE = False

print(r"""
______  __   ___  ___     _            
| ___ \/  |  |  \/  |    | |           
| |_/ /`| |  | .  . | ___| |_ ___ _ __ 
|  __/  | |  | |\/| |/ _ \ __/ _ \ '__|
| |    _| |_ | |  | |  __/ ||  __/ |   
\_|    \___/ \_|  |_/\___|\__\___|_|     v 1.3.0
""")

if cfg.RUN_SPLITTER:
    print(r"""
     __  ___  _    _  ___  ___  ___  ___ 
    / _|| o \| |  | ||_ _||_ _|| __|| o \
    \_ \|  _/| |_ | | | |  | | | _| |   /
    |__/|_|  |___||_| |_|  |_| |___||_|\\
    """)

def dictcopy(d: dict):
    "returns a copy of a dict using copy though json"
    return json.loads(json.dumps(d))


# @timed_function
def replace_codes(readings: list)-> list:
    "replace the OBIS codes by their ROOT_TOPIC as defined in the codetable"
    for reading in readings:
        for code in cfg.codetable:
            if re.match(code[0], reading['meter']):
                reading['meter'] = re.sub(code[0], code[1], reading['meter'])

                if reading['unit'] and len(reading['unit']) > 0:
                    reading['meter'] += '_' + reading['unit']
                if VERBOSE:
                    log.debug("{} --> {}".format(code[0], reading['meter']))
                break
    return readings

class P1Meter():
    """
    P1 meter to take readings from a Dutch electricity meter and publish them on mqtt for consumption by homeassistant
    """
    cts: Pin
    dtr: Pin
    fb: Feedback
    uart: UART

    def __init__(self, mq_client: MQTTClient2, fb: Feedback):
        # init port for receiving 115200 Baud 8N1 using inverted polarity in RX/TX
        # UART 1 = Receive and TX if configured as Splitter
        self.uart = UART(1, rx=cfg.RX_PIN_NR, tx=cfg.TX_PIN_NR,
                         baudrate=115200, bits=8, parity=None,
                         stop=1, invert=UART.INV_RX | UART.INV_TX,
                         txbuf=2048, rxbuf=2048)                     # larger buffer for testing and stability
        log.info("setup to receive P1 meter data : {}".format(self.uart))
        self.last = []
        self.pending = {}
        self.last_time = time.localtime()
        self.message = ''
        self.telegrams_rx = 0
        self.telegrams_tx = 0
        self.telegrams_pub = 0
        self.telegrams_err = 0
        self.mqtt_client = mq_client
        self.fb = fb
        self.crc_received = ''
        # receive set CTS/RTS High
        self.cts = Pin(cfg.CTS_PIN_NR, Pin.OUT)
        self.cts.on()                 # Ask P1 meter to send data
        # In case the
        self.dtr = Pin(cfg.DTR_PIN_NR, Pin.IN, Pin.PULL_DOWN)


    def clearlast(self)-> None:
        "trigger sending the complete next telegram by forgetting the previous"
        if len(self.last) > 0:
            log.warning("trigger sending the complete next telegram by forgetting the previous")
            self.last = []
            self.fb.update(Feedback.LED_P1METER, Feedback.PURPLE)

    async def receive(self):
        "Receive telegrams from the p1 meter and send them once received"
        sreader = asyncio.StreamReader(self.uart)
        #start with an empty telegram, explicit to avoid references
        empty = {'header': '', 'data': [], 'footer': ''}
        tele = dictcopy(empty)
        log.info("listening on UART1 RX Pin:{} for P1 meter data".format(cfg.RX_PIN_NR))
        if cfg.RUN_SPLITTER:
            log.info("repeating on UART1 RX Pin:{} ".format(cfg.TX_PIN_NR))
        while True:
            line = await sreader.readline()         #pylint: disable= not-callable
            if VERBOSE:
                log.debug("raw: {}".format(line))
            if line:
                # to string
                try:
                    line = line.decode()
                except BaseException as error:      #pylint: disable= unused-variable
                    line = "--noise--"
                if VERBOSE:
                    log.debug("clean : {}".format(line))
                if line[0] == '/':
                    log.debug('header found')
                    self.fb.update(Feedback.LED_P1METER, Feedback.GREEN)
                    tele = dictcopy(empty)
                    self.message = line

                elif line[0] == '!':
                    log.debug('footer found')
                    tele['footer'] = line
                    self.message += "!"
                    if len(line) > 5:
                        self.crc_received = line[1:5]
                    # self.message += line
                    # Process the received telegram
                    await self.process(tele)
                    # start with a blank slate
                    self.message = ''
                    self.crc_received = ''

                elif line != "--noise--":
                    tele['data'].append(line)
                    # add to message
                    self.message += line

    @property
    def crc(self) -> str:
        "Compute the crc of self.message"
        buf = self.message.encode()
        # TMI log.debug( "buf: {}".format(buf))
        return "{0:04X}".format(crc16(buf))


    def crc_ok(self, tele: dict = None)-> bool:
        "run CRC-16 check on the received telegram"
        if not tele or not self.message:
            return False
        try:
            # cache crc to avid wasting time
            crc = self.crc
            log.debug("RX computed CRC {0}".format(crc))
            if crc in tele['footer']:
                return True
            else:
                log.warning("CRC Failed, computed: {0} != received {1}".format(str(crc), str(tele['footer'][1:5])))
                return False
        except (OSError, TypeError) as e:
            log.error("Error during CRC check: {}".format(e))
            return False

    def parsereadings(self, newdata):
        "split the received data into readings(meter, reading, unit)"
        readings = []
        for line in newdata:
            out = re.match('(.*?)\((.*)\)', line)           #pylint: disable=anomalous-backslash-in-string
            if out:
                lineinfo = {'meter': out.group(1), 'reading':None, 'unit': None}

                reading = out.group(2).split('*')
                if len(reading) == 2:
                    lineinfo['reading'] = reading[0]
                    lineinfo['unit'] = reading[1]
                else:
                    lineinfo['reading'] = reading[0]
                # a few meters have compound content, that remain seperated by `)(`
                # split and use  only the last section (ie gas meter reading)
                lineinfo['reading'] = lineinfo['reading'].split(')(')[-1]
                if VERBOSE:
                    log.debug(lineinfo)
                readings.append(lineinfo)
        return readings

    async def process(self, tele: dict):
        # check CRC
        if not self.crc_ok(tele):
            self.telegrams_err += 1
            self.fb.update(Feedback.LED_P1METER, Feedback.RED)
            return
        else:
            self.fb.update(Feedback.LED_P1METER, Feedback.GREEN)
            self.telegrams_rx += 1

        # Send a copy of the received message (self.message)
        if cfg.RUN_SPLITTER:
            await self.send(self.message)
            self.telegrams_tx += 1

        # what has changed since last time  ?
        newdata = set(tele['data']) - set(self.last)
        readings = self.parsereadings(newdata)

        # replace codes for ROOT_TOPICs
        readings = replace_codes(readings)
        log.debug("readings: {}".format(readings))

        # move list into dictionary
        for reading in readings:
            self.pending[reading['meter']] = reading

        delta_sec = seconds_between(self.last_time, time.localtime())
        if  delta_sec < cfg.INTERVAL_MIN and self.telegrams_pub > 0:
            ## do not send too often, remember any changes to send later
            log.info('suppress send')
            log.debug('pending : {}'.format(self.pending.keys))
            # turn off
            self.fb.update(Feedback.LED_P1METER, Feedback.BLACK)
        else:
            # send this data and any unsent information
            self.fb.update(Feedback.LED_P1METER, Feedback.GREEN)
            readings = list(self.pending.values())
            if await self.mqtt_client.publish_readings(readings):
                # only safe last if mqtt publish was ok
                self.telegrams_pub += 1
                self.last = tele['data'].copy()
                self.pending = {}
                self.last_time = time.localtime()
            else:
                self.fb.update(Feedback.LED_MQTT, Feedback.YELLOW)
            # Turn off

    async def send(self, telegram: str):
        """
        Sends/repeats telegram, with added CRC16
        """

        log.info('Copy telegram')
        if not self.dtr.value():
            log.warning("Splitter DTR is Low, will not send P1 telegram data")
        else:
            swriter = asyncio.StreamWriter(self.uart, {})

            self.fb.update(Feedback.LED_P1METER, Feedback.BLUE)
            if VERBOSE:
                log.debug(b'TX telegram message: ----->')
                log.debug(telegram)
                log.debug(b'-----')
            swriter.write(telegram + self.crc_received  + '\r\n')
            await swriter.drain()       # pylint: disable= not-callable
            await asyncio.sleep_ms(1)


