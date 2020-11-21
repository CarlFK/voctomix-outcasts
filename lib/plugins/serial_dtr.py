# Turning on a light opens a serial port, which pulls the DTR line high.
# Turning off a light closes the serial port, pulling DTR low.

from .base_plugin import BasePlugin

__all__ = ['SerialDtr']


class SerialDtr(BasePlugin):
    def __init__(self, config):
        self.fn = config.get('serial_dtr', 'port')
        self.fd = None

    def tally_on(self):
        self.fd = open(self.fn)

    def tally_off(self):
        if self.fd:
            self.fd.close()
            self.fd = None

    def __del__(self):
        tally_off()
