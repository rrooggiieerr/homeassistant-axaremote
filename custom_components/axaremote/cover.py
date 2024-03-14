from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from axaremote import AXARemote, AXARemoteError
from homeassistant.components.cover import (
    ATTR_CURRENT_POSITION,
    ATTR_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the AXA Remote window opener."""
    axa: AXARemote = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([AXARemoteCover(axa)])


class AXARemoteCover(CoverEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = None
    _attr_device_class = CoverDeviceClass.WINDOW
    _attr_assumed_state = True
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
        | CoverEntityFeature.SET_POSITION
    )
    _attr_should_poll = False

    _attr_current_cover_position = 0
    _attr_is_closed = False
    _attr_is_closing = False
    _attr_is_opening = False

    _attr_extra_state_attributes = {}

    _unsubscribe_updater = None

    def __init__(self, axa: AXARemote) -> None:
        """Initialize the window."""
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, axa.unique_id)},
            name="AXA Remote",
            manufacturer="AXA",
        )
        self._attr_unique_id = axa.unique_id

        self._axa = axa
        self._attr_available = True
        self._attr_device_info["model"] = self._axa.device
        self._attr_device_info["sw_version"] = self._axa.version
        self._attr_current_cover_position = self._axa.position()

    async def async_added_to_hass(self) -> None:
        last_state = await self.async_get_last_state()
        if (
            last_state is not None
            and last_state.attributes.get(ATTR_CURRENT_POSITION) is not None
        ):
            position = last_state.attributes.get(ATTR_CURRENT_POSITION)
            _LOGGER.debug("Old window position: %s", position)

            status = self._axa.status()
            if status == AXARemote.STATUS_LOCKED:
                position = 0
                self._attr_is_closed = True
                self._attr_assumed_state = False
            else:
                self._axa.set_position(position)

            self._attr_current_cover_position = position

            self.start_updater()

    async def async_update(self) -> None:
        _LOGGER.debug("Available: %s", self.available)

        try:
            await self.hass.async_add_executor_job(self._axa.sync_status)
            status = self._axa.status()

            if status == AXARemote.STATUS_DISCONNECTED:
                # Device is offline
                self.stop_updater()
                self._attr_available = False
                self.start_updater(timedelta(seconds=5))
                return

            if status != AXARemote.STATUS_DISCONNECTED:
                # Device is back online
                self.stop_updater()
                self._attr_available = True
                self.start_updater()

            if status == AXARemote.STATUS_LOCKED:
                position = 0
                self._attr_assumed_state = False
            elif status in [AXARemote.STATUS_LOCKING, AXARemote.STATUS_UNLOCKING]:
                position = 0
                self._attr_assumed_state = True
            else:
                position = self._axa.position()
                _attr_assumed_state = True
            _LOGGER.debug("Window position: %5.1f %%", position)

            if status == AXARemote.STATUS_LOCKED:
                self._attr_is_closing = False
                self._attr_is_closed = True
                self._attr_is_opening = False
            elif status in [AXARemote.STATUS_UNLOCKING, AXARemote.STATUS_OPENING]:
                self._attr_is_closing = False
                self._attr_is_closed = False
                self._attr_is_opening = True
            elif status in [AXARemote.STATUS_LOCKING, AXARemote.STATUS_CLOSING]:
                self._attr_is_closing = True
                self._attr_is_closed = False
                self._attr_is_opening = False
            elif status == AXARemote.STATUS_OPEN:
                self._attr_is_closing = False
                self._attr_is_closed = False
                self._attr_is_opening = False
            elif status == AXARemote.STATUS_STOPPED:
                self._attr_is_closing = False
                self._attr_is_closed = False
                self._attr_is_opening = False

            self._attr_current_cover_position = int(position)
        except AXARemoteError as ex:
            raise UpdateFailed(
                f"Error communicating with AXA Remote on {self._axa._connection}"
            ) from ex

    def start_updater(self, interval=timedelta(seconds=1)):
        """Start the updater to update Home Assistant while window is moving."""
        if self._unsubscribe_updater is None:
            _LOGGER.debug("start update listener")
            self._unsubscribe_updater = async_track_time_interval(
                self.hass, self.updater_hook, interval
            )

    @callback
    def updater_hook(self, now):
        """Call for the updater."""
        _LOGGER.debug("updater hook")
        self.async_schedule_update_ha_state(True)

    def stop_updater(self):
        """Stop the updater."""
        if self._unsubscribe_updater is not None:
            _LOGGER.debug("stop update listener")
            self._unsubscribe_updater()
            self._unsubscribe_updater = None

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the window."""
        self.stop_updater()
        await self.hass.async_add_executor_job(self._axa.open)
        self.start_updater()

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the window."""
        self.stop_updater()
        await self.hass.async_add_executor_job(self._axa.close)
        self.start_updater()

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the window."""
        self.stop_updater()
        await self.hass.async_add_executor_job(self._axa.stop)
        self.start_updater()

    async def async_set_cover_position(self, **kwargs) -> None:
        """Move the cover to a specific position."""
        position = kwargs[ATTR_POSITION]
        if self.current_cover_position == position:
            return

        self.stop_updater()

        if self.current_cover_position < position:
            if await self.hass.async_add_executor_job(self._axa.open):
                while self.current_cover_position < position:
                    self.async_schedule_update_ha_state(True)
        elif self.current_cover_position > position:
            if await self.hass.async_add_executor_job(self._axa.close):
                while self.current_cover_position > position:
                    self.async_schedule_update_ha_state(True)

        await self.hass.async_add_executor_job(self._axa.stop)
        self.start_updater()
