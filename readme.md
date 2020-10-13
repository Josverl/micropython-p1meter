

# connecting 


## Circuit diagram

The ESP UART 1 is used to connect to whatever pin you specify in config.py 
this allows normal functionality to use the USB port (UART 0) for configuration and monitoring of the ESP32.

The RJ12 connector in the electricity meter uses the following layout 
![Rj12](docs/rj-12.png)

Connect the ESP32 to an RJ12 cable/connector following the diagram.

### connection via straight 4/6 wire cable :
Note that this will reverse the pin numbers on the female connector that you are using

| RJ12 P1       | cable|RJ12 Meter| ESP32 Pin | color     | 4w test cable | comments
| --------------|----- |----------| ----------| ----------|---------------|------------
| 1 - 5v out    | ---> | 6        | 5v or Vin |           |               | [Optional]. max 250 mA When using a 6 pin cable you can use the power source provided by the meter.
| 2 - CTS       | <--- | 5        | gpio-5    | blue      |  zwart        | Clear to Send,  High = allow P1 Meter to send data
| 3 - Data GND  | <--> | 4        | GND       | black     |  rood         | 
| 4 - -         |      | 3        | -         |           |  groen        | 
| 5 - RXD (data)| ---> | 2        | gpio-2    | yellow    |  geel         | 1K external pull-up resistor needed
| 6 - Power GND | ---- | 1        | GND       |           |               | [Optional]

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

3 Neopixel Leds (top to bottom):

|led| purpose | Red           | Green                    | other
|---|---------|---------------|--------------------------|---
| 2 | P1 meter| CRC Error     | CRC OK                   | **Blue**: data received , **Purple** : Simulator sending Data
| 1 | mqtt    | Not connected | Connected to MQTT broker | **Yellow**: Data could not be send to Broker
| 0 | wifi    | Not connected | IP address acquired      |

## configuration file 

<document What to change in the config file>

Please adjust the relevant settings in [config.py](src/config.py)
``` python
# Serial Pins for meter connection
# TX pin is only used for testing/simulation but needs to be specified
RX_PIN_NR = const(2)
TX_PIN_NR = const(15)
RTS_PIN_NR = const(5)

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


