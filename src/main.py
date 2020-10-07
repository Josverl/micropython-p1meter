import gc
import logging
import uasyncio as asyncio
from p1meter import P1Meter
import wifi
from mqttclient import MQTTClient2 # ensure_mqtt_connected, publish_one
from config import RX_PIN_NR, TX_PIN_NR, RUN_SIM
from utilities import cpu_temp

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

async def maintain_memory(interval :int=600 ):
    "run GC at a 10 minute interval"
    while 1:
        before = gc.mem_free()
        gc.collect()
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
        after = gc.mem_free()
        #todo: root topic
        log.debug( "freed: {0:,} - now free: {1:,}".format( after-before , after ).replace(',','.') ) # EU Style : use . as a thousands seperator
        glb_mqtt_client.publish_one("p1_meter/sensor/mem_free", str(after) )
        glb_mqtt_client.publish_one("p1_meter/sensor/cpu_temp", str(cpu_temp()) )
        await asyncio.sleep(interval)


async def main(mq_client):
    # debug aid
    log.info("Set up main tasks")
    set_global_exception()  # Debug aid

    # connect to wifi and mqtt broker
    asyncio.create_task(wifi.ensure_connected())
    asyncio.create_task(mq_client.ensure_mqtt_connected())
    if RUN_SIM:
        # SIMULATION: simulate meter input on this machine
        sim = P1MeterSIM(glb_p1_meter.uart, mq_client)
        asyncio.create_task(sim.sender(interval=1))

    # start receiver
    asyncio.create_task(glb_p1_meter.receive())
    # run memory maintenance task
    asyncio.create_task(maintain_memory())
    while True:
        await asyncio.sleep(1)

###############################################################################
try:
    log.info('micropython p1 meter is starting...')
    glb_mqtt_client = MQTTClient2()
    glb_p1_meter = P1Meter(RX_PIN_NR,TX_PIN_NR,mq_client=glb_mqtt_client )

    asyncio.run(main(glb_mqtt_client))
finally:
    log.info("Clear async loop retained state")
    asyncio.new_event_loop()  # Clear retained state


