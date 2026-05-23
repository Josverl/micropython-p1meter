# Mock for MicroPython 'network' module.

STA_IF = 0
AP_IF = 1

STAT_GOT_IP = 1010
STAT_CONNECTING = 1001
STAT_WRONG_PASSWORD = 202
STAT_NO_AP_FOUND = 201
STAT_ASSOC_FAIL = 203


class WLAN:
    def __init__(self, interface_id=STA_IF):
        self._active = False
        self._connected = True   # pretend connected so healthy() can run

    def active(self, is_active=None):
        if is_active is None:
            return self._active
        self._active = is_active

    def connect(self, ssid=None, password=None):
        pass

    def disconnect(self):
        self._connected = False

    def isconnected(self):
        return self._connected

    def status(self):
        return STAT_GOT_IP

    def ifconfig(self):
        return ('192.168.1.1', '255.255.255.0', '192.168.1.254', '8.8.8.8')

    def config(self, **kwargs):
        pass
