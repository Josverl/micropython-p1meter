# Stub for MicroPython 'neopixel' module.


class NeoPixel:
    def __init__(self, pin, n):
        self.n = n
        self._buf = [(0, 0, 0)] * n

    def __setitem__(self, i, c):
        self._buf[i] = c

    def __getitem__(self, i):
        return self._buf[i]

    def write(self):
        pass
