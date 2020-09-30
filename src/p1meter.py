import uasyncio as asyncio
from machine import UART


#####################################################
#
#####################################################

async def receiver(uart_rx:UART):
    sreader = asyncio.StreamReader(uart_rx)
    while True:
        res = await sreader.readline()
        print('Recieved', res)

