# todo

## functional:
 - [x] add signal leds for: 
      - [x] network connected - green
      - [x] mqtt connected + ping ok - yellow
      - [x] telegram received (toggle) - blue
      - [x] SIM telegram Send (toggle) - red
      - optional: meter power detected (6 pin cable)
      ? leds on / off in normal operation
      ? leds automatically off after 10 minutes to aid in troubleshooting on startup 


testen / documenteren , dit zou in 1.13 moeten zitten
esp32: Add support for mDNS queries and responder.
They are both enabled by default, but can be disabled by defining
MICROPY_HW_ENABLE_MDNS_QUERIES and/or MICROPY_HW_ENABLE_MDNS_RESPONDER to
0.  The hostname for the responder is currently taken from
tcpip_adapter_get_hostname() but should eventually be configurable.



 - [x] build case for meter 
 - [x] periodically send all readings ( per minute / hour ? configurable)
 - [ ] also publish the ident from the header 

 - [x] add actionable descriptions to common mqtt connection errors 
 - [?] prevent / cleanup common mqtt connection errors on initial connect
 ``` log
        WARN     mqttclient mqtt not healthy
        INFO     mqttclient create mqtt client homeassistant.local
        WARN     mqttclient need to start mqqt client
        INFO     mqttclient connecting to mqtt server homeassistant.local
        ERROR    mqttclient 5
        WARN     SIMULATION send simulated telegram
        INFO     mqttclient publish 23 meter readings
        ERROR    mqttclient Problem sending json to MQTT : [Errno 104] ECONNRESET
        ERROR    mqttclient Oops while disconnecting MQTT : [Errno 104] ECONNRESET
       
```
mqtt client:  

ERROR    mqttclient OS Error -2
 

 - [ ] the readings stay the same if the meter goes offline - how to deal with this 

 
 - [ ] switch to more stable MQTT lib
 - [ ] clear last sent state on mqtt reconnect to force sending all
 - [ ] use wlan.wlan_stable flag to determine network connection
         # !!  Note the use of conf.DEBUG rather than from conf import DEBUG. 
         # This construction means that you can alter the variable during the life of the program, and have that change reflected elsewhere (assuming a single thread/process, obviously).
         # ref: https://stackoverflow.com/questions/24023601/is-it-good-practice-to-use-import-main
        - also disconnect / reset mqtt client in that case 
 - [ ] LOW - reconnect quicker 
 - [ ] ping mqtt server on server connect
 - [ ] ping mqtt server periodically and reconnect on issue 
 - [ ] support TLS/SSL 
 - [x] refactor to class to get rid of global
 - [x] detect mqtt issues on sending and disconnect / reconnect
 - [?] add queue of messages to send 





Test cases : 
 - [ok] restart mqtt server 
 - [x] wrong password 
 - [x] no network connectivity to mqtt broker
 - [ ] no write permissions on ROOT_TOPIC

Test on other firmwares 
 - [OK] micropython 1.13 - bld 103 - nightly  
        - add mqqt.simple to libs
 - [ fail] LoBo + AsyncIO ( for telnet)
 - [ fail] micropython 1.12
 - [ ] pycopy


Stability:
 - [x] CRC16 check
 - [x] CRC16 type bug 

code quality:
 - [ ] pylint errors 
        - [ ] asyncio
        - [ ] gc
        - [ ] sys
network:
- [ ] wifi.wlan_stable does not properly reflect the state ( need to import module , not just the state )
- [ ] clear last sent state on network reconnect
- [x] set config.dhcp hostname + last MAC bit 
- [ ] LOW PRIO - fix weird UART0 disconnect on LOLIN32 Pro when starting up the network (does not repro on other hardware , and nospiram FW fails to load as well)
- [x] more robust network reconnection 
- [x] add log descriptions for common connection errors
- test cases 
  - [disable wifi / enable wifi]
    - [ok] test / repro network disconnect - re-connect 


nice to have:
 - [ ] parse the date-time from the telegram to make it more readable 
 - [x] add webrepl for remote diag
 - [x] add ftp server for remote diag
 - [x] publish MAC to mqtt to identify different meters
 - [ ] read config from MQTT /p1_meter/sensor/MAC --> root ROOT_TOPIC : 'p1_meter_2'
 - [x] logging formatting with colors 
      - new logging lib with format options`


upstream Doc:
 - [ ] create PR for micropython documentation with esp32 UART additions
        - inverted polarity
        - rx tx buffer size

### Done
- [x] catch more MQTT errors
- [x] replace codes -> ROOT_TOPIC names 
- [x] simulator:  support larger messages 
- [x] only save updated if send actually succeeds, to avoid dampening/removing unsent changes / states  

