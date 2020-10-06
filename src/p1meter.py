import logging
import ujson as json #used for deepcopy op dict
import ure as re
from machine import UART
import uasyncio as asyncio
from timed_func import timed_function

from mqttclient import publish_readings
from utilities import crc16
from config import codetable

# Logging
log = logging.getLogger('p1meter')

def dictcopy(d : dict):
    "returns a copy of a dict using copy though json"
    return json.loads(json.dumps(d))


# @timed_function
def replace_codes(readings :list)-> list :
    "replace the codes by their topic as defined in the codetable"
    for reading in readings:
        for code in codetable:
            if re.match(code[0],reading['meter']):
                reading['meter'] = re.sub(code[0], code[1], reading['meter'])
                log.debug("{} --> {}".format(code[0],reading['meter'] ))
                break
    return readings

class P1Meter():
    """
    P1 meter to take readings from a Dutch electricity meter and publish them on mqtt for consumption by homeassistant
    """
    def __init__(self, rx :int ,tx :int):
        # init port for recieving 115200 Baud 8N1 using inverted polarity in RX/TX
        self.uart = UART(   1, rx=rx, tx=tx,
                            baudrate=115200,  bits=8, parity=None,
                            stop=1 , invert=UART.INV_RX | UART.INV_TX,
                            txbuf=2048, rxbuf=2048)                     # larger buffer for testing and stability
        self.last = []
        self.message = b''

    async def receive(self):
        "Receive telegrams from the p1 meter and send them once recieved"
        sreader = asyncio.StreamReader(self.uart)
        #start with an empty telegram, explicit to avoid references
        empty = {'header': '', 'data': [],  'footer': ''}
        tele = dictcopy(empty)
        while True:
            line = await sreader.readline()
            log.debug("raw: {}".format(line))
            if line:
                # to string
                try:
                    line = line.decode()
                except BaseException as error:  # pylint: disable=unused-variable
                    line = "--noise--"
                # log.debug("clean".format(line))
                if line[0] == '/':
                    log.debug('header found')
                    tele = dictcopy(empty)
                    self.message=line

                elif line[0] == '!':
                    log.debug('footer found')
                    tele['footer'] = line
                    self.message+="!"
                    await self.process(tele)
                    self.message=b''

                elif line != "--noise--":
                    tele['data'].append(line)
                    # add to message
                    self.message+=line

# TODO: HIERNA SOMS EEN FOUT BY FOUTE CRC ? GEKLOIO MET DRAADJE
# DEBUG:p1meter:message: b'1-3:0.2.8(42)\n# 1-0:1.7.0(35.277*kW)\n# 1-0:2.7.0(62.976*kW)\n1-0:1.8.1(009248.534*kWh)\n0-1:24.2.1(200909220000S)(05907.828*m3)\n!'
# Traceback (most recent call last):
#   File "uasyncio/core.py", line 1, in run_until_complete
#   File "p1meter.py", line 52, in receive
#   File "p1meter.py", line 65, in process
# TypeError: can't convert 'str' object to bytes implicitly
    def crc_ok(self, tele:dict)-> bool:
        #run the CRC
        try:
            buf = bytearray(self.message.replace('\n','\r\n'))
            log.debug( "buf: {}".format(buf))
            crc_computed = "{0:0X}".format(crc16(buf))
            log.debug("RX computed CRC {0}".format(crc_computed))
            if tele['footer'] == "!{0}\n".format(crc_computed):
                return True
            else:
                log.warning("CRC Failed, computed: {0} != received {1}!!".format(crc_computed, tele['footer'][1:5]))
                return False
        except OSError as e:
            log.error("Error during CRC check: {}".format(e))
            return False

    async def process(self, tele:dict):
        # check CRC
        if not self.crc_ok(tele) :
            return
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
        # replace codes for topics
        reading = replace_codes(readings)

        log.debug("readings: {}".format(readings))



        # todo: add timeout ?
        if await publish_readings(readings):
            # only safe last of publish was succesfull
            self.last = tele['data'].copy()

