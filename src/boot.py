
# boot.py - - runs on boot-up
# pylint: disable= wrong-import-position, wrong-import-order
import sys  # pylint: disable=wrong-import-position
sys.path.insert(1, '/lib')

import esp
import logging
from config import DEBUG

#############################################################
# setup colorized log formating in columns to ease reading
#############################################################
log = logging.getLogger('boot')

# pylint: disable= bad-whitespace
class LogFormatter(logging.Handler):
    RESET       = u"\u001b[0m"
    FG_RED      = u"\u001b[31m"
    FG_GREEN    = u"\u001b[32m"
    FG_YELLOW   = u"\u001b[33m"
    FG_BLUE     = u"\u001b[34m"
    FG_MAGENTA  = u"\u001b[35m"
    FG_CYAN     = u"\u001b[36m"

    def emit(self, record):
        color = self.RESET
        if record.levelno >= logging.CRITICAL:
            color = self.FG_MAGENTA
        elif record.levelno >= logging.ERROR:
            color = self.FG_RED
        elif record.levelno >= logging.WARNING:
            color = self.FG_YELLOW
        elif record.levelno >= logging.INFO:
            color = self.RESET
        elif record.levelno >= logging.DEBUG:
            color = self.FG_CYAN
        print("{}{:<8} {:<10} {}{}".format(color, record.levelname, record.name, record.message, self.RESET) )

logging.getLogger().addHandler(LogFormatter())



if DEBUG:
    esp.osdebug(0, esp.LOG_VERBOSE)         # show all HW info
    logging.basicConfig(level=logging.DEBUG)
else:
    esp.osdebug(0, esp.LOG_ERROR)           # show HW errors only
    logging.basicConfig(level=logging.INFO)

# WiFI: no need to init wifi,it is established by an async task

import machine
FREQ = 240
log.info("Set clock frequency to {}Mhz".format(FREQ))
machine.freq(FREQ*1000000)
