from .rpi_gpio import RpiGpio
from .serial_dtr import SerialDtr
from .stdout import Stdout
from .tomu import Tomu


PLUGINS = {
    'rpi_gpio': RpiGpio,
    'serial_dtr': SerialDtr,
    'stdout': Stdout,
    'tomu': Tomu,
}
