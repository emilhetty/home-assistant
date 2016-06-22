"""
Support for Zwave garage door components.

For more details about this platform, please refer to the documentation
https://home-assistant.io/components/garagedoor.zwave/
"""
# Because we do not compile openzwave on CI
# pylint: disable=import-error
import logging
from homeassistant.components.garage_door import DOMAIN
from homeassistant.components.zwave import ZWaveDeviceEntity
from homeassistant.components import zwave
from homeassistant.components.garage_door import GarageDoorDevice

COMMAND_CLASS_SWITCH_BINARY = 0x25  # 37

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Find and return Z-Wave garage door device."""
    if discovery_info is None or zwave.NETWORK is None:
        return

    node = zwave.NETWORK.nodes[discovery_info[zwave.ATTR_NODE_ID]]
    value = node.values[discovery_info[zwave.ATTR_VALUE_ID]]

    value.set_change_verified(False)
    add_devices([ZwaveGarageDoor(value)])


class ZwaveGarageDoor(zwave.ZWaveDeviceEntity, GarageDoorDevice):
    """Representation of an Zwave garage door device."""

    def __init__(self, value):
        """Initialize the zwave garage door."""
        from openzwave.network import ZWaveNetwork
        from pydispatch import dispatcher
        ZWaveDeviceEntity.__init__(self, value, DOMAIN)
        self._node = value.node
        dispatcher.connect(
            self.value_changed, ZWaveNetwork.SIGNAL_VALUE_CHANGED)

    def value_changed(self, value):
        """Called when a value has changed on the network."""
        if self._value.node == value.node:
            self.update_ha_state(True)
            _LOGGER.debug("Value changed on network %s", value)

    @property
    def is_closed(self):
        """Return the current position of Zwave garage door."""
        for value in self._node.get_values(
                class_id=COMMAND_CLASS_SWITCH_BINARY).values():
            if value.command_class == 37 and value.index == 0:
                return value.data

    def close_door(self):
        """Close the garage door."""
        self._value.node.set_switch(self._value.value_id, False)

    def open_door(self):
        """Open the garage door."""
        self._value.node.set_switch(self._value.value_id, True)
