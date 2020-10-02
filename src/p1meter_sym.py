import uasyncio as asyncio
import random

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
1-0:1.7.0({1:06.3f}*kW)
1-0:2.7.0({2:06.3f}*kW)
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


# telegram = """/XMX5LGBBFG1012650850
# 1-3:0.2.8(42)                                         Version information for P1 output
# 0-0:1.0.0(200909224846S)                              Date-time stamp of the P1 message
# 0-0:96.1.1(4530303331303033373235323935313136)        Equipment identifier (device 0) 
# 1-0:1.8.1(009248.534*kWh)                             Meter Reading electricity delivered to client (Tariff 1) in 0,001 kWh
# 1-0:1.8.2(010048.316*kWh)                             Meter Reading electricity delivered to client (Tariff 2) in 0,001 kWh
# 1-0:2.8.1(000136.408*kWh)                             Meter Reading electricity delivered by client (Tariff 1) in 0,001 kWh
# 1-0:2.8.2(000330.023*kWh)                             Meter Reading electricity delivered by client (Tariff 2) in 0,001 kWh
# 0-0:96.14.0(0002)                                     Tariff indicator electricity. ( 1 / 2) 
# 1-0:1.7.0(00.317*kW)                                  Actual electricity power delivered (+P) in 1 Watt resolution
# 1-0:2.7.0(00.000*kW)                                  Actual electricity power received (-P) in 1 Watt resolution
# 0-0:96.7.21(00001)                                    ~~~ Number of power failures in any phase (missing .255)
# 0-0:96.7.9(00000)                                     ~~~ Number of long power failures in any phase (missing .255)
# 1-0:99.97.0(0)(0-0:96.7.19)                           ~~~ Power Failure Event Log (long power failures)
# 1-0:32.32.0(00000)
# 1-0:32.36.0(00000)
# 0-0:96.13.1()                                         Text message
# 0-0:96.13.0()                                         Text message
# 0-1:24.1.0(003)                                       Device-Type ( device 1 = 003)  (assumed gas meter) 
# 0-1:96.1.0(4730303332353631323831383834363136)        Equipment identifier (device 1) 
# 0-1:24.2.1(200909220000S)(05907.828*m3)               0-[1..4] :24.2.1 Last 5-minute value (temperature converted), gas delivered to client in m3, including decimal values and capture time
# !A7B3                                                 
# """

async def sender(uart_tx :UART):
    """
    Simulates data being sent from the t1 port to aud in debugging
    this requires pin 2rx)  and 5(tx) to be connected
    """
    swriter = asyncio.StreamWriter(uart_tx, {})
    while True:
        swriter.write(telegram.format(0,random.random()*100,random.random()*100))
        await swriter.drain()
        await asyncio.sleep(5)



