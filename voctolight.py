#!/usr/bin/env python3
# Based upon:
# https://github.com/voc/voctomix/tree/voctopanel/example-scripts/voctolight

from argparse import ArgumentParser, FileType
import asyncio
from enum import Enum
import json
from sys import exit

from lib.config import Config
from lib.plugins.all_plugins import get_plugin


class Connection(asyncio.Protocol):
    def __init__(self, interpreter):
        self.interpreter = interpreter

    def connect(self, host, port=9999):
        self.loop = asyncio.get_event_loop()
        self.conn = self.loop.create_connection(lambda: self, host, port)
        self.loop.run_until_complete(conn.conn)

    def send(self, message):
        self.transport.write(message.encode())
        self.transport.write('\n'.encode())

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        # print('data received: {}'.format(data.decode()))
        lines = data.decode().rstrip('\n').split('\n')
        for line in lines:
            interpreter.handler(line)

    def connection_lost(self, exc):
        print('server closed the connection')
        asyncio.get_event_loop().stop()


# FIXME: Duplicate from videomix.py
class CompositeModes(Enum):
        fullscreen = 0
        side_by_side_equal = 1
        side_by_side_preview = 2
        picture_in_picture = 3


class Interpreter(object):
    a_or_b = False
    primary = False
    composite_mode = CompositeModes.fullscreen

    def __init__(self, actor, config, debug=False):
        self.config = config
        self.actor = actor
        self.debug = debug
        actor.tally_off()
        if self.debug:
            print('LED has been reset to off')

    def compute_state(self):
        if self.composite_mode == CompositeModes.fullscreen:
            return self.primary
        else:
            return self.a_or_b

    def handler(self, response):
        words = response.split()
        signal = words[0]
        args = words[1:]
        try:
            handler = getattr(self, 'handle_{}'.format(signal))
        except AttributeError:
            print('Ignoring signal', signal)
        else:
            handler(args)
            if interpreter.compute_state():
              print('LED has been switched on')
              actor.tally_on()
            else:
              print('LED has been switched off')
              actor.tally_off()

    def handle_composite(self, composite_mode):
        """Parse `sbs(a,b)` into mode=sbs, cam_a=a, cam_b=b"""
        mode, rest = composite_mode.split('(', 1)
        cam_a, cam_b = rest.rstrip(')').split(',', 1)
        self.handle_video_status([cam_a, cam_b])
        self.handle_composite_mode(mode)

    def handle_video_status(self, cams):
        mycam = self.config.get('light', 'cam')
        if mycam in cams:
            self.a_or_b = True
        else:
            self.a_or_b = False

        self.primary = (cams[0] == mycam)
        # print ('Is primary?', self.primary)

    def handle_composite_mode(self, mode_list):
        mode = mode_list[0]
        if mode in ('fullscreen', 'fs'):
            self.composite_mode = CompositeModes.fullscreen
        elif mode in ('side_by_side_equal', 'sbs'):
            self.composite_mode = CompositeModes.side_by_side_equal
        elif mode in ('side_by_side_preview', 'lec'):
            self.composite_mode = CompositeModes.side_by_side_preview
        elif mode == 'picture_in_picture':
            self.composite_mode = CompositeModes.picture_in_picture
        else:
            print('Cannot handle', mode, 'of type', type(mode))

    def handle_server_config(self, args):
        server_config_json = ' '.join(args)
        server_config = json.loads(server_config_json)
        self.config.setup_with_server_config(server_config)


if __name__ == '__main__':
    parser = ArgumentParser(
        description='Tallylight controlling daemon for voctomix.')
    parser.add_argument(
        '-c', '--config', type=FileType('r'), help='Use a specific config file')
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='Show what would be done in addition to toggling lights')
    args = parser.parse_args()
    config = Config(cmd_line_config=args.config)
    actor = get_plugin(config)
    interpreter = Interpreter(actor, config, debug=args.debug)
    conn = Connection(interpreter)
    conn.connect(config.get('server', 'host'))
    conn.send('get_config')
    conn.send('get_composite_mode')
    conn.send('get_video')
    try:
        conn.loop.run_forever()
    except KeyboardInterrupt:
        print('Quitting (Ctrl-C)')
    actor.reset_led()
