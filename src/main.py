import gc
import logging
import time
import machine
import uasyncio as asyncio
from p1meter import P1Meter
import wifi
from mqttclient import MQTTClient2 # ensure_mqtt_connected, publish_one
from config import ROOT_TOPIC, RX_PIN_NR, TX_PIN_NR, RUN_SIM, CLIENT_ID

from utilities import cpu_temp, Feedback

if RUN_SIM:
    ROOT_TOPIC = CLIENT_ID      # avoid overwiting actual data
    from p1meter_sym import P1MeterSIM

# Logging
log = logging.getLogger('main')
fb = Feedback()

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
        log.debug( "freed: {0:,} - now free: {1:,}".format( after-before , after ).replace(',','.') ) # EU Style : use . as a thousands seperator
        glb_mqtt_client.publish_one(ROOT_TOPIC + b"/sensor/mem_free", str(after) )
        glb_mqtt_client.publish_one(ROOT_TOPIC + b"/sensor/cpu_temp", str(cpu_temp()) )
        glb_mqtt_client.publish_one(ROOT_TOPIC + b"/sensor/client_id", CLIENT_ID )
        await asyncio.sleep(interval)

async def update_leds():
    "set the leds to reflect the state of the main components"
    while 1:
        # wifi led
        if (wifi.wlan.status() == wifi.network.STAT_GOT_IP):
            fb.update(fb.L_NET, fb.GREEN)
        else:
            fb.update(fb.L_NET, fb.RED)

        #MQTT
        if glb_mqtt_client.healthy():
            fb.update(fb.L_MQTT, fb.GREEN)
        else:
            fb.update(fb.L_MQTT, fb.RED)

        await asyncio.sleep_ms(200)

async def trigger_all(interval:int=300):
    "trigger the sending of the complete next telegram every 5 minutes"
    while 1:
        await asyncio.sleep(interval)    
        glb_p1_meter.clearlast()

async def main(mq_client):
    # debug aid
    log.info("Set up main tasks")
    set_global_exception()  # Debug aid

    asyncio.create_task(update_leds())
    # connect to wifi and mqtt broker
    asyncio.create_task(wifi.ensure_connected())
    asyncio.create_task(mq_client.ensure_mqtt_connected())
    if RUN_SIM:
        # SIMULATION: simulate meter input on this machine
        sim = P1MeterSIM(glb_p1_meter.uart, mq_client,fb)
        asyncio.create_task(sim.sender(interval=10))

    # start receiver
    asyncio.create_task(glb_p1_meter.receive())

    asyncio.create_task(trigger_all())

    # run memory maintenance task
    asyncio.create_task(maintain_memory())
    while True:
        await asyncio.sleep(1)

###############################################################################
try:
    log.info('micropython p1 meter is starting...')

    glb_mqtt_client = MQTTClient2()
    glb_p1_meter = P1Meter(RX_PIN_NR,TX_PIN_NR,mq_client=glb_mqtt_client ,fb=fb)
    fb.clear()
    asyncio.run(main(glb_mqtt_client))
finally:
    # status 
    fb.clear(fb.RED)

    log.info("Clear async loop retained state")
    asyncio.new_event_loop()  # Clear retained state

# reboot after x seconds stopped when in production
if not RUN_SIM:
    log.warning('Rebooting in 15 seconds, Ctrl-C to abort')
    for n in range(3):
        fb.update(n,fb.PURPLE)
        time.sleep(15)
        fb.update(n,fb.BLUE)
    log.warning('Rebooting now...')
    machine.reset()
