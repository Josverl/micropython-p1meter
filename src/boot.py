# boot.py - - runs on boot-up

# This file is executed on every boot (including wake-boot from deepsleep)
import sys,network, time, machine

# create station interface - Standard WiFi client 
wlan = network.WLAN(network.STA_IF) 
if not wlan.active():
    print("Activate Wlan")
    # activate the interface
    wlan.active(True)
    # connect to a known WiFi 
    wlan.connect('IoT', 'MicroPython')   
else:
    print("Wlan already active")

# Note that this may take some time, so we need to wait 
# Wait 5 sec or until connected 
tmo = 50
while not wlan.isconnected():
    time.sleep_ms(100)
    tmo -= 1
    if tmo == 0:
        break

# prettyprint the interface's IP/netmask/gw/DNS addresses
config = wlan.ifconfig()
print("IP:{0}, Network mask:{1}, Router:{2}, DNS: {3}".format( *config ))
del config
