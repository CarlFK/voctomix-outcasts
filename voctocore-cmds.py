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
import logging
import socket
import sys
import time

logger = logging.getLogger(__name__)

def connect(host='localhost', port=9999, timeout=2, wait=False):

    logger.debug(f"Establishing Connection to {host=}")

    host_ip = socket.gethostbyname(host)
    logger.debug(f"{host_ip=}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

    fails=0
    sleepy_time=2

    while True:
        try:
            sock.connect((host, port))
            logger.debug(f"Connected: {sock.getpeername()=}")
            break
        except ConnectionRefusedError:
            if wait:
                fails+=1
                logger.debug(f"ConnectionRefusedError - {fails=} {sleepy_time=} before looping...")
                time.sleep(sleepy_time)
                continue
            else:
                sys.exit('ConnectionRefusedError - Voctocore not running?  Exiting bye.')

    if fails:
        logger.debug(f"{fails=} so sleep a little more just to be sure.")
        time.sleep(sleepy_time)
        logger.debug(f"Wake up and get to work.")

    sock.settimeout(timeout)

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



def send_cmds(sock, cmds, delay):
    """Send a list of commands
    delay between each
    maybe echo before sending
    maybe print response
    """

    for cmd in cmds:
        logger.info( f'sending: {cmd}' )

        cmd+="\n"
        cmd=cmd.encode()

        reply = vocto_io(sock, cmd)

        reply = reply.decode()
        logger.info(reply)

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
            if not line:
                # ignore blank lines.
                continue
            if line[0].startswith(("#",";")):
                # ignore #/; comment or whatever # lines
                continue
            cmds.append(line)


    return cmds

def log_setup(verbose):

    levels = { 4:logging.CRITICAL, 3:logging.DEBUG, 2:logging.INFO, 1:logging.WARNING, 0:logging.ERROR }
    level = levels[verbose]

    logging.basicConfig(
            format='{asctime} {funcName}:{lineno} {levelname}: {message}',
            datefmt='%H:%M:%S',
            level=level,
            style="{")



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
        help="print commands, replies and connection info.")

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
        '--wait-for-core', action='store_true',
        help="loop forever when can't connect to core.")

    parser.add_argument(
        '--debug', action='store_true',
        help="debugging things, (currently nothing)")

    args = parser.parse_args()

    return args


def main():

    args = get_args()

    log_setup(args.verbose)

    cmds = args.cmds
    if args.file:
        cmds.extend(read_cmds(args.file))

    with connect(args.host, args.port, args.timeout, args.wait_for_core) as sock:
        send_cmds(sock, cmds, args.delay)

    sys.exit()


if __name__ == '__main__':
    main()
