
# boot.py - - runs on boot-up
import sys  # pylint: disable=wrong-import-position
sys.path.insert(1, '/lib')

from micropython import const
import machine
import esp
import logging

#logging 

log = logging.getLogger('boot')

# WiFI: no need to init wifi,it is established from async task

#Debug 
DEBUG = False
if DEBUG:
    # esp.osdebug(0)          # redirect vendor O/S debugging messages to UART(0)
    # esp.osdebug(0, esp.LOG_ERROR)
    esp.osdebug(0, esp.LOG_VERBOSE)
    logging.basicConfig(level=logging.DEBUG)
    #logging.basicConfig(level=logging.INFO)
else:
    #esp.osdebug(None)       # turn off vendor O/S debugging messages
    esp.osdebug(0, esp.LOG_ERROR)   # show errors only 
    logging.basicConfig(level=logging.INFO)


