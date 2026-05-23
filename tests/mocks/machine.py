# Mock for MicroPython 'machine' module.
# Used by the test suite when running on the MicroPython Unix port (no real hardware).


class Pin:
    IN = 0
    OUT = 1
    PULL_DOWN = 0
    PULL_UP = 1

    def __init__(self, pin_id, mode=-1, pull=-1):
        self._val = 0

    def on(self):
        self._val = 1

    def off(self):
        self._val = 0

    def value(self, v=None):
        if v is None:
            return self._val
        self._val = int(bool(v))


class UART:
    INV_RX = 1
    INV_TX = 2

    def __init__(self, *args, **kwargs):
        pass

    def read(self, nbytes=-1):
        return b''

    def write(self, buf):
        pass

    def any(self):
        return 0

    def __repr__(self):
        return 'UART(mock)'


def unique_id():
    return b'\x00\x00\x00\x00\x00\x00'


def reset():
    raise SystemExit('machine.reset() called in mock')
