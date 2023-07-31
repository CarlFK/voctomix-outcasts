from .base_plugin import BasePlugin
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


def get_plugin(config) -> BasePlugin:
    """Creates an instance of a plugin named in Voctolight's configuration file."""
    plugin_name = config.get('light', 'plugin')
    plugin_cls = PLUGINS.get(plugin_name, None)

    if plugin_cls is None:
        raise ValueError(f'{plugin_name} is not a valid plugin name')

    return plugin_cls(config)
