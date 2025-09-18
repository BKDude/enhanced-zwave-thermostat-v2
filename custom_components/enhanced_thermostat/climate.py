"""Climate platform for Enhanced Thermostat."""
from __future__ import annotations

import logging

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from datetime import timedelta

from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)

from .const import DOMAIN
from .schedule import Schedule
from .store import Store

_LOGGER = logging.getLogger(__name__)

# Hysteresis buffer to prevent rapid cycling
HYSTERESIS_BUFFER = 1.0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Enhanced Thermostat climate platform."""
    thermostat_entity_id = entry.data["thermostat_entity_id"]
    safety_min_temp = entry.data.get("safety_min_temp")
    safety_max_temp = entry.data.get("safety_max_temp")
    schedule_yaml = entry.data.get("schedule")

    async_add_entities([
        EnhancedThermostat(
            thermostat_entity_id,
            entry.entry_id,
            safety_min_temp,
            safety_max_temp,
            schedule_yaml,
        )
    ])


class EnhancedThermostat(ClimateEntity):
    """Representation of an Enhanced Thermostat."""

    _attr_has_entity_name = True

    def __init__(
        self,
        thermostat_entity_id: str,
        entry_id: str,
        safety_min_temp: float | None,
        safety_max_temp: float | None,
        schedule_yaml: str | None,
    ) -> None:
        """Initialize the thermostat."""
        self._thermostat_entity_id = thermostat_entity_id
        self._underlying_thermostat_state = None
        self._attr_name = "Enhanced Thermostat"
        self._attr_unique_id = entry_id
        self._attr_hvac_modes = [
            HVACMode.OFF,
            HVACMode.HEAT,
            HVACMode.COOL,
            HVACMode.HEAT_COOL,
        ]
        self._attr_supported_features = ClimateEntityFeature(0)

        self._safety_min_temp = safety_min_temp
        self._safety_max_temp = safety_max_temp
        self._safety_active = False
        self._safety_triggered_mode = None

        self._schedule = Schedule(schedule_yaml)
        self._store: Store | None = None
        self._runtime_data = {}
        self._last_hvac_action = None
        self._last_action_timestamp = None

    @property
    def temperature_unit(self) -> str | None:
        """Return the unit of measurement."""
        if self._underlying_thermostat_state:
            return self._underlying_thermostat_state.attributes.get("temperature_unit")
        return None

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        if self._underlying_thermostat_state:
            return self._underlying_thermostat_state.attributes.get("current_temperature")
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        if self._underlying_thermostat_state:
            return self._underlying_thermostat_state.attributes.get("temperature")
        return None

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return hvac operation ie. heat, cool, fan only."""
        if self._underlying_thermostat_state:
            return self._underlying_thermostat_state.state
        return HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current running hvac operation if supported."""
        if self._underlying_thermostat_state:
            return self._underlying_thermostat_state.attributes.get("hvac_action")
        return HVACAction.OFF

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        self._schedule.set_override(self._get_next_schedule_time())
        await self.hass.services.async_call(
            "climate",
            "set_temperature",
            {"entity_id": self._thermostat_entity_id, "temperature": kwargs.get(ATTR_TEMPERATURE)},
            blocking=True,
        )

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        self._schedule.set_override(self._get_next_schedule_time())
        await self.hass.services.async_call(
            "climate",
            "set_hvac_mode",
            {"entity_id": self._thermostat_entity_id, "hvac_mode": hvac_mode},
            blocking=True,
        )

    @callback
    def _async_update_underlying_thermostat(self, event) -> None:
        """Handle underlying thermostat state changes."""
        new_state = event.data.get("new_state")
        if new_state is None:
            return

        self._underlying_thermostat_state = new_state
        self._attr_supported_features = new_state.attributes.get("supported_features")

        self._async_update_runtime(new_state)
        self._async_check_safety_temp()

        self.async_write_ha_state()

    def _create_notification(self, message: str) -> None:
        """Create a persistent notification."""
        self.hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": "Enhanced Thermostat Safety Alert",
                "message": message,
                "notification_id": f"{DOMAIN}_safety_alert",
            },
        )

    def _async_check_safety_temp(self) -> None:
        """Check and apply safety temperatures."""
        if self.hvac_mode is None or self.current_temperature is None:
            return

        # If safety mode was active, check if it should be turned off
        if self._safety_active:
            # If user changed the mode, disable safety mode
            if self.hvac_mode != self._safety_triggered_mode:
                self._safety_active = False
                self._safety_triggered_mode = None
                self._create_notification("Safety mode deactivated due to manual override.")
                return

            # Check if temperature has returned to a safe level
            if self._safety_triggered_mode == HVACMode.HEAT and self.current_temperature >= self._safety_min_temp + HYSTERESIS_BUFFER:
                self.async_set_hvac_mode(HVACMode.OFF)
                self._safety_active = False
                self._safety_triggered_mode = None
                self._create_notification(f"Safety heating turned off. Temperature is now {self.current_temperature}°.")
            elif self._safety_triggered_mode == HVACMode.COOL and self.current_temperature <= self._safety_max_temp - HYSTERESIS_BUFFER:
                self.async_set_hvac_mode(HVACMode.OFF)
                self._safety_active = False
                self._safety_triggered_mode = None
                self._create_notification(f"Safety cooling turned off. Temperature is now {self.current_temperature}°.")
            return

        # If thermostat is off, check if safety temperatures are needed
        if self.hvac_mode == HVACMode.OFF:
            if self._safety_min_temp is not None and self.current_temperature < self._safety_min_temp:
                self._safety_active = True
                self._safety_triggered_mode = HVACMode.HEAT
                self.async_set_hvac_mode(HVACMode.HEAT)
                self.async_set_temperature(temperature=self._safety_min_temp)
                self._create_notification(
                    f"Safety heating activated. Current temperature is {self.current_temperature}°, target is {self._safety_min_temp}°."
                )
            elif self._safety_max_temp is not None and self.current_temperature > self._safety_max_temp:
                self._safety_active = True
                self._safety_triggered_mode = HVACMode.COOL
                self.async_set_hvac_mode(HVACMode.COOL)
                self.async_set_temperature(temperature=self._safety_max_temp)
                self._create_notification(
                    f"Safety cooling activated. Current temperature is {self.current_temperature}°, target is {self._safety_max_temp}°."
                )

    def _get_next_schedule_time(self) -> datetime:
        """Get the next scheduled event time."""
        now = datetime.now()
        # For simplicity, we'll just look ahead 24 hours.
        # A more robust solution would look further.
        return now + timedelta(days=1)

    async def _async_apply_schedule(self, now) -> None:
        """Apply the schedule."""
        setpoint = self._schedule.get_current_setpoint(now)
        if setpoint:
            target_temp = setpoint.get("temperature")
            hvac_mode = setpoint.get("hvac_mode")

            if hvac_mode and hvac_mode != self.hvac_mode:
                await self.async_set_hvac_mode(HVACMode(hvac_mode.lower()))

            if target_temp and target_temp != self.target_temperature:
                await self.async_set_temperature(temperature=target_temp)

    def _async_update_runtime(self, new_state) -> None:
        """Update the HVAC runtime."""
        now = datetime.now()
        today = now.date().isoformat()

        current_hvac_action = new_state.attributes.get("hvac_action")

        if self._last_hvac_action and self._last_action_timestamp:
            if current_hvac_action != self._last_hvac_action:
                duration = (now - self._last_action_timestamp).total_seconds() / 3600  # in hours
                if today not in self._runtime_data:
                    self._runtime_data[today] = {"heating_hours": 0, "cooling_hours": 0}

                if self._last_hvac_action == HVACAction.HEATING:
                    self._runtime_data[today]["heating_hours"] += duration
                elif self._last_hvac_action == HVACAction.COOLING:
                    self._runtime_data[today]["cooling_hours"] += duration

                self._store.async_save(self._runtime_data)

        self._last_hvac_action = current_hvac_action
        self._last_action_timestamp = now

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        # Initialize and share the store
        self._store = Store(self.hass, f"{DOMAIN}_{self.unique_id}_runtime")
        self.hass.data[DOMAIN][self.unique_id]["store"] = self._store

        # Load runtime data
        self._runtime_data = await self._store.async_load()

        # Get the initial state of the underlying thermostat
        self._underlying_thermostat_state = self.hass.states.get(self._thermostat_entity_id)
        if self._underlying_thermostat_state:
            self._attr_supported_features = self._underlying_thermostat_state.attributes.get("supported_features")

        # Subscribe to state changes
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [self._thermostat_entity_id], self._async_update_underlying_thermostat
            )
        )

        # Set up a timer to apply the schedule
        self.async_on_remove(
            async_track_time_interval(
                self.hass, self._async_apply_schedule, timedelta(minutes=1)
            )
        )
