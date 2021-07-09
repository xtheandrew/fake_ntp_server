#!/usr/bin/env python
from __future__ import print_function

import argparse
import socket
import time
import datetime

from ntp_packet import (
    NTPPacket,
    NTPTimestamp,
)

def fake_server(address, fake_time):

    s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind( (address, 123) )

    time_start = time.time()

    while True:
        packet, source = s.recvfrom(100)
        print('Received {length} byte packet from {source}'.format(length=len(packet), source=source[0]))
        packet = NTPPacket.from_bytes(packet)

        if packet.version not in (3, 4):
            print('Unsupported NTP version.')
            continue

        if packet.mode != 3:
            print('Not a client request.')
            continue

        try:
            print('Client time:', packet.transmit_timestamp)
        except:
            pass
        time_since_start = time.time() - time_start
        return_time = fake_time + time_since_start

        response = NTPPacket()
        response.version = packet.version
        response.mode = 4
        response.stratum = 1
        response.reference_identifier = b'XFAK'
        response.origin_timestamp = packet.transmit_timestamp
        response.reference_timestamp = NTPTimestamp.from_unix_timestamp(return_time)
        response.receive_timestamp = NTPTimestamp.from_unix_timestamp(return_time)
        response.transmit_timestamp = NTPTimestamp.from_unix_timestamp(return_time)

        response = response.to_bytes()
        s.sendto(response, source)

def parse_bind_addr(address):
    address = socket.getaddrinfo(address, 123, 0, 0, 0, socket.AI_NUMERICHOST)
    address = address[0]
    if address[0] == socket.AF_INET:
        return '::ffff:' + address[4][0]
    else:
        return address[4][0]

def parse_time(t):
    dt = datetime.datetime.strptime(t, '%Y%m%d%H%M%S')
    return time.mktime(dt.timetuple())

def parse_args():
    parser = argparse.ArgumentParser(description='Fake NTP server')
    parser.add_argument('--listen', type=parse_bind_addr, default='::')
    parser.add_argument('--time', type=parse_time, default=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    return parser.parse_args()

def main():
    args = parse_args()
    fake_server(args.listen, args.time)

if __name__ == '__main__':
    main()
