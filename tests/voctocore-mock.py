#!/usr/bin/env python3

"""
voctocore-mock.py: mock voctocore server to test voctocore-cmds.py

   Copyright: 2025-2026 Carl F. Karsten <carl@nextdayvideo.com>,

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to
   deal in the Software without restriction, including without limitation the
   rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
   sell copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in
   all copies or substantial portions of the Software.


Features:
    waits for connections on a port (defult 9999)
    echos what it recieves.
"""

import argparse
import socket
import sys
import time

from pprint import pprint

# Echo server program

class Server:

    timeout=1
    verbose=False
    forever=False

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def process_data(self,data):
        if self.verbose: print(f'Server.process_data {data=}')
        self.conn.sendall(data)

    def run(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

            if self.verbose: print('setting up...')
            sock.bind((self.host, self.port))
            sock.listen(self.timeout)
            while True:
                if self.verbose: print('listening...')
                self.conn, self.addr = sock.accept()
                with self.conn:
                    if self.verbose: print('Connected by', self.addr)
                    while True:
                        data = self.conn.recv(1024)
                        if not data: break
                        if self.verbose: print('Recieved', data)
                        self.process_data(data)
                if self.forever:
                    continue
                else:
                    if self.verbose: print('Exiting...')
                    break

class Vocto(Server):

    """mocky server that does things with the string sent to it.
    quit
    wait time to wait
    help
    two causes too much data to be sent back and the server throws and error like vocotocore.
    """

    def command_processor(self,data):
        """
        given a string,
        see if there is anything interesting
        and do something interisting
        """

        words = data.decode().strip("\n").split()

        if words[0] == "quit":
            if self.verbose: print('Exiting...')
            sys.exit(0)

        elif words[0] == "wait":
            sleepy_time=int(words[1])
            if self.verbose: print(f'Waiting {sleepy_time=}...')
            time.sleep(sleepy_time)
            if self.verbose: print('Wake up.')

        elif words[0] == "help":
            data = self.__doc__
            data = data.encode()

        elif words[0] == "two":
            super().process_data(data)

        elif words[0] == "None":
            if self.verbose: print('Not replying, let the client timeout.')
            data = None

        return data


    def process_data(self, data):
        data = self.command_processor(data)
        if data is not None:
            super().process_data(data)


def get_args():
    parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='''Vocto-mock Server
            Receives commands like voctocore.''')

    parser.add_argument(
        '-v', '--verbose', action='count', default=0,
        help="print commands as they are sent.")

    parser.add_argument(
        '--host', action='store',
        default='localhost',
        help="hostname of vocto core")

    parser.add_argument(
        '--port', action='store', default=9999,
        help="port of vocto core")

    parser.add_argument(
        '--forever', action='store_true', default=False,
        help="listen forever or exit after first receive")

    parser.add_argument(
        '--timeout', action='store', type=int, default=1,
        help="seconds to wait for reply from server, then abort")

    parser.add_argument(
        '--delay', action='store', type=float, default=0,
        help="delay in seconds between commands")

    parser.add_argument(
        '--debug', action='store_true',
        help="debugging things, (currently nothing)")

    args = parser.parse_args()

    return args


def main():

    args = get_args()

    serv = Vocto(args.host, args.port)
    serv.timeout = args.timeout
    serv.verbose = args.verbose
    serv.forever = args.forever
    serv.run()


if __name__ == '__main__':
    main()
