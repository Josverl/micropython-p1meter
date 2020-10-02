# boot.py - - runs on boot-up
from micropython import const
import machine
import esp

# no need to init wifi,it is established from async task
DEBUG = False

if DEBUG:
    esp.osdebug(0)          # redirect vendor O/S debugging messages to UART(0)
else:
    esp.osdebug(None)       # turn off vendor O/S debugging messages


# run the simulator for testing 
RUN_SIM = True