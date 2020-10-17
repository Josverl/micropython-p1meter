"ntp time MicroPython 1.11 updated with for local time offset"
from machine import RTC
from utime import localtime
try:
    import usocket as socket
except OSError:
    import socket
try:
    import ustruct as struct
except OSError:
    import struct

# (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
NTP_DELTA = 3155673600

host = "pool.ntp.org"

def ntp_time():
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1b
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()
    val = struct.unpack("!I", msg[40:44])[0]
    return val - NTP_DELTA

# There's currently no timezone support in MicroPython, so
# utime.localtime() will return UTC time (as if it was .gmtime())

# RTC.datetime([datetimetuple]) Get or set the date and time of the RTC.
# The 8-tuple has the following format:
# (year, month, day, weekday, hours, minutes, seconds, subseconds)
# RTC.init(datetime)
# (year, month, day[, hour[, minute[, second[, microsecond[, tzinfo]]]]])

def settime(tzoffset:int=0):
    t = ntp_time()
    tm = localtime(t-(tzoffset * 60 * 60))
    RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
