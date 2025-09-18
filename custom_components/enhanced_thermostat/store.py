"""Handles data storage for the Enhanced Thermostat integration."""
from __future__ import annotations

import json
import logging

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class Store:
    """Manages the persistence of integration data."""

    def __init__(self, hass: HomeAssistant, storage_key: str) -> None:
        """Initialize the store."""
        self._hass = hass
        self._storage_path = hass.config.path(f".storage/{storage_key}")
        self._data = {}

    async def async_load(self) -> dict:
        """Load data from the store."""
        try:
            with open(self._storage_path, "r") as f:
                self._data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            _LOGGER.debug("No existing storage found, starting fresh.")
            self._data = {}
        return self._data

    async def async_save(self, data: dict) -> None:
        """Save data to the store."""
        self._data = data
        try:
            with open(self._storage_path, "w") as f:
                json.dump(self._data, f)
        except IOError as e:
            _LOGGER.error(f"Failed to save data to store: {e}")
