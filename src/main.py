import gc
import logging
import uasyncio as asyncio
from p1meter import P1Meter
import wifi
from mqttclient import ensure_mqtt_connected, publish_one
from config import RX_PIN_NR, TX_PIN_NR


# run the simulator for testing
RUN_SIM = True

if RUN_SIM:
    from p1meter_sym import P1MeterSIM


# Logging
log = logging.getLogger('main')

def set_global_exception():
    def handle_exception(loop, context):    # pylint: disable=unused-argument
        import sys                          # pylint: disable=import-outside-toplevel
        sys.print_exception(context["exception"])
        sys.exit()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)

async def maintain_memory(interval=600):
    "run GC at a 10 minute interval"
    while 1:
        before = gc.mem_free()
        gc.collect()
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
        after = gc.mem_free()
        publish_one("p1_meter/sensor/mem_free", str(after) )
        log.debug( "freed: {0:,} - now free: {1:,}".format( before-after , after ).replace(',','.') ) # EU Style : use . as a thousands seperator -  
        await asyncio.sleep(interval)


p1_meter = None             #Debug aid
async def main():
    global p1_meter         #debug aid
    log.info("Set up main tasks")
    p1_meter = P1Meter(RX_PIN_NR,TX_PIN_NR)

    set_global_exception()  # Debug aid
    asyncio.create_task(maintain_memory())
    asyncio.create_task(wifi.ensure_connected())
    asyncio.create_task(ensure_mqtt_connected())
    if RUN_SIM:
        # SIMULATION: simulate meter input on this machine
        sim = P1MeterSIM(p1_meter.uart)
        asyncio.create_task(sim.sender(interval=1))
    asyncio.create_task(p1_meter.receive())
    while True:
        await asyncio.sleep(1)

print('python p1 meter is starting up')
try:
    asyncio.run(main())
finally:
    log.info("Clear async loop retained state")
    asyncio.new_event_loop()  # Clear retained state
