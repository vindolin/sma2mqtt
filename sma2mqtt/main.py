import sys
import time
import socket
import struct
import os
import tempfile

import paho.mqtt.client as mqtt

MULTICAST_IP = '239.12.255.254'  # fixed multicast IP of SMA Energy Meter/Home Manger
MULTICAST_PORT = 9522

DATA_START_OFFSET = 4
FORCE_PUBLISH_EVERY = 50

ENERGY_MAX = 10000000
POWER_MAX = 100000

dump_data = False
just_print = False
tmp_path = os.path.join(tempfile.gettempdir(), 'sma_dump.bin')


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(
        description='Listen to SMA Speedwire broadcast traffic and convert it to MQTT messages.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--topic', help='Topic for the MQTT message.', default='sma')
    parser.add_argument('--mqtt_client_id', help='Distinct client ID for the MQTT connection.', default='sma2mqtt')
    parser.add_argument('--mqtt_address', help='Address for the MQTT connection.', default='localhost')
    parser.add_argument('--mqtt_port', help='Port for the MQTT connection.', type=int, default=1883)
    parser.add_argument('--mqtt_username', help='User name for the MQTT connection.', default=None)
    parser.add_argument('--mqtt_password', help='Password name for the MQTT connection.', default=None)
    parser.add_argument('--just_print', help='Don\'t connect to MQTT and just print the values.', action='store_true')
    parser.add_argument('--dump_data', help='Write the binary datagram to {TMP}/sma_dump.bin.', action='store_true')

    return parser.parse_args()


class NotAnSmaPacket(Exception):
    pass


class MissingEndMarker(Exception):
    pass


class DataOutOfBounds(Exception):
    pass


def find_end_marker(data, offset):
    position = data.find(b'\x00\x02\x0b\x05', offset) + 4
    length = 1
    return int.from_bytes(data[position: position + length], byteorder="big")


def find_int32_be(data, marker, offset):
    position = data.find(marker, offset) + len(marker)
    length = 4
    return int.from_bytes(data[position: position + length], byteorder='big')


def find_bigint64_be(data, marker, offset):
    position = data.find(marker, offset) + len(marker)  # the -1 is here to include the last \x00 into the 8 bytes
    length = 8
    return int.from_bytes(data[position: position + length], byteorder="big")


def validate_energy(kwh):
    if abs(kwh) > ENERGY_MAX:
        raise DataOutOfBounds


def validate_power(kw):
    if abs(kw) > POWER_MAX:
        raise DataOutOfBounds


values_template = {
    'total_w_buy': None,
    'total_w_sell': None,
    'total_w': None,

    'l1_w_buy': None,
    'l2_w_buy': None,
    'l3_w_buy': None,

    'l1_w_sell': None,
    'l2_w_sell': None,
    'l3_w_sell': None,

    'l1_w': None,
    'l2_w': None,
    'l3_w': None,

    'total_w': None,

    'kwh_buy': None,
    'kwh_sell': None,
}

last_values = values_template.copy()
counter = 0


def setup_socket():
    mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_IP), socket.INADDR_ANY)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    sock.bind(('', MULTICAST_PORT))
    return sock


def green(string):
    return f'\033[0;32m{string}\033[00m'


def red(string):
    return f'\033[0;31m{string}\033[00m'


def white(string):
    return f'\033[0;37m{string}\033[00m'


def color_value(number):
    if number < 0:
        return red(number)
    elif number > 0:
        return green(number)

    return white('-------')


def decode_speedwire(data):
    global counter
    if counter == 0:
        print(f'{"L1 W": >8} + {"L2 W": >8} + {"L3 W": >8} = {"TOTAL W": >8} | {"SELL kWh": >8} {"BUY kWh": >8}')
    counter += 1

    if data[0:3] != b'SMA':  # only handle packets that start with SMA
        raise NotAnSmaPacket

    end = find_end_marker(data, DATA_START_OFFSET)
    if end != 82:
        raise MissingEndMarker

    # write binary dgram to disk
    if dump_data:
        with open(tmp_path, 'bw') as tmp_file:
            tmp_file.write(bytearray(data))

    total_w_buy = find_int32_be(data, b'\x00\x01\x04\x00', DATA_START_OFFSET)
    total_w_buy /= 10

    kwh_buy = find_bigint64_be(data, b'\x00\x01\x08\x00', DATA_START_OFFSET)
    kwh_buy = round(kwh_buy / 3600 / 1000, 8)

    l1_w = find_int32_be(data, b'\x00\x15\x04\x00', DATA_START_OFFSET)
    l1_w_buy = l1_w / 10

    l2_w = find_int32_be(data, b'\x00\x29\x04\x00', DATA_START_OFFSET)
    l2_w_buy = l2_w / 10

    l3_w = find_int32_be(data, b'\x00\x3d\x04\x00', DATA_START_OFFSET)
    l3_w_buy = l3_w / 10

    total_w_sell = find_int32_be(data, b'\x00\x02\x04\x00', DATA_START_OFFSET)
    total_w_sell /= 10

    kwh_sell = find_bigint64_be(data, b'\x00\x02\x08\x00', DATA_START_OFFSET)
    kwh_sell = kwh_sell / 3600 / 1000

    l1_w = find_int32_be(data, b'\x00\x16\x04\x00', DATA_START_OFFSET)
    l1_w_sell = l1_w / 10

    l2_w = find_int32_be(data, b'\x00\x2A\x04\x00', DATA_START_OFFSET)
    l2_w_sell = l2_w / 10

    l3_w = find_int32_be(data, b'\x00\x3e\x04\x00', DATA_START_OFFSET)
    l3_w_sell = l3_w / 10

    l1w = l1_w_sell if l1_w_sell > l1_w_buy else l1_w_buy * -1
    l2w = l2_w_sell if l2_w_sell > l2_w_buy else l2_w_buy * -1
    l3w = l3_w_sell if l3_w_sell > l3_w_buy else l3_w_buy * -1

    # sometimes invalid large values get reported
    # check against the bounds and ignore runs with erroneous values
    validate_energy(kwh_buy)
    validate_energy(kwh_sell)
    validate_power(l1_w_sell)
    validate_power(l2_w_sell)
    validate_power(l3_w_sell)
    validate_power(l1_w_buy)
    validate_power(l2_w_buy)
    validate_power(l2_w_buy)

    total_w = total_w_sell if total_w_sell > total_w_buy else total_w_buy * -1

    # 20 results from the length of 10000.0 (7) + the length of the ANSI color characters (13), TODO preconvert to strings
    kwh_sell_str = f'{kwh_sell: >8.4f}'
    kwh_buy_str = f'{kwh_buy: >8.4f}'

    print(f'{color_value(l1w): >20} + {color_value(l2w): >20} + {color_value(l3w): >20} = {color_value(total_w): >20} | {green(kwh_sell_str)} {red(kwh_buy_str)}')

    values = values_template.copy()

    # copy values into return value dict
    for k, v in locals().items():
        if k in values:
            values[k] = v

    return values


def publish_values(mqtt_client, topic, values):
    global counter, last_values

    # publish all values regardless of changes every n runs
    if counter > FORCE_PUBLISH_EVERY:
        last_values = values_template.copy()
        counter = 0

    # publish only values that have changed from the former run
    for k, v in values.items():
        if last_values[k] != v:
            if not just_print:
                mqtt_client.publish(f'{topic}/{k}', v)
            last_values[k] = v


def main():
    global dump_data, just_print
    args = parse_args()
    dump_data = args.dump_data
    just_print = args.just_print

    mqtt_client = mqtt.Client(args.mqtt_client_id)

    def socket_loop():
        # setup the multicast socket to the Speedwire host
        sock = setup_socket()

        # loop that reads the Speedwire and publishes to MQTT
        while True:
            if sock:
                try:
                    values = decode_speedwire(sock.recv(1024))
                    publish_values(mqtt_client, args.topic, values)

                # ignore errors for this run
                except NotAnSmaPacket:
                    pass
                except MissingEndMarker:
                    pass
                except DataOutOfBounds:
                    pass

    if just_print:
        socket_loop()
    else:
        if args.mqtt_username and args.mqtt_password:
            mqtt_client.username_pw_set(args.mqtt_username, args.mqtt_password)

        try:
            while True:  # endless loops that reconnects if an mqtt or socket error occurs
                mqtt_client.loop_start()
                mqtt_client.connect(args.mqtt_address, args.mqtt_port)

                print('MQTT connecting', end='')
                # try to connect to the MQTT server
                for i in range(30):  # try for 3 seconds
                    if mqtt_client.is_connected():
                        break
                    print('.', end='')
                    sys.stdout.flush()
                    time.sleep(0.1)
                print('connected\n')

                if not mqtt_client.is_connected():
                    sys.exit(f'Could not connect to the MQTT server at {args.mqtt_address}:{args.mqtt_port}, please check your parameters.')

                socket_loop()

        except Exception as err:
            raise
            print(err)


if __name__ == '__main__':
    main()
