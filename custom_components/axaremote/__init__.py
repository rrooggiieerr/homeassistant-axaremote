"""The AXA Remote integration."""
import logging
import os

import serial
from axaremote import AXARemote
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONF_SERIAL_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.COVER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AXA Remote from a config entry."""
    axa = None

    # Test if we can connect to the device.
    try:
        serial_port = entry.data[CONF_SERIAL_PORT]
        axa = AXARemote(serial_port)

        # Open the connection.
        if not axa.connect():
            raise ConfigEntryNotReady(f"Unable to connect to device {serial_port}")

        _LOGGER.info("Device %s is available", serial_port)
    except serial.SerialException as e:
        raise ConfigEntryNotReady(
            f"Unable to connect to device {serial_port}: {e}"
        ) from e

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = axa

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    axa: AXARemote = hass.data[DOMAIN][entry.entry_id]
    axa.disconnect()

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
