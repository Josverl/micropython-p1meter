import gc
#import machine
from machine import UART
import uasyncio as asyncio
import logging

import p1meter
import p1meter_sym
import wifi
from mqttclient import ensure_mqtt_connected

from config import RX_PIN_NR, TX_PIN_NR


# Logging
log = logging.getLogger('main')

#init port for recieving 115200 Baud 8N1 using inverted polarity in RX/TX 
uart = UART(1, rx=RX_PIN_NR, tx=TX_PIN_NR, baudrate=115200,  bits=8, parity=None, stop=1 , invert=UART.INV_RX | UART.INV_TX  )

def set_global_exception():
    def handle_exception(loop, context):
        import sys
        sys.print_exception(context["exception"])
        sys.exit()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)

async def maintain_memory(interval=600):
    "run GC at a 10 minute interval"
    while 1: 
        await asyncio.sleep(interval)
        gc.collect()
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

async def main():
    log.info("Set up main tasks")
    set_global_exception()  # Debug aid
    asyncio.create_task(maintain_memory())
    asyncio.create_task(wifi.ensure_connected())
    asyncio.create_task(ensure_mqtt_connected())
    if RUN_SIM:
        # SIMULATION: simulate meter input on this machine
        asyncio.create_task(p1meter_sym.sender(uart))
    asyncio.create_task(p1meter.receiver(uart))
    while True:
        await asyncio.sleep(1)

print('python p1 meter is starting up')
try:
    asyncio.run(main())
finally:
    log.info("Clear async loop retained state")
    asyncio.new_event_loop()  # Clear retained state