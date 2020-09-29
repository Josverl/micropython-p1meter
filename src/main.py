# main.py
# Dummy Sender of the telegrams 

import utime as time
from machine import Pin, UART

# ------------------------
# decode bytearray
# ------------------------
import binascii
def decode(a:bytearray):
    "bytearray to string"
    return binascii.hexlify(a).decode()

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
sender = False
if sender:
    #  ref : https://forum.micropython.org/viewtopic.php?p=43872#top
    #  inverted signal : uart.init(921600, bits=8, stop=1, parity=None, rx=rx, tx=tx, cts=cts, rts=rts,  invert=UART.INV_TX | UART.INV_RX | UART.INV_RTS | UART.INV_CTS) 

    uart1 = UART(1, rx=2, tx=5, baudrate=115200,  bits=8, parity=None, stop=1, invert=UART.INV_TX | UART.INV_RX   )
    # serial settings to use are: a baudrate of 115200, an eight bit bytesize without a parity bit.   115200 8N1 a

    n = 0
    while True:
        uart1.write(telegram)
        n += 1
        print(n)
        time.sleep(1)
else:
    ## interestingly when reading the information with inverted=UART.INV_RX  : this results in an UnicodeError:

    uart1 = UART(1, rx=2, tx=5, baudrate=115200,  bits=8, parity=None, stop=1, invert=UART.INV_RX   )
    #uart1.init(baudrate=115200, bits=8, parity=None, stop=1, invert=UART.INV_TX | UART.INV_RX )
    # serial settings to use are: a baudrate of 115200, an eight bit bytesize without a parity bit.   115200 8N1 & inverse polarity
    while True:
        # Read while there is data on the port
        tele = {'header': '', 'data': [], 'footer': ''}
        while uart1.any():
            line = uart1.readline()
            # print("raw:", line)
            if line:
                # to string and remove last character : \n
                line = line.decode()
            line = line[:-1]
            print("rcvd:", line)
            if line[0] == '/':
                print('header found')
                tele = {'header': line , 'data': [], 'footer': ''}
            elif line[0] == '!':
                print('footer found')
                tele['footer'] = line
                print(tele)
            else:
                tele['data'].append(line)
        time.sleep(1)

