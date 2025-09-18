"""Scheduling logic for the Enhanced Thermostat."""
from __future__ import annotations

import logging
from datetime import time, datetime

import yaml
from homeassistant.components.climate import HVACMode

_LOGGER = logging.getLogger(__name__)


class Schedule:
    """Manages the thermostat schedule."""

    def __init__(self, schedule_yaml: str | None) -> None:
        """Initialize the schedule."""
        self._schedule = self._parse_schedule(schedule_yaml)
        self._override_active = False
        self._override_until = None

    def _parse_schedule(self, schedule_yaml: str | None) -> dict[str, list] | None:
        """Parse the YAML schedule."""
        if not schedule_yaml:
            return None

        try:
            schedule = yaml.safe_load(schedule_yaml)
            # Basic validation
            if not isinstance(schedule, dict):
                _LOGGER.error("Schedule must be a dictionary.")
                return None

            for day, events in schedule.items():
                if not isinstance(events, list):
                    _LOGGER.error(f"Events for {day} must be a list.")
                    return None
                for event in events:
                    if not isinstance(event, dict) or "time" not in event:
                        _LOGGER.error(f"Invalid event in {day}: {event}")
                        return None
            return schedule
        except yaml.YAMLError as e:
            _LOGGER.error(f"Error parsing schedule YAML: {e}")
            return None

    def get_current_setpoint(self, now: datetime) -> dict | None:
        """Get the current scheduled setpoint."""
        if not self._schedule:
            return None

        if self._override_active and self._override_until and now < self._override_until:
            return None  # Override is active

        self._override_active = False
        self._override_until = None

        day_name = now.strftime("%A").lower()
        if day_name not in self._schedule:
            return None

        events = sorted(self._schedule[day_name], key=lambda x: self._parse_time(x["time"]))
        current_event = None
        for event in events:
            if self._parse_time(event["time"]) <= now.time():
                current_event = event
            else:
                break

        return current_event

    def set_override(self, until: datetime) -> None:
        """Set a manual override."""
        self._override_active = True
        self._override_until = until

    def _parse_time(self, time_str: str) -> time:
        """Parse a time string."""
        return datetime.strptime(time_str, "%H:%M").time()
