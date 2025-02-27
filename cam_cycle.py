#!/usr/bin/env python3
"""
cam_cycle.py: cycles through the inputs.

   Copyright: 2025-2025 Carl F. Karsten <carl@nextdayvideo.com>,

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to
   deal in the Software without restriction, including without limitation the
   rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
   sell copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in
   all copies or substantial portions of the Software.


Features:
    Retrieves list of sources from vocto-core server
    set_video_a #1, sleep, next

"""

import argparse
from pprint import pprint
import socket
import sys
from time import sleep

from lib.connection import Connection


class VocConf:

    debug = False
    core_ip = None

    def get_server_conf(self):

        # establish a synchronus connection to server
        conn = Connection(self.core_ip)

        # fetch config from server
        server_config = conn.fetch_config()

        if self.debug:
            pprint(server_config)

        return server_config

    def __init__(self, host, debug):
        self.debug = debug
        self.core_ip = socket.gethostbyname(host)
        if debug:
            print(f"{self.core_ip=}")


class VocCmd:

    debug = False
    fd = None

    def connect_core(self, host, port):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        try:
            sock.connect((host, port))
            sock.settimeout(2)
            fd = sock.makefile("w")
        except ConnectionRefusedError:
            sys.exit("Voctocore is not running. Exiting")

        return fd

    def vocto_write(self, command: str):
        """Write commands to the voctocore control server

        command: voctocore command server command
        """

        if self.debug:
            print(f"{command=}")

        self.fd.write(command + "\n")
        self.fd.flush()

        return None

    def __init__(self, host, port, debug):
        self.debug = debug
        self.fd = self.connect_core(host, port)


def sources_cycle(vc, sources, delay):

    while True:
        for source in sources:
            vc.vocto_write(f"set_video_a {source}")
            sleep(delay)


def get_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Vocto-cycle Client
            Sources are retrieved from the server.
            cycle though sources.
            """,
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Also print INFO and DEBUG messages.",
    )

    parser.add_argument(
        "--delay",
        action="store",
        default=5,
        type=int,
        help="delay between source by this many seconds",
    )

    parser.add_argument(
        "--host", action="store", default="localhost", help="hostname of vocto core"
    )

    parser.add_argument(
        "--port", action="store", default=9999, help="port of vocto core"
    )

    parser.add_argument("--debug", action="store_true", help="debugging things.")

    args = parser.parse_args()

    return args


def main():

    args = get_args()

    # get sources:
    vocconf = VocConf(args.host, args.debug)
    conf = vocconf.get_server_conf()
    # Pull out the list of sources
    sources = conf["mix"]["sources"].split(",")

    # send commands forever:
    voccmd = VocCmd(args.host, args.port, args.debug)
    sources_cycle(voccmd, sources, args.delay)


if __name__ == "__main__":
    main()
