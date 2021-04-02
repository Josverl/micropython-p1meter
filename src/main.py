
#import ugc as gc
import gc
import logging
import time
import uasyncio as asyncio
from p1meter import P1Meter
import wifi
from mqttclient import MQTTClient2
from config import ROOT_TOPIC, RUN_SIM, NETWORK_ID, RUN_SPLITTER
from config import INTERVAL_MEM, INTERVAL_ALL

from utilities import cpu_temp, Feedback, reboot, getntptime

# Splitter and Simulator cannot be run at the same time as they use the same UART
if RUN_SIM and not RUN_SPLITTER:
    from p1meter_sym import P1MeterSIM

# Logging
log = logging.getLogger('main')
fb = Feedback()

def set_global_exception():
    def handle_exception(loop, context):            #pylint: disable=unused-argument
        import sys                                  #pylint: disable=import-outside-toplevel
        sys.print_exception(context["exception"])   #pylint: disable=no-member
        sys.exit()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)

async def maintain_memory(interval: int = INTERVAL_MEM):
    "run GC at a 10 minute interval"
    while 1:
        before = gc.mem_free()                              #pylint: disable=no-member
        gc.collect()
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())   #pylint: disable=no-member
        after = gc.mem_free()                               #pylint: disable=no-member
        log.debug("freed: {0:,} - now free: {1:,}".format(after-before, after).replace(',', '.')) # EU Style : use . as a thousands seperator
        glb_mqtt_client.publish_one(ROOT_TOPIC + b"/sensor/mem_free", str(after))
        glb_mqtt_client.publish_one(ROOT_TOPIC + b"/sensor/cpu_temp", str(cpu_temp()))
        glb_mqtt_client.publish_one(ROOT_TOPIC + b"/sensor/client_id", NETWORK_ID)
        glb_mqtt_client.publish_one(ROOT_TOPIC + b"/sensor/telegrams_rx", glb_p1_meter.messages_rx)
        glb_mqtt_client.publish_one(ROOT_TOPIC + b"/sensor/telegrams_tx", glb_p1_meter.messages_tx)
        glb_mqtt_client.publish_one(ROOT_TOPIC + b"/sensor/telegrams_pub", glb_p1_meter.messages_pub)
        glb_mqtt_client.publish_one(ROOT_TOPIC + b"/sensor/telegrams_err", glb_p1_meter.messages_err)
        await asyncio.sleep(interval)

async def update_leds():
    "set the leds to reflect the state of the main components"
    while 1:
        # wifi led
        if wifi.wlan.status() == wifi.network.STAT_GOT_IP:
            fb.update(fb.LED_NETWORK, fb.GREEN)
        else:
            fb.update(fb.LED_NETWORK, fb.RED)

        #MQTT
        if glb_mqtt_client.healthy():
            fb.update(fb.LED_MQTT, fb.GREEN)
        else:
            fb.update(fb.LED_MQTT, fb.RED)

        await asyncio.sleep(1)

async def trigger_all(interval: int = INTERVAL_ALL):
    "trigger the sending of the complete next telegram every 5 minutes"
    while 1:
        await asyncio.sleep(interval)
        glb_p1_meter.clearlast()

async def ntp_sync(t=600):
    "sync time from ntp periodically"
    while True:
        try:
            getntptime()
            log.info("fresh time: {2}-{1}-{0} {3}:{4}:{5}".format(*time.localtime()))
        except OSError:
            # OSError: [Errno 110] ETIMEDOUT
            pass
        await asyncio.sleep(t)

async def main(mq_client):
    # debug aid
    log.info("Set up main tasks")
    set_global_exception()  # Debug aid

    asyncio.create_task(update_leds())
    # connect to wifi and mqtt broker
    asyncio.create_task(wifi.ensure_connected())
    asyncio.create_task(ntp_sync())
    asyncio.create_task(mq_client.ensure_mqtt_connected())
    if RUN_SIM and not RUN_SPLITTER:
        # SIMULATION: simulate meter input on this machine
        sim = P1MeterSIM(glb_p1_meter.uart, mq_client, fb)
        asyncio.create_task(sim.sender(interval=5))

    # start receiver
    asyncio.create_task(glb_p1_meter.receive())

    asyncio.create_task(trigger_all())

    # run memory maintenance task
    asyncio.create_task(maintain_memory())
    while True:
        await asyncio.sleep(1)

###############################################################################


glb_mqtt_client = MQTTClient2()
glb_p1_meter = P1Meter(mq_client=glb_mqtt_client, fb=fb)

def run():
    try:
        log.info('micropython p1 meter is starting...')
        fb.clear()
        asyncio.run(main(glb_mqtt_client))
    finally:
        # status
        fb.clear(fb.RED)

        log.info("Clear async loop retained state")
        asyncio.new_event_loop()  # Clear retained state

        reboot(10)


run()
