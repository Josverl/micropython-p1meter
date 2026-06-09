import gc
import logging
import time
import uasyncio as asyncio
from p1meter import P1Meter
import wifi
from mqttclient import MQTTClient2
import config as cfg
from utilities import cpu_temp, Feedback, reboot, getntptime

if cfg.RUN_SIM and not cfg.RUN_SPLITTER:
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

async def maintain_memory(mq_client, p1_meter, interval: int = cfg.INTERVAL_MEM):
    "run GC at a ~10 minute interval and publish housekeeping metrics"
    while 1:
        before = gc.mem_free()                              #pylint: disable=no-member
        gc.collect()
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())   #pylint: disable=no-member
        after = gc.mem_free()                               #pylint: disable=no-member
        log.debug("freed: {0:,} - now free: {1:,}".format(after - before, after).replace(',', '.'))
        mq_client.publish_one(cfg.ROOT_TOPIC + b"/sensor/mem_free", str(after))
        mq_client.publish_one(cfg.ROOT_TOPIC + b"/sensor/cpu_temp", str(cpu_temp()))
        mq_client.publish_one(cfg.ROOT_TOPIC + b"/sensor/client_id", cfg.HOST_NAME)
        mq_client.publish_one(cfg.ROOT_TOPIC + b"/sensor/telegrams_rx", str(p1_meter.telegrams_rx))
        mq_client.publish_one(cfg.ROOT_TOPIC + b"/sensor/telegrams_tx", str(p1_meter.telegrams_tx))
        mq_client.publish_one(cfg.ROOT_TOPIC + b"/sensor/telegrams_pub", str(p1_meter.telegrams_pub))
        mq_client.publish_one(cfg.ROOT_TOPIC + b"/sensor/telegrams_err", str(p1_meter.telegrams_err))
        await asyncio.sleep(interval)

async def update_leds(mq_client):
    "set the leds to reflect the state of the main components"
    while 1:
        if wifi.wlan.status() == wifi.network.STAT_GOT_IP:
            fb.update(fb.LED_NETWORK, fb.GREEN)
        else:
            fb.update(fb.LED_NETWORK, fb.RED)

        if mq_client.healthy():
            fb.update(fb.LED_MQTT, fb.GREEN)
        else:
            fb.update(fb.LED_MQTT, fb.RED)

        await asyncio.sleep(1)

async def trigger_all(p1_meter, interval: int = cfg.INTERVAL_ALL):
    "trigger the sending of the complete next telegram every INTERVAL_ALL seconds"
    while 1:
        await asyncio.sleep(interval)
        p1_meter.clearlast()

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

async def main(mq_client, p1_meter):
    log.info("Set up main tasks")
    set_global_exception()

    asyncio.create_task(update_leds(mq_client))
    asyncio.create_task(wifi.ensure_connected())
    asyncio.create_task(ntp_sync())
    asyncio.create_task(mq_client.ensure_mqtt_connected())
    if cfg.RUN_SIM and not cfg.RUN_SPLITTER:
        sim = P1MeterSIM(p1_meter.uart, mq_client, fb)
        asyncio.create_task(sim.sender())

    asyncio.create_task(p1_meter.receive())
    asyncio.create_task(trigger_all(p1_meter))
    asyncio.create_task(maintain_memory(mq_client, p1_meter))

    while True:
        await asyncio.sleep(1)

###############################################################################

def run():
    mq_client = MQTTClient2()
    p1_meter = P1Meter(mq_client=mq_client, fb=fb)
    try:
        log.info('micropython p1 meter is starting...')
        fb.clear()
        asyncio.run(main(mq_client, p1_meter))
    finally:
        fb.clear(fb.RED)
        log.info("Clear async loop retained state")
        asyncio.new_event_loop()
        reboot(10)


run()
