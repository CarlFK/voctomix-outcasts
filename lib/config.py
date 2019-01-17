from configparser import ConfigParser
from os.path import join, dirname, realpath, expanduser

__all__ = ['Config']

class Config(ConfigParser):
    config_files = [
        join(dirname(realpath(__file__)),
                     'default-config.ini'),
        join(dirname(realpath(__file__)),
                     'config.ini'),
        '/etc/voctomix/voctolight.ini',
        '/etc/voctolight.ini',
        expanduser('~/.voctolight.ini'),
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
