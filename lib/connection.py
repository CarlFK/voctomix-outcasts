import json
import logging
import socket


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
