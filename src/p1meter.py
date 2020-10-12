import logging
import ujson as json #used for deepcopy op dict
import ure as re
from machine import UART
import uasyncio as asyncio
from utilities import  crc16, Feedback

from mqttclient import MQTTClient2
from config import codetable

# Logging
log = logging.getLogger('p1meter')
#set level no lower than ..... for this log only
log.level = max( logging.DEBUG , logging._level) #pylint: disable=protected-access
VERBOSE = False

print(r"""
______  __   ___  ___     _            
| ___ \/  |  |  \/  |    | |           
| |_/ /`| |  | .  . | ___| |_ ___ _ __ 
|  __/  | |  | |\/| |/ _ \ __/ _ \ '__|
| |    _| |_ | |  | |  __/ ||  __/ |   
\_|    \___/ \_|  |_/\___|\__\___|_|     v 0.9.5
""")

def dictcopy(d : dict):
    "returns a copy of a dict using copy though json"
    return json.loads(json.dumps(d))


# @timed_function
def replace_codes(readings :list)-> list :
    "replace the OBIS codes by their ROOT_TOPIC as defined in the codetable"
    for reading in readings:
        for code in codetable:
            if re.match(code[0],reading['meter']):
                reading['meter'] = re.sub(code[0], code[1], reading['meter'])

                if reading['unit'] and len(reading['unit']) > 0:
                    reading['meter'] += '_' + reading['unit']

                log.debug("{} --> {}".format(code[0],reading['meter'] ))
                break
    return readings

class P1Meter():
    """
    P1 meter to take readings from a Dutch electricity meter and publish them on mqtt for consumption by homeassistant
    """
    def __init__(self, rx :int ,tx :int,mq_client :MQTTClient2, fb:Feedback):
        # init port for receiving 115200 Baud 8N1 using inverted polarity in RX/TX

        self.uart = UART(   1, rx=rx, tx=tx,
                            baudrate=115200,  bits=8, parity=None,
                            stop=1 , invert=UART.INV_RX | UART.INV_TX,
                            txbuf=2048, rxbuf=2048)                     # larger buffer for testing and stability
        log.info("setup to receive P1 meter data : {}".format(self.uart))
        self.last = []
        self.message = ''
        self.mqtt_client = mq_client
        self.fb=fb

    def clearlast(self)-> None:
        "trigger sending the complete next telegram by forgetting the previous"
        log.warning("trigger sending the complete next telegram by forgetting the previous")
        self.last = []
        self.fb.update(Feedback.L_P1, Feedback.PURPLE)

    async def receive(self):
        "Receive telegrams from the p1 meter and send them once received"
        sreader = asyncio.StreamReader(self.uart)
        #start with an empty telegram, explicit to avoid references
        empty = {'header': '', 'data': [],  'footer': ''}
        tele = dictcopy(empty)
        log.info("listening on UART for P1 meter data")
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
                    tele = dictcopy(empty)
                    self.message=line

                elif line[0] == '!':
                    log.debug('footer found')
                    tele['footer'] = line
                    self.message+="!"
                    await self.process(tele)
                    self.message=''

                elif line != "--noise--":
                    tele['data'].append(line)
                    # add to message
                    self.message+=line

    def crc_ok(self, tele:dict = None)-> bool:
        "run CRC-16 check on the received telegram"
        # todo: just pass the expected CRC16 rather than the entire telegram
        if not tele or not self.message:
            return False
        try:
            # buf = self.message.replace('\n','\r\n').encode()
            buf = self.message.encode()
            # TMI log.debug( "buf: {}".format(buf))
            crc_computed = "{0:04X}".format(crc16(buf))
            log.debug("RX computed CRC {0}".format(crc_computed))
            if crc_computed in tele['footer']:
                return True
            else:
                log.warning("CRC Failed, computed: {0} != received {1}!!".format(str(crc_computed), str(tele['footer'][1:5])))
                return False
        except (OSError, TypeError) as e:
            log.error("Error during CRC check: {}".format(e))
            return False

    async def process(self, tele:dict):
        # check CRC
        if not self.crc_ok( tele, ) :
            self.fb.update(Feedback.L_P1, Feedback.RED)
            return
        self.fb.update(Feedback.L_P1, Feedback.BLUE)
 
        # what has changed since last time ?
        newdata= set(tele['data']) - set(self.last)

        readings = []
        for line in newdata:
            # split data into readings
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
                lineinfo['reading']=lineinfo['reading'].split(')(')[-1]

                log.debug(lineinfo)
                readings.append(lineinfo )
        # replace codes for ROOT_TOPICs
        reading = replace_codes(readings)

        log.debug("readings: {}".format(readings))

        # todo: add timeout ?
        if await self.mqtt_client.publish_readings(readings):
            # only safe last if mqtt publish was ok
            self.last = tele['data'].copy()
            self.fb.update(Feedback.L_P1, Feedback.GREEN)
        else:
            self.fb.update(Feedback.L_P1, Feedback.YELLOW)

