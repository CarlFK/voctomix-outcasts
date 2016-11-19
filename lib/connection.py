import json
import logging
import socket

"""
   Copyright: 2015,2016    Carl F. Karsten <carl@nextdayvideo.com>, Ryan Verner <ryan@nextdayvideo.com.au>

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:
 
   The above copyright notice and this permission notice shall be included in
   all copies or substantial portions of the Software.
"""


log = logging.getLogger('Connection')


class Connection(object):
    def __init__(self, host, port=9999):
        self.host = host
        self.port = port

        log.info('Establishing connection to %s', host)
        self.sock = socket.create_connection((host, port))

        log.debug('Connection successful \o/')
        ip = self.sock.getpeername()[0]
        log.debug('Remote-IP is %s', ip)

    def fetch_config(self):
        log.info('Reading server-config')
        fd = self.sock.makefile('rw')
        fd.write('get_config\n')
        fd.flush()

        while True:
            line = fd.readline()
            signal, _, args = line.partition(' ')

            if signal != 'server_config':
                continue

            server_config = json.loads(args)
            return server_config
