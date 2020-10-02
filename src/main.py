
import p1meter
import p1meter_sym
import uasyncio as asyncio
import wifi

from machine import UART
uart = UART(1, rx=2, tx=5, baudrate=115200,  bits=8, parity=None, stop=1 , invert=UART.INV_RX | UART.INV_TX  )

run_sym = True


def set_global_exception():
    def handle_exception(loop, context):
        import sys
        sys.print_exception(context["exception"])
        sys.exit()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)

async def main():

    set_global_exception()  # Debug aid
    asyncio.create_task(wifi.ensure_connected())
        asyncio.create_task(p1meter_sym.sender(uart))
    asyncio.create_task(p1meter.receiver(uart))
    while True:
        await asyncio.sleep(1)

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()  # Clear retained state