from micropython import const

# Base SSID to connect to 
homenet = {'SSID': 'IoT', 'password': 'MicroPython'}
broker = {'server': '192.168.1.99', 'user': 'sensor', 'password': 'SensorPassport'}

# Serial Pins for meter connection
RX_PIN_NR = const(2)
# TX = Only for simulation 
TX_PIN_NR = const(5)

