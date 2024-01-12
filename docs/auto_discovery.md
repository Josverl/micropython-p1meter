To register the switch we need inform home assistant with name of the switch and all its MQTT topics,

mosquitto_pub -V mqttv311 -h 192.168.0.17 -p 1883 -t "homeassistant/switch/bedroom/config" -m '{"name": "bedroom", "command_topic": "homeassistant/switch/bedroom/set", "payload_on": "ON", "payload_off": "OFF", "availability_topic": "homeassistant/switch/bedroom/available", "state_topic": "homeassistant/bedroom/state"}'

topic `homeassistant/switch/bedroom/config`
Config 
``` json
{
    "name": "bedroom",
    "command_topic": "homeassistant/switch/bedroom/set",
    "payload_on": "ON",
    "payload_off": "OFF",
    "availability_topic": "homeassistant/switch/bedroom/available",
    "state_topic": "homeassistant/bedroom/state"
}
```
Once the switch is registered it should be visible on home assistant UI.



## for a Sensor 
https://www.home-assistant.io/docs/mqtt/discovery/#sensors-with-multiple-values 
<discovery_prefix>/<component>/[<node_id>/]<object_id>/config
Text
<component>: One of the supported MQTT components, eg. binary_sensor.
<node_id> (Optional): ID of the node providing the topic, this is not used by Home Assistant but may be used to structure the MQTT topic. The ID of the node must only consist of characters from the character class [a-zA-Z0-9_-] (alphanumerics, underscore and hyphen).
<object_id>: The ID of the device. This is only to allow for separate topics for each device and is not used for the entity_id. The ID of the device must only consist of characters from the character class [a-zA-Z0-9_-] (alphanumerics, underscore and hyphen).

<discovery_prefix>/<component>/[<node_id>/]<object_id>/config
topic `homeassistant/sensor/test/p1_meter/config`
Config 
``` json
{
    "name": "AUTO Electricity total consumption High Tariff",
    "icon": "mdi:lightning-bolt",
    "unit_of_measurement": "kWh",
    "state_topic": "p1_meter/total/consumption_high_tariff_kWh",
    "value_template": "{{ value|float }}"
}
```



``` yaml
sensor:

# Sensors for esp32_p1meter to be used in Home Assistant
  - platform: mqtt
    name: Electricity total consumption High Tariff
    icon: mdi:lightning-bolt
    unit_of_measurement: 'kWh'
    state_topic: "p1_meter/total/consumption_high_tariff_kWh"
    value_template: "{{ value|float }}"

  - platform: mqtt
    name: Electricity total consumption Low Tariff
    icon: mdi:lightning-bolt
    unit_of_measurement: 'kWh'
    state_topic: "p1_meter/total/consumption_low_tariff_kWh"
    value_template: "{{ value|float }}"

  - platform: mqtt
    name: Electricity total production High Tariff
    icon: mdi:lightning-bolt
    unit_of_measurement: 'kWh'
    state_topic: "p1_meter/total/production"

```

