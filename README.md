# sma2mqtt

Command line tool that connects to the multipass stream and writes... TODO

TODO


Install:
--------
```bash
pip install sma2mqtt
```

```bash
sma2mqtt --help
```

```
usage: sma2mqtt [-h] [--topic TOPIC] [--client_id CLIENT_ID]
                     [--serial_port SERIAL_PORT] [--mqtt_address MQTT_ADDRESS]
                     [--mqtt_port MQTT_PORT] [--mqtt_username MQTT_USERNAME]
                     [--mqtt_password MQTT_PASSWORD]

Log temperature data and progress from the USB port of a Prusa printer to an MQTT server.

optional arguments:
  -h, --help            show this help message and exit
  --serial_port SERIAL_PORT
                        Path to the serial port device. (default: /dev/ttyACM0)
  --topic TOPIC         Topic for the MQTT message. (default: sma)
  --client_id CLIENT_ID
                        Distinct client ID for the MQTT connection. (default: prusa2mqtt)
  --serial_port SERIAL_PORT
                        Path to the serial port device.
  --mqtt_address MQTT_ADDRESS
                        Address for the MQTT connection. (default: localhost)
  --mqtt_port MQTT_PORT
                        Port for the MQTT connection. (default: 1883)
  --mqtt_username MQTT_USERNAME
                        User name for the MQTT connection. (default: None)
  --mqtt_password MQTT_PASSWORD
                        Password name for the MQTT connection. (default: None)
```
