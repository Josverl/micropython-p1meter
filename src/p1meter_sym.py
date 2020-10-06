# pylint: disable=trailing-whitespace

import logging
import random
from machine import UART
import uasyncio as asyncio
from utilities import crc16

# Logging
log = logging.getLogger('SIMULATION')
# logging.basicConfig(level=logging.INFO)
#####################################################
# test rig
#####################################################


class P1MeterSIM():
    """
    P1 meter to fake a Dutch electricity meter and generate some reading to test the rest of the software
    """
    def __init__(self, uart:UART):
        # do not re-init port for sim
        self.uart = uart
        # self.telegram = template

    async def sender(self, interval :int = 5):
        """
        Simulates data being sent from the t1 port to aid in debugging
        this assume that pin rx=2 and tx=5 are connected
        """
        swriter = asyncio.StreamWriter(self.uart, {})
        while True:
            log.info('send telegram')
            telegram = self.fake_message()
            log.debug('TX telegram message: {}'.format(telegram))
            swriter.write(telegram)
            await swriter.drain()
            await asyncio.sleep(interval)

    def fake_message(self):
        # Pick a template

        #msg = meter1
        msg = meter3

        u = random.randint(-1000,1000) /100
        msg = msg.format(0,max(u, 0), -1*min(u,0))


        buf = bytearray(msg.replace('\n','\r\n'))
        crc_computed = "{0:0X}".format(crc16(buf))
        log.debug("TX CRC16 buf : {}".format(buf))
        log.debug("TX computed CRC {0}".format(crc_computed))
        msg = msg + "{0}".format(crc_computed) + '\n'
        return msg



meter1 = """/XMX5LGBBFG1012650850
1-3:0.2.8(42)
1-0:1.7.0({1:06.3f}*kW)
1-0:2.7.0({2:06.3f}*kW)
1-0:1.8.1(009248.534*kWh)
0-1:24.2.1(200909220000S)(05907.828*m3)
!"""

meter2=(   "/KFM5KAIFA-METER\n"
        "\n"
        "1-3:0.2.8(42)\n"
        "0-0:1.0.0(170124213128W)\n"
        "0-0:96.1.1(4530303236303030303234343934333135)\n"
        "1-0:1.8.1(000306.946*kWh)\n"
        "1-0:1.8.2(000210.088*kWh)\n"
        "1-0:2.8.1(000000.000*kWh)\n"
        "1-0:2.8.2(000000.000*kWh)\n"
        "0-0:96.14.0(0001)\n"
        "1-0:1.7.0(02.793*kW)\n"
        "1-0:2.7.0(00.000*kW)\n"
        "1-0:1.7.0({1:06.3f}*kW)\n"
        "1-0:2.7.0({2:06.3f}*kW)\n"
        "0-0:96.7.21(00001)\n"
        "0-0:96.7.9(00001)\n"
        "1-0:99.97.0(1)(0-0:96.7.19)(000101000006W)(2147483647*s)\n"
        "1-0:32.32.0(00000)\n"
        "1-0:52.32.0(00000)\n"
        "1-0:72.32.0(00000)\n"
        "1-0:32.36.0(00000)\n"
        "1-0:52.36.0(00000)\n"
        "1-0:72.36.0(00000)\n"
        "0-0:96.13.1()\n"
        "0-0:96.13.0()\n"
        "1-0:31.7.0(003*A)\n"
        "1-0:51.7.0(005*A)\n"
        "1-0:71.7.0(005*A)\n"
        "1-0:21.7.0(00.503*kW)\n"
        "1-0:41.7.0(01.100*kW)\n"
        "1-0:61.7.0(01.190*kW)\n"
        "1-0:22.7.0(00.000*kW)\n"
        "1-0:42.7.0(00.000*kW)\n"
        "1-0:62.7.0(00.000*kW)\n"
        "0-1:24.1.0(003)\n"
        "0-1:96.1.0(4730303331303033333738373931363136)\n"
        "0-1:24.2.1(170124210000W)(00671.790*m3)\n"
        "!"
    )



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


meter3 = """/XMX5LGBBFG1012463817
1-3:0.2.8(42)
0-0:1.0.0(180624024002S)
0-0:96.1.1(4530303331303033323632373634333136)
1-0:1.8.1(002200.945*kWh)
1-0:1.8.2(001961.604*kWh)
1-0:2.8.1(000000.000*kWh)
1-0:2.8.2(000000.000*kWh)
0-0:96.14.0(0001)
1-0:1.7.0({1:06.3f}*kW)
1-0:2.7.0({2:06.3f}*kW)
0-0:96.7.21(00003)
0-0:96.7.9(00001)
1-0:99.97.0(1)(0-0:96.7.19)(170214081346W)(0000006334*s)
1-0:32.32.0(00000)
1-0:32.36.0(00000)
0-0:96.13.1()
0-0:96.13.0()
1-0:31.7.0(002*A)
1-0:21.7.0(00.378*kW)
1-0:22.7.0(00.000*kW)
0-1:24.1.0(003)
0-1:96.1.0(4730303235303033333630383535373136)
0-1:24.2.1(180624020000S)(00968.481*m3)
!"""