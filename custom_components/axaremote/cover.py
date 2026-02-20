from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from axaremote import AXARemote, AXARemoteError, AXAStatus
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
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=1)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the AXA Remote window opener."""
    axa: AXARemote = config_entry.runtime_data
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
    _update_interval = None

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
        self._attr_current_cover_position = None

    async def async_added_to_hass(self) -> None:
        last_state = await self.async_get_last_state()
        if (
            last_state is not None
            and last_state.attributes.get(ATTR_CURRENT_POSITION) is not None
        ):
            position = last_state.attributes.get(ATTR_CURRENT_POSITION)

            [status, _position] = self._axa.status()
            if status == AXAStatus.LOCKED:
                position = 0
                self._attr_is_closed = True
                self._attr_assumed_state = False
            else:
                self._axa.restore_position(position)

            self._attr_current_cover_position = position

            self.start_updater()

    async def async_update(self) -> None:
        try:
            if self._axa.busy:
                [status, position] = self._axa.status()
            else:
                [status, position] = await self.hass.async_add_executor_job(
                    self._axa.sync_status
                )

            if not self._axa.connected and self._attr_available:
                # Device is offline
                self._attr_available = False
                self.start_updater(timedelta(seconds=5))
                return
            if not self._axa.connected:
                # Device is still offline
                self._attr_available = False
                return
            if self._axa.connected and not self._attr_available:
                # Device is back online
                self._attr_available = True
                self.start_updater()

            if (
                status not in [AXAStatus.OPENING, AXAStatus.CLOSING]
                and self._update_interval != SCAN_INTERVAL
            ):
                self.start_updater()

            if status == AXAStatus.LOCKED:
                position = 0
                self._attr_assumed_state = False
            elif status in [AXAStatus.LOCKING, AXAStatus.UNLOCKING]:
                position = 0
                self._attr_assumed_state = True
            else:
                self._attr_assumed_state = True

            if status == AXAStatus.LOCKED:
                self._attr_is_closing = False
                self._attr_is_closed = True
                self._attr_is_opening = False
            elif status in [AXAStatus.UNLOCKING, AXAStatus.OPENING]:
                self._attr_is_closing = False
                self._attr_is_closed = False
                self._attr_is_opening = True
            elif status in [AXAStatus.LOCKING, AXAStatus.CLOSING]:
                self._attr_is_closing = True
                self._attr_is_closed = False
                self._attr_is_opening = False
            elif status == AXAStatus.OPEN:
                self._attr_is_closing = False
                self._attr_is_closed = False
                self._attr_is_opening = False
            elif status == AXAStatus.STOPPED:
                self._attr_is_closing = False
                self._attr_is_closed = False
                self._attr_is_opening = False

            self._attr_current_cover_position = int(position)
        except AXARemoteError as ex:
            raise UpdateFailed(
                f"Error communicating with AXA Remote on {self._axa.connection}"
            ) from ex

    def start_updater(self, interval=SCAN_INTERVAL):
        """Start the updater to update Home Assistant while window is moving."""
        if self._unsubscribe_updater and self._update_interval != interval:
            self.stop_updater()

        if self._unsubscribe_updater is None:
            self._update_interval = interval
            self._unsubscribe_updater = async_track_time_interval(
                self.hass, self.updater_hook, interval
            )

    @callback
    def updater_hook(self, now):
        """Call for the updater."""
        self.async_schedule_update_ha_state(True)

    def stop_updater(self):
        """Stop the updater."""
        if self._unsubscribe_updater is not None:
            self._unsubscribe_updater()
            self._unsubscribe_updater = None
            self._update_interval = None

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the window."""
        self.stop_updater()

        try:
            await self.hass.async_add_executor_job(self._axa.open)
        except AXARemoteError as ex:
            _LOGGER.error(
                "Problem communicating with %s, reason: %s", self._axa.connection, ex
            )
        finally:
            self.start_updater()

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the window."""
        self.stop_updater()

        try:
            await self.hass.async_add_executor_job(self._axa.close)
        except AXARemoteError as ex:
            _LOGGER.error(
                "Problem communicating with %s, reason: %s", self._axa.connection, ex
            )
        finally:
            self.start_updater()

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the window."""
        self.stop_updater()

        try:
            await self.hass.async_add_executor_job(self._axa.stop)
        except AXARemoteError as ex:
            _LOGGER.error(
                "Problem communicating with %s, reason: %s", self._axa.connection, ex
            )
        finally:
            self.start_updater()

    async def async_set_cover_position(self, **kwargs) -> None:
        """Move the cover to a specific position."""
        position = kwargs[ATTR_POSITION]
        if self.current_cover_position == position:
            return

        self.stop_updater()

        try:
            await self.hass.async_add_executor_job(self._axa.set_position, position)
        except AXARemoteError as ex:
            _LOGGER.error(
                "Problem communicating with %s, reason: %s", self._axa.connection, ex
            )
        finally:
            self.start_updater(timedelta(seconds=0.1))
