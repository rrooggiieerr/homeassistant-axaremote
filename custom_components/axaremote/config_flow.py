"""Config flow for AXA Remote integration."""

from __future__ import annotations

import logging
import os
from typing import Any, Final

import homeassistant.helpers.config_validation as cv
import serial
import voluptuous as vol
from axaremote import AXARemoteSerial, AXARemoteTelnet
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_TYPE
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_MANUAL_PATH,
    CONF_SERIAL_PORT,
    CONF_TYPE_SERIAL,
    CONF_TYPE_TELNET,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT: Final = 23


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AXA Remote."""

    VERSION = 1

    _step_setup_serial_schema = None

    _step_setup_network_schema = vol.Schema(
        {
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        }
    )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            user_selection = user_input[CONF_TYPE]
            if user_selection == "Serial":
                return await self.async_step_setup_serial()

            return await self.async_step_setup_network()

        list_of_types = ["Serial", "Network"]

        schema = vol.Schema({vol.Required(CONF_TYPE): vol.In(list_of_types)})
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_setup_serial(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the setup serial step."""
        errors: dict[str, str] = {}

        ports = await self.hass.async_add_executor_job(serial.tools.list_ports.comports)
        list_of_ports = {}
        for port in ports:
            list_of_ports[port.device] = (
                f"{port}, s/n: {port.serial_number or 'n/a'}"
                + (f" - {port.manufacturer}" if port.manufacturer else "")
            )

        self._step_setup_serial_schema = vol.Schema(
            {
                vol.Exclusive(CONF_SERIAL_PORT, CONF_SERIAL_PORT): vol.In(
                    list_of_ports
                ),
                vol.Exclusive(
                    CONF_MANUAL_PATH, CONF_SERIAL_PORT, CONF_MANUAL_PATH
                ): cv.string,
            }
        )

        if user_input is not None:
            try:
                info = await self.validate_input_setup_serial(user_input, errors)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception as ex:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception: %s", ex)
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=info)

        return self.async_show_form(
            step_id="setup_serial",
            data_schema=self._step_setup_serial_schema,
            errors=errors,
        )

    async def validate_input_setup_serial(
        self, data: dict[str, Any], errors: dict[str, str]
    ) -> dict[str, Any]:
        """Validate the user input allows us to connect.

        Data has the keys from _step_setup_serial_schema with values provided by the user.
        """
        # Validate the data can be used to set up a serial connection.
        self._step_setup_serial_schema(data)

        serial_port = None
        if CONF_MANUAL_PATH in data:
            serial_port = data[CONF_MANUAL_PATH]
        elif CONF_SERIAL_PORT in data:
            serial_port = data[CONF_SERIAL_PORT]

        if serial_port is None:
            raise vol.error.RequiredFieldInvalid("No serial port configured")

        serial_port = await self.hass.async_add_executor_job(
            get_serial_by_id, serial_port
        )

        # Test if the device exists
        if not os.path.exists(serial_port):
            raise vol.error.PathInvalid(f"Device {serial_port} does not exists")

        await self.async_set_unique_id(serial_port)
        self._abort_if_unique_id_configured()

        # Test if we can connect to the device.
        try:
            axa = AXARemoteSerial(serial_port)
            if not await self.hass.async_add_executor_job(axa.connect):
                raise CannotConnect(f"Unable to connect to the device {serial_port}")

            await self.hass.async_add_executor_job(axa.disconnect)
            _LOGGER.info("Device %s available", serial_port)
        except serial.SerialException as ex:
            raise CannotConnect(
                f"Unable to connect to the device {serial_port}"
            ) from ex

        # Return info that you want to store in the config entry.
        return {
            "title": f"AXA Remote {serial_port}",
            CONF_TYPE: CONF_TYPE_SERIAL,
            CONF_SERIAL_PORT: serial_port,
        }

    async def async_step_setup_network(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step when setting up network configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await self.validate_input_setup_network(user_input, errors)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception as ex:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception: %s", ex)
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=info)
            # data = await self.validate_input_setup_network(user_input, errors)
            # if not errors:
            #     return self.async_create_entry(
            #         title=f"{data[CONF_HOST]}:{data[CONF_PORT]}", data=data
            #     )

        return self.async_show_form(
            step_id="setup_network",
            data_schema=self._step_setup_network_schema,
            errors=errors,
        )

    async def validate_input_setup_network(
        self, data: dict[str, Any], errors: dict[str, str]
    ) -> dict[str, Any]:
        """Validate the user input allows us to connect.

        Data has the keys from _step_setup_network_schema with values provided by the user.
        """
        # Validate the data can be used to set up a network connection.
        self._step_setup_network_schema(data)

        host = data[CONF_HOST]
        port = data[CONF_PORT]

        # ToDo Test if the host exists

        await self.async_set_unique_id(f"{host}:{port}")
        self._abort_if_unique_id_configured()

        # Test if we can connect to the device.
        try:
            axa = AXARemoteTelnet(host, port)
            if not await self.hass.async_add_executor_job(axa.connect):
                raise CannotConnect(f"Unable to connect to the device on {host}:{port}")

            await self.hass.async_add_executor_job(axa.disconnect)
            _LOGGER.info("Device on %s:%s available", host, port)
        except serial.SerialException as ex:
            raise CannotConnect(
                f"Unable to connect to the device on {host}:{port}"
            ) from ex

        # Return info that you want to store in the config entry.
        return {
            "title": f"AXA Remote {host}:{port}",
            CONF_TYPE: CONF_TYPE_TELNET,
            CONF_HOST: host,
            CONF_PORT: port,
        }


def get_serial_by_id(dev_path: str) -> str:
    """Return a /dev/serial/by-id match for given device if available."""
    by_id = "/dev/serial/by-id"
    if not os.path.isdir(by_id):
        return dev_path

    for path in (entry.path for entry in os.scandir(by_id) if entry.is_symlink()):
        if os.path.realpath(path) == dev_path:
            return path
    return dev_path


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
