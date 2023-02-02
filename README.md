# sma2mqtt

Command line tool that listens to the multicast Speedwire of a SMA Energy Meter/Home Manger 2.0 and writes the values to a MQTT server.

I'm using this in my home to read the power consumption/generation from a SMA Home Manager 2.0.


Use at your own risk.



Install:
--------
```bash
pip install sma2mqtt
```

```bash
sma2mqtt --help
```

```
usage: sma2mqtt [-h] [--topic TOPIC] [--mqtt_client_id MQTT_CLIENT_ID]
                     [--mqtt_address MQTT_ADDRESS]
                     [--mqtt_port MQTT_PORT] [--mqtt_username MQTT_USERNAME]
                     [--mqtt_password MQTT_PASSWORD]

Log temperature data and progress from the USB port of a Prusa printer to an MQTT server.

optional arguments:
  -h, --help            show this help message and exit
  --topic TOPIC         Topic for the MQTT message. (default: sma)
  --mqtt_client_id MQTT_CLIENT_ID
                        Distinct client ID for the MQTT connection. (default: sma2mqtt)
  --mqtt_address MQTT_ADDRESS
                        Address for the MQTT connection. (default: localhost)
  --mqtt_port MQTT_PORT
                        Port for the MQTT connection. (default: 1883)
  --mqtt_username MQTT_USERNAME
                        User name for the MQTT connection. (default: None)
  --mqtt_password MQTT_PASSWORD
                        Password name for the MQTT connection. (default: None)
```
