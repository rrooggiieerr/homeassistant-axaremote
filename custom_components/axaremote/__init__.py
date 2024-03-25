"""The AXA Remote integration."""

import logging
import os

import serial
from axaremote import AXARemoteSerial, AXARemoteTelnet
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_TYPE, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONF_SERIAL_PORT, CONF_TYPE_SERIAL, CONF_TYPE_TELNET, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.COVER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AXA Remote from a config entry."""
    axa = None

    conf_type = CONF_TYPE_SERIAL
    if CONF_TYPE in entry.data:
        conf_type = entry.data[CONF_TYPE]

    if conf_type == CONF_TYPE_TELNET:
        host = entry.data[CONF_HOST]
        port = entry.data[CONF_PORT]

        axa = AXARemoteTelnet(host, port)
    else:
        serial_port = entry.data[CONF_SERIAL_PORT]

        axa = AXARemoteSerial(serial_port)

    # Test if we can connect to the device.
    if not await hass.async_add_executor_job(axa.connect):
        raise ConfigEntryNotReady(f"Unable to connect to device {axa.connection}")

    _LOGGER.info("AXA Remote on %s is available", axa.connection)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = axa

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    axa: AXARemote = hass.data[DOMAIN][entry.entry_id]
    await hass.async_add_executor_job(axa.disconnect)

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
