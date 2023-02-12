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
                     [--mqtt_password MQTT_PASSWORD] [--just_print] [--dump_data]
                     [--serial_nr] [--force_print_serial] [--print_offsets]

Command line tool that listens to the multicast Speedwire of a SMA Energy Meter/Home Manger 2.0 and writes the values to a MQTT server.

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
  --just_print
                        Don't connect to MQTT and just print the values.
  --dump_data
                        Write the binary datagram to {TMP}/sma_dump.bin.
  --serial_nr
                        Only watch packets for this serial number.
  --force_print_serial
                        Print the serial number, even if only one was found.
  --print_offsets
                        Print the offsets where the patterns were found.
```
