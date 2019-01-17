# Makes a tomu.im USB Simple sample as a tally light.
# https://github.com/im-tomu/tomu-samples/tree/master/usb_simple

__all__ = ['TomuSimpleLed']

DO_USB = True
try:
    import usb.core
except ImportError:
    DO_USB = False


class Tomu:
    def __init__(self, config):
        self.on = int(config.get('tomu', 'on'))
        self.off = int(config.get('tomu', 'off'))
        if not DO_USB:
            raise ValueError('USB support not available. Install pyusb')

        self.device = usb.core.find(idVendor=0x1209, idProduct=0x70b1)
        if self.device is None:
            raise ValueError('Device not found, flash usb_simple on the tomu.')

        self.device.set_configuration()

    def tally_on(self):
        self.device.ctrl_transfer(0x40, 0, self.on, 0, '')

    def tally_off(self):
        self.device.ctrl_transfer(0x40, 0, self.off, 0, '')
