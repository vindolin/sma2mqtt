import sys
import time
import socket
import struct

import paho.mqtt.client as mqtt

MULTICAST_IP = '239.12.255.254'
MULTICAST_PORT = 9522


class NotAnSmaPacket(Exception):
    pass


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

    return parser.parse_args()


def setup_socket():
    mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_IP), socket.INADDR_ANY)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    sock.bind(('', MULTICAST_PORT))
    return sock


def decode_bytes(data):
    return int.from_bytes(data, byteorder="big") / 10


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
    # based on R. Mitchell's code from: https://gist.github.com/mitchese/afd823c3c5036c5b0e5394625f1a81e4
    if data[0:3] != b'SMA':  # only handle packets that start with SMA
        raise NotAnSmaPacket

    # file1 = open('data.txt', 'bw')
    # file1.write(bytearray(data))
    # file1.close()

    l1_buy = decode_bytes(data[164:308][6:8])
    l1_sell = decode_bytes(data[164:308][26:28])

    l2_buy = decode_bytes(data[308:452][6:8])
    l2_sell = decode_bytes(data[308:452][26:28])

    l3_buy = decode_bytes(data[452:596][6:8])
    l3_sell = decode_bytes(data[452:596][26:28])

    total_buy = decode_bytes(data[34:36])
    total_sell = decode_bytes(data[54:56])

    l1_val = l1_sell if l1_sell > l1_buy else l1_buy * -1
    l2_val = l2_sell if l2_sell > l2_buy else l2_buy * -1
    l3_val = l3_sell if l3_sell > l3_buy else l3_buy * -1

    total_val = total_sell if total_sell > total_buy else total_buy * -1

    # 20 results from the length of 10000.0 (7) + the length of the ANSI color characters (13)
    print(f'{color_value(l1_val): >20} + {color_value(l2_val): >20} + {color_value(l3_val): >20} = {color_value(total_val): >20}')

    return (total_buy, total_sell)


def main():
    args = parse_args()
    mqtt_client = mqtt.Client(args.mqtt_client_id)

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

            # setup the multicast socket to the Speedwire host
            sock = setup_socket()

            # loop that reads the Speedwire and publishes to MQTT
            while True:
                if sock:
                    try:
                        buy, sell = decode_speedwire(sock.recv(1024))
                        if buy > 0.0:
                            mqtt_client.publish(f'{args.topic}/buy', buy)
                        if sell > 0.0:
                            mqtt_client.publish(f'{args.topic}/sell', sell)
                    except NotAnSmaPacket:
                        pass

    except Exception as err:
        print(err)


if __name__ == '__main__':
    main()
