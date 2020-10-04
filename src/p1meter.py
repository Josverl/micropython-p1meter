import binascii
import uasyncio as asyncio
from machine import UART
import ure as re
import logging
import ujson as json #used for deepcopy op dict 
from mqttclient import publish_readings
from utilities import crc16

# Logging
log = logging.getLogger('p1meter')

def dictcopy(d : dict):
    "returns a copy of a dict using copy though json"
    return json.loads(json.dumps(d))

class P1Meter():
    """
    P1 meter to take readings from a Dutch electricity meter and publish them on mqtt for consumption by homeassistant
    """
    def __init__(self, rx :int ,tx :int):
        #init port for recieving 115200 Baud 8N1 using inverted polarity in RX/TX 
        self.uart = UART(1, rx=rx, tx=tx, baudrate=115200,  bits=8, parity=None, stop=1 , invert=UART.INV_RX | UART.INV_TX)
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

    async def process(self, tele:dict):
        # todo: -check CRC 

        #run the CRC
        log.debug( "message: {}".format(self.message))  
# TODO: HIERNA SOMS EEN FOUT BY FOUTE CRC ? GEKLOIO MET DRAADJE
# DEBUG:p1meter:message: b'1-3:0.2.8(42)\n# 1-0:1.7.0(35.277*kW)\n# 1-0:2.7.0(62.976*kW)\n1-0:1.8.1(009248.534*kWh)\n0-1:24.2.1(200909220000S)(05907.828*m3)\n!'
# Traceback (most recent call last):
#   File "uasyncio/core.py", line 1, in run_until_complete
#   File "p1meter.py", line 52, in receive
#   File "p1meter.py", line 65, in process
# TypeError: can't convert 'str' object to bytes implicitly
        buf = bytearray(self.message.replace('\n','\r\n'))
        log.debug( "buf: {}".format(buf))

        crc_computed = crc16(buf) 

        log.debug("RX computed CRC {0:X}".format(crc_computed))
        if tele['footer'] == "!{0:X}\n".format(crc_computed):
            log.info("CRC OK !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
   
        # # what has changed 
        # newdata= set(tele['data']) - set(self.last)

        # self.last = tele['data'].copy()

        # readings = []
        # for line in newdata:
        #     # split data into readings
        #     out = re.match('(.*?)\((.*)\)', line)
        #     if out:
        #         lineinfo = {'meter': out.group(1), 'reading':None, 'unit': None}

        #         reading = out.group(2).split('*')
        #         if len(reading) == 2:
        #             lineinfo['reading'] = reading[0]
        #             lineinfo['unit'] = reading[1]
        #         else:
        #             lineinfo['reading'] = reading[0]
        #         log.debug(lineinfo)
        #         readings.append(lineinfo )
        
        # print("readings:" , readings)

        # await publish_readings(readings)

