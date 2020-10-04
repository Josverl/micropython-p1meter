import gc
#import machine
from machine import UART
import uasyncio as asyncio
import logging
from p1meter import P1Meter
import wifi
from mqttclient import ensure_mqtt_connected
from config import RX_PIN_NR, TX_PIN_NR


# run the simulator for testing
RUN_SIM = True

if RUN_SIM: 
    from p1meter_sym import P1MeterSIM


# Logging
log = logging.getLogger('main')

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
p1_meter = None
async def main():
    global p1_meter
    log.info("Set up main tasks")
    p1_meter = P1Meter(RX_PIN_NR,TX_PIN_NR)
    
    set_global_exception()  # Debug aid
    asyncio.create_task(maintain_memory())
    asyncio.create_task(wifi.ensure_connected())
    asyncio.create_task(ensure_mqtt_connected())
    if RUN_SIM:
        # SIMULATION: simulate meter input on this machine
        sim = P1MeterSIM(p1_meter.uart)
        asyncio.create_task(sim.sender())
    asyncio.create_task(p1_meter.receive())
    while True:
        await asyncio.sleep(1)

print('python p1 meter is starting up')
try:
    asyncio.run(main())
finally:
    log.info("Clear async loop retained state")
    asyncio.new_event_loop()  # Clear retained state