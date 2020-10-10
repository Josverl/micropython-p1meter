

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

## Simulation / test mode 
The p1 meter comes with a built-in test and simulation mode that allows you to test and  change the software, without needing to physically connect it to a electricity meter.

this simulation mode can be enabled  by wiring, or by making a change to the config.py file 

To enable this wia wiring: 
 1. Connect Pin 18 --> GND , enable Simulator 
 2. Connect Pin 15 --> Pin 2 , connect simulator TX to RX 

**By default:**  
- the root topic is changed 
- a fake P1 message is generated every 10 seconds on Pin 15 
  - this message has a few random values added to it 
  - the CRC16 is calculated before sending
- the message is passed of the serial connect ( see .2 above) to the input 
- the message is is processed by the normal software and sent to mqtt usign a different root topic to avoid interfering with actual input..

![simulated output in mqtt](docs/simulator_mqtt.png)

To change the fake message see [p1meter_sym.py](src/p1meter_sym.py)


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


