"""Sensor platform for Enhanced Thermostat."""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Enhanced Thermostat sensor platform."""
    store = hass.data[DOMAIN][entry.entry_id]["store"]
    async_add_entities([
        HeatingRuntimeSensor(entry.entry_id, store),
        CoolingRuntimeSensor(entry.entry_id, store),
    ])


class HeatingRuntimeSensor(SensorEntity):
    """Representation of a Heating Runtime Sensor."""

    _attr_has_entity_name = True
    _attr_name = "Heating Runtime Today"
    _attr_native_unit_of_measurement = "h"

    def __init__(self, entry_id: str, store) -> None:
        """Initialize the sensor."""
        self._attr_unique_id = f"{entry_id}_heating_runtime"
        self._store = store

    async def async_update(self) -> None:
        """Update the sensor."""
        data = await self._store.async_load()
        today = datetime.now().date().isoformat()
        self._attr_native_value = data.get(today, {}).get("heating_hours", 0)


class CoolingRuntimeSensor(SensorEntity):
    """Representation of a Cooling Runtime Sensor."""

    _attr_has_entity_name = True
    _attr_name = "Cooling Runtime Today"
    _attr_native_unit_of_measurement = "h"

    def __init__(self, entry_id: str, store) -> None:
        """Initialize the sensor."""
        self._attr_unique_id = f"{entry_id}_cooling_runtime"
        self._store = store

    async def async_update(self) -> None:
        """Update the sensor."""
        data = await self._store.async_load()
        today = datetime.now().date().isoformat()
        self._attr_native_value = data.get(today, {}).get("cooling_hours", 0)
