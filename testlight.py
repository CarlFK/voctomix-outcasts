#!/usr/bin/env python3
# Test driver for Voctolight plugins.
from argparse import ArgumentParser, FileType
from sys import exit

from lib.config import Config
from lib.plugins.all_plugins import PLUGINS

def main():
    parser = ArgumentParser(
        description='Test program for testing tallylight plugins')
    parser.add_argument(
        '-c', '--config', type=FileType('r'), help='Use a specific config file')
    args = parser.parse_args()
    config = Config(cmd_line_config=args.config)

    plugin_cls = PLUGINS.get(config.get('light', 'plugin'), None)
    if plugin_cls is None:
        print('No plugin selected, control will not work!')
        exit(1)

    plugin = plugin_cls(config)

    try:
        while True:
            print('Tally light on. Press ENTER to turn off, ^C to stop.')
            plugin.tally_on()
            input()
            print('Tally light off. Press ENTER to turn on, ^C to stop.')
            plugin.tally_off()
            input()
    except KeyboardInterrupt:
        pass

if __name__ in '__main__':
    main()
