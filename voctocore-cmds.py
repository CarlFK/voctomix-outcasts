#!/usr/bin/env python3

"""
voctocore-cmds.py: command client for Voctomix.

   Copyright: 2015-2020 Carl F. Karsten <carl@nextdayvideo.com>,

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to
   deal in the Software without restriction, including without limitation the
   rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
   sell copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in
   all copies or substantial portions of the Software.


Features:
    Connects to Voctocore, sends commands, disconnectes, exits.
"""

import argparse
import socket
import sys
import time


def connect(host='localhost', port=9999, timeout=2):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

    try:
        sock.connect((host, port))
        sock.settimeout(timeout)
    except ConnectionRefusedError:
        sys.exit('ConnectionRefusedError - Voctocore not running?  Exiting bye.')

    return sock


def vocto_io(sock, command: bytes):
    """Send a command to the voctocore control server
    returnr response.

    s: socket
    command: voctocore command server command
    """
    try:
        sock.sendall(command)
        data=sock.recv(10000)

    except socket.timeout as err:
        sys.exit(f'socket.timeout - There was a problem while sending {command} voctocore.'
                 'Giving up, bye.')

    return data



def send_cmds(sock, cmds, delay, verbose):
    """Send a list of commands
    delay between each
    maybe echo before sending
    print response
    """

    for cmd in cmds:
        if verbose: print( f'sending: {cmd}' )

        cmd+="\n"
        cmd=cmd.encode()

        reply = vocto_io(sock, cmd)

        reply = reply.decode()
        print(reply)

        time.sleep(delay)


def read_cmds(filename):
    """
    Read vocto commands from a file.
    """
    with open(filename) as f:
        lines=f.read().split('\n')
        cmds = []
        for line in lines:
            line = line.strip()
            # ignore blank lines.
            if line:
                cmds.append(line)

    return cmds


def get_args():
    parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='''Vocto-cmds Client
            Sends commands to voctocore.
            ''')

    parser.add_argument(
        '-c', '--cmds', action='append', default=[],
        help="command to send to core.")

    parser.add_argument(
        '-f', '--file',
        help="file of commands to send to core.")

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
        '--timeout', action='store', type=float, default=.5,
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

    cmds = args.cmds
    if args.file:
        cmds.extend(read_cmds(args.file))

    core_ip = socket.gethostbyname(args.host)
    if args.verbose:
        print(f"{core_ip=}")

    with connect(core_ip, args.port, args.timeout) as sock:
        send_cmds(sock, cmds, args.delay, args.verbose)

    sys.exit()


if __name__ == '__main__':
    main()
