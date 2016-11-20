#!/usr/bin/env python3
#
# Copyright: 2015,2016    Carl F. Karsten <carl@nextdayvideo.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.


import argparse
import socket
import datetime
import sys


def capture_cuts(sock):
    """Listen to a voctocore control socket, and yield on cuts"""
    fd = sock.makefile('rw')
    for line in fd:
        words = line.rstrip('\n').split(' ')

        signal = words[0]
        args = words[1:]

        if signal == 'message' and args[0] == 'cut':
            yield


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--host', default='localhost',
                   help='Hostname of voctocore')
    p.add_argument('--port', type=int, default=9999,
                   help='Port to connect to, on voctocore')
    args = p.parse_args()

    sock = socket.create_connection((args.host, args.port))
    for cut in capture_cuts(sock):
        ts = datetime.datetime.now().strftime("%Y-%m-%d/%H_%M_%S")
        print(ts)
        sys.stdout.flush()


if __name__ == '__main__':
    main()
