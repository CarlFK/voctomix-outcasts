#!/usr/bin/env python3
"""
corbits.py: interfaces to vocto-core.

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
    VocConf: gets the config from core.
    VocCmd: sends commands to core.

"""

from pprint import pprint
import socket
import sys

from lib.connection import Connection


class VocConf:

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


