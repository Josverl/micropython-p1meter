

## todo
functional:
 - [ ] add signal leds for: 
      - [x] network connected 
      - [x] mqtt connected + ping ok 
      - [x] telegram received (toggle) 
      - optional: meter power detected (6 pin cable)
      ? leds on / off in normal operation
      ? leds automatically off after 10 minutes to aid in troubleshooting on startup 

 - [ ] build case for meter 
 - [ ] periodically send all readings ( per minute / hour ? configurable)
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
 - [ ] switch to more stable MQTT lib
 - [ ] clear last sent state on mqtt reconnect to force sending all
 - [ ] use wlan.wlan_stable flag to determine network connection
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
 - [ ] no write permissions on topic

Test on other firmwares 
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
- [ ] wifi.wlan_stable does not properly reflect the state 
- [ ] clear last sent state on network reconnect
- [ ] set config.dhcp hostname + last MAC bit 
- [ ] LOW PRIO - fix weird UART0 disconnect on LOLIN32 Pro when starting up the network (does not repro on other hardware , and nospiram FW fails to load as well)
- [x] more robust network reconnection 
- [x] add log descriptions for common connection errors
- test cases 
  - [disable wifi / enable wifi]
    - [ok] test / repro network disconnect - re-connect 


nice to have:
 - [ ] parse the date-time from the telegram to make it more readable 
 - [ ] add telnet server for remote diag
 - [ ] publish MAC to mqtt to identify different meters
 - [ ] read config from MQTT /p1_meter/sensor/MAC --> root topic : 'p1_meter_2'
 - [x] logging formatting with colors 
      - new logging lib with format options`


upstream Doc:
 - [ ] create PR for micropython documentation with esp32 UART additions
        - inverted polarity
        - rx tx buffer size

### Done
- [x] catch more MQTT errors
- [x] replace codes -> topic names 
- [x] simulator:  support larger messages 
- [x] only save updated if send actually succeeds, to avoid dampening/removing unsent changes / states  

## Dev setup 
 - git clone
 - micropy install
 - adjust config.py settings :
    - homenet : WiFi SSID and Password 
    - broker : MQtt broker address, user and password
    - RX pins to connect to the P1 Port
    - Options (TX pin if you want to test drive without a connection to a P1 port)
 - upload code from ./src to board
 - 

### Prereqs : 
 - git client
 - python 3.x installed 
### hardware & Firmware 
 - ESP32 board with micropython 1.13 or newer
 - memory: no SPI ram is required

### building
 - building is not needed 

### Testing
You can run the built-in  simulator for testing (using TX_PIN_NR)

  - connect the rx and tx pins with a wire 
  ``` python
      RX_PIN_NR = const(2)
      TX_PIN_NR = const(5)
  ```
  - RX_PIN_NR = const(2)
  TX_PIN_NR = const(5)
    - edit the configuration file `config.py` to enable the Simulator 
  ``` python
      RUN_SIM = True
  ````    
  RUN_SIM = True
 - 

### Recommended: 
 - vscode
 - pymakr extension
 - pip install micropy-cli 


