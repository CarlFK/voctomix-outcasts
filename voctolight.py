#!/usr/bin/env python3
# Based upon:
# https://github.com/voc/voctomix/tree/voctopanel/example-scripts/voctolight

from enum import Enum
import argparse
import asyncio
import configparser
import json
import os.path


class Config(configparser.ConfigParser, object):
    config_files = [
        os.path.join(os.path.dirname(os.path.realpath(__file__)),
                     'default-config.ini'),
        os.path.join(os.path.dirname(os.path.realpath(__file__)),
                     'config.ini'),
        '/etc/voctomix/voctolight.ini',
        '/etc/voctolight.ini',
        os.path.expanduser('~/.voctolight.ini'),
    ]

    def __init__(self, cmd_line_config=None):
        super().__init__()
        self.cmd_line_config = cmd_line_config
        self._read_config()

    def _read_config(self):
        self.read(self.config_files)
        if self.cmd_line_config:
            self.read_file(self.cmd_line_config)
            self.cmd_line_config.seek(0)

    def setup_with_server_config(self, server_config):
        self.clear()
        self._read_config()
        self.read_dict(server_config)

    def getlist(self, section, option):
        return [x.strip() for x in self.get(section, option).split(',')]


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

    def onnection_lost(self, exc):
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

    def __init__(self, actor, config):
        self.config = config
        self.actor = actor
        actor.reset_led()

    def compute_state(self):
        if self.composite_mode == CompositeModes.fullscreen:
            actor.enable_tally(self.primary)
        else:
            actor.enable_tally(self.a_or_b)

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
            interpreter.compute_state()

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
        if mode == 'fullscreen':
            self.composite_mode = CompositeModes.fullscreen
        elif mode == 'side_by_side_equal':
            self.composite_mode = CompositeModes.side_by_side_equal
        elif mode == 'side_by_side_preview':
            self.composite_mode = CompositeModes.side_by_side_preview
        elif mode == 'picture_in_picture':
            self.composite_mode = CompositeModes.picture_in_picture
        else:
            print('Cannot handle', mode, 'of type', type(mode))

    def handle_server_config(self, args):
        server_config_json = ' '.join(args)
        server_config = json.loads(server_config_json)
        self.config.setup_with_server_config(server_config)


class RPiGPIODriver:
    def __init__(self, config):
        self._import()
        self.gpios = config.get('light', 'gpios').split(',')
        self.gpio_red = int(config.get('light', 'gpio_red'))
        self.reset_led()

    def _import(self):
        global GPIO
        import RPi.GPIO as GPIO

    def reset_led(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        for gpio in self.gpios:
            gpio = int(gpio)
            GPIO.setup(gpio, GPIO.OUT)
            GPIO.output(gpio, GPIO.HIGH)

    def enable_tally(self, enable):
        if enable:
            GPIO.output(self.gpio_red, GPIO.LOW)
        else:
            GPIO.output(self.gpio_red, GPIO.HIGH)


class DebugDriver:
    def __init__(self, config):
        pass

    def reset_led(self):
        print('LED has been reset to off')

    def enable_tally(self, enable):
        if enable:
            print('tally on!')
        else:
            print('tally off!')


class SerialDTRDriver:
    def __init__(self, config):
        self.fn = config.get('light', 'port')
        self.fd = None

    def reset_led(self):
        if self.fd:
            self.fd.close()

    def enable_tally(self, enable):
        if enable:
            self.fd = open(self.fn)
        else:
            if self.fd:
                self.fd.close()
            self.fd = None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Tallylight controlling daemon for voctomix.')
    parser.add_argument(
        '--config', type=open, help='Use a specific config file')
    parser.add_argument(
        '--debug', action='store_true',
        help='Show what would be done instead of toggling lights')
    args = parser.parse_args()
    config = Config(cmd_line_config=args.config)
    driver = config.get('light', 'driver')
    if args.debug:
        actor = DebugDriver(config)
    elif driver == 'rpi':
        actor = RPiGPIODriver(config)
    elif driver == 'serial':
        actor = SerialDTRDriver(config)
    else:
        raise Exception('Unknown driver: ' + driver)
    interpreter = Interpreter(actor, config)
    conn = Connection(interpreter)
    conn.connect(config.get('server', 'host'))
    conn.send('get_config')
    conn.send('get_composite_mode')
    conn.send('get_video')
    conn.loop.run_forever()
