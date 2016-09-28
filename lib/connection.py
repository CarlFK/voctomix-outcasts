import logging
import socket
import json
from queue import Queue


log = logging.getLogger('Connection')
conn = None
ip = None
port = 9999
command_queue = Queue()
signal_handlers = {}

def establish(host):
	global conn, port, log, ip

	log.info('establishing Connection to %s', host)
	conn = socket.create_connection( (host, port) )
	log.debug('Connection successful \o/')

	ip = conn.getpeername()[0]
	log.debug('Remote-IP is %s', ip)

def fetchServerConfig():
	global conn, log

	log.info('reading server-config')
	fd = conn.makefile('rw')
	fd.write("get_config\n")
	fd.flush()

	while True:
		line = fd.readline()
		words = line.split(' ')

		signal = words[0]
		args = words[1:]

		if signal != 'server_config':
			continue

		server_config_json = " ".join(args)
		server_config = json.loads(server_config_json)
		return server_config
