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


import socket
import datetime
import sys

host = 'localhost'
port = 9999

conn = socket.create_connection((host, port))
fd = conn.makefile('rw')

for line in fd:
    words = line.rstrip('\n').split(' ')

    signal = words[0]
    args = words[1:]

    if signal == 'message' and args[0] == 'cut':
        ts = datetime.datetime.now().strftime("%Y-%m-%d/%H_%M_%S")
        print(ts)
        sys.stdout.flush()
