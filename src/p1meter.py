import binascii
import uasyncio as asyncio
from machine import UART
import ure as re
import logging
from mqttclient import publish_readings

# Logging
log = logging.getLogger('p1meter')

#####################################################
async def receiver(uart_rx: UART):
    sreader = asyncio.StreamReader(uart_rx)
    #start with an empty telegram, explicit to avoid references 
    # possible solution : copy.deepcopy(dict1) not on micropython
    # copy by hydrate from json ?
    # create class -- TMO 

    tele = {'header': '', 'data': [], 'readings': [],  'footer': ''}
    while True:
        line = await sreader.readline()
        log.debug("raw: {}".format(line))
        if line:
            # to string and remove last character : \n
            try:
                line = line.decode()
                line = line[:-1]
            except BaseException as error:  # pylint: disable=unused-variable
                line = "--noise--"
            # log.debug("clean".format(line))
            if line[0] == '/':
                log.debug('header found')
                tele = {'header': '', 'data': [], 'readings': [],  'footer': ''}

            elif line[0] == '!':
                log.debug('footer found')
                tele['footer'] = line
                # todo: -check CRC 
                await publish_readings(tele)
                # publish_readings(tele)

            elif line != "--noise--":
                tele['data'].append(line)
                # split data into readings
                out = re.match('(.*?)\((.*)\)', line)
                if out:
                    lineinfo = {'meter': out.group(1), 'reading':None, 'unit': None}

                    reading = out.group(2).split('*')
                    if len(reading) == 2:
                        lineinfo['reading'] = reading[0]
                        lineinfo['unit'] = reading[1]
                    else:
                        lineinfo['reading'] = reading[0]
                    log.debug(lineinfo)
                    tele['readings'].append(lineinfo )
    



