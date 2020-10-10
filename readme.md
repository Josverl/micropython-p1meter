

## todo
functional:
 - [ ] add signal leds for: 
      - [x] network connected - green
      - [x] mqtt connected + ping ok - yellow
      - [x] telegram received (toggle) - blue
      - [x] SIM telegram Send (toggle) - red
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


# connecting 


## Circuit diagram

The ESP UART 1 is used to connect to whatever pin you specify in config.py 
this allows normal functionality to use the USB port (UART 0) for configuration and monitoring of the ESP32.

![Rj12](docs/rj-12.png)

Connect the ESP32 to an RJ12 cable/connector following the diagram.

| P1 pin        | ESP32 Pin | color   | comments
| --------------| ----------| --------|--------
| 1 - 5v out    | 5v or Vin | red     | optional. max 250 mA When using a 6 pin cable you can use the power source provided by the meter.
| 2 - RTS       | 3.3v      | blue    |
| 3 - Data GND  | GND       | black   | 
| 4 - -         | -         |         | 
| 5 - RXD (data)| gpio2     | yellow  | 10k pull-up recommended (internal / external) 
| 6 - Power GND | -         |         |

## install 
 - git clone
 - micropy install
 - adjust config.py settings :
    - homenet : WiFi SSID and Password 
    - broker : MQtt broker address, user and password
    - RX pins to connect to the P1 Port
    - Options (TX pin if you want to test drive without a connection to a P1 port)
 - upload code from /src folder to the board

## connection / operation

Leds :
|pin  | color | meaning
|-----|-------|-----------
|     | Red   | ON : something is wrong 
|     | Green | ON: connected to WLAN
|     | Yellow| ON: Connected to MQTT broker
|     | Blue  | Blink : toggles when a complete datagram was received 

## configuration file 

<document What to change in the config file>

Please adjust the relevant settings in [config.py](src/config.py)
``` python
# Serial Pins for meter connection
# TX pin is only used for testing/simulation but needs to be specified
RX_PIN_NR = const(2)
TX_PIN_NR = const(15)

# Base SSID to connect to
homenet = {'SSID': 'IoT', 'password': 'MicroPython'}

#the mqtt broker to connect to
broker = {'server': 'homeassistant.local', 'user': 'sensor', 'password': 'beepbeep'}

CLIENT_ID = b'p1_meter_' + hexlify(unique_id())
ROOT_TOPIC = b"p1_meter"

#also publish telegram as json
publish_as_json = False
```


### Prereqs : 
 - git client
 - python 3.x installed 

### Hardware & Firmware 
 - just about any ESP32 board 
 - configured with micropython 1.13 or newer  
   http://micropython.org/download/esp32/
    - ESP32 GENERIC-SPIRAM : [esp32spiram-idf3-20200902-v1.13.bin](http://micropython.org/resources/firmware/esp32spiram-idf3-20200902-v1.13.bin)
 - memory:   
   no SPI ram is required,  the firmware auto detects if it is present and runs on either.

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


