from micropython import const

# Base SSID to connect to 
homenet = {'SSID': 'IoT', 'password': 'MicroPython'}
broker = {'server': '192.168.1.99', 'user': 'sensor', 'password': 'SensorPassport'}

# Serial Pins 
RX_PIN_NR = const(2)
TX_PIN_NR = const(5)

