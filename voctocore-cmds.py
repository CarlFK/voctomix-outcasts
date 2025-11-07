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

def connect(host='localhost', port=9999):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

    try:
        sock.connect((host, port))
        sock.settimeout(2)
    except ConnectionRefusedError:
        sys.exit('ConnectionRefusedError - Voctocore not running?  Exiting bye.')

    fd = sock.makefile('w')

    return fd


def read_cmds(filename):
    """
    Read vocto commands from a file.
    """
    with open(filename) as f:
        lines=f.read().split('\n')
        cmds = []
        for line in lines:
            line = line.strip()
            if line:
                cmds.append(line)

    return cmds


def vocto_send(fd, command: str):
    """Write commands to the voctocore control server

    fd: socket file object
    command: voctocore command server command
    """
    try:
        fd.write(command + '\n')
        fd.flush()

    except socket.timeout as err:
        sys.exit(f'socket.timeout - There was a problem while sending {command} voctocore.'
                 'Giving up, bye.')


def send_cmds(fd, cmds, verbose):

    for cmd in cmds:
        if verbose: print( f'sending command: {cmd}' )
        vocto_send(fd, cmd)


def get_args():
    parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='''Vocto-cmds Client
            Sends commands to voctocore.
            ''')

    parser.add_argument(
        '-c', '--cmds', action='append',
        help="command to send to core.")

    parser.add_argument(
        '-f', '--file',
        help="file of commands to send to core.")

    parser.add_argument(
        '-v', '--verbose', action='count', default=0,
        help="Also print INFO and DEBUG messages.")

    parser.add_argument(
        '--host', action='store',
        default='localhost',
        help="hostname of vocto core")

    parser.add_argument(
        '--port', action='store',
        default=9999,
        help="port of vocto core")

    parser.add_argument(
        '--debug', action='store_true',
        help="debugging things, like dump a  gst-launch-1.0 command")

    args = parser.parse_args()

    return args


def main():

    args = get_args()
    core_ip = socket.gethostbyname(args.host)

    fd=connect(args.host, args.port)

    if args.file:
        cmds = read_cmds(args.file)
    else:
        cmds = args.cmds

    send_cmds(fd, cmds, args.verbose)

    sys.exit()


if __name__ == '__main__':
    main()
