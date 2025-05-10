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
from time import sleep

from lib.connection import Connection
from lib.corebits import VocConf, VocCmd


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
        "--lap-time",
        action="store",
        default=20,
        type=int,
        dest="lap_time",
        help="time for one lap",
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

    delay=args.lap_time / sources

    # send commands forever:
    voccmd = VocCmd(args.host, args.port, args.debug)
    sources_cycle(voccmd, sources, delay)


if __name__ == "__main__":
    main()
