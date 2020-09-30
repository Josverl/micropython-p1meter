import uasyncio as asyncio

#####################################################
# test rig 
#####################################################

telegram = """/XMX5LGBBFG1012650850
1-3:0.2.8(42)
0-0:1.0.0(200909224846S)
0-0:96.1.1(4530303331303033373235323935313136)
1-0:1.8.1(009248.534*kWh)
1-0:1.8.2(010048.316*kWh)
1-0:2.8.1(000136.408*kWh)
1-0:2.8.2(000330.023*kWh)
0-0:96.14.0(0002)
1-0:1.7.0(00.317*kW)
1-0:2.7.0(00.000*kW)
0-0:96.7.21(00001)
0-0:96.7.9(00000)
1-0:99.97.0(0)(0-0:96.7.19)
1-0:32.32.0(00000)
1-0:32.36.0(00000)
0-0:96.13.1()
0-0:96.13.0()
0-1:24.1.0(003)
0-1:96.1.0(4730303332353631323831383834363136)
0-1:24.2.1(200909220000S)(05907.828*m3)
!A7B3
"""
async def sender(uart_tx :UART):
    """
    Simulates data being sent from the t1 port to aud in debugging
    this requires pin 2rx)  and 5(tx) to be connected
    """
    swriter = asyncio.StreamWriter(uart_tx, {})
    while True:
        swriter.write(telegram)
        await swriter.drain()
        await asyncio.sleep(1)

