# Enhanced Z-Wave Thermostat V2 (Home Assistant Integration)

An enhanced wrapper around an existing Z-Wave (or any) `climate.*` thermostat in Home Assistant.
It adds safety protections, simple schedule automation, and daily runtime tracking sensors while
letting the original thermostat do the actual device control.

## Features

- **Safety temperature guardrails**
  - Automatically turns on HEAT if the home gets below a configured minimum when the thermostat is off.
  - Automatically turns on COOL if the home gets above a configured maximum when the thermostat is off.
  - Uses a small hysteresis buffer to avoid rapid cycling and reverts back when safe.
  - Sends a persistent notification when safety mode is activated/deactivated.

- **Simple built-in scheduling**
  - Optional YAML schedule (per day, time-based) to set target temperature and HVAC mode.
  - Manual changes temporarily override the schedule until the next scheduled event.

- **Runtime tracking sensors**
  - Sensors track daily hours of heating and cooling runtime.
    - `sensor.<integration>_heating_runtime_today`
    - `sensor.<integration>_cooling_runtime_today`

- **Config Flow (UI) setup**
  - Select your existing thermostat entity.
  - Optionally set safety min/max setpoints and a schedule in YAML.

## How it works

- The integration creates an "Enhanced Thermostat" climate entity that mirrors the selected underlying thermostat.
- If the underlying thermostat is `off` and the current temperature crosses a configured safety limit, the integration will:
  - Turn on `heat` and set temperature to `safety_min_temp`, or
  - Turn on `cool` and set temperature to `safety_max_temp`.
- A lightweight scheduler can change setpoints and modes based on a YAML schedule.
- Heating/Cooling runtime is accumulated by watching `hvac_action` changes and saved in Home Assistant's `.storage`.

## Requirements

- Home Assistant Core (recent version).
- An existing, working `climate.*` entity (e.g., a Z-Wave thermostat).

## Installation

### Option A: HACS (Custom Repository)

1. In HACS, go to "Integrations" > "…" menu > "Custom repositories".
2. Add this repository URL and select category "Integration".
3. Install "Enhanced Z-Wave Thermostat V2".
4. Restart Home Assistant.

Notes for HACS:
- This repo includes a `hacs.json` at the root and a proper `custom_components/enhanced_thermostat/` structure.
- Ensure you are using the repository URL where this code is hosted (e.g., GitHub).

### Option B: Manual install

1. Copy the `custom_components/enhanced_thermostat/` directory to your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.

## Configuration (UI)

Set up via Settings > Devices & Services > "Add Integration" > search for "Enhanced Thermostat".

- **Thermostat entity** (required): Pick your existing `climate.*` entity to wrap.
- **Safety min temp** (optional, float): Minimum temperature safeguard (start heating if below when off).
- **Safety max temp** (optional, float): Maximum temperature safeguard (start cooling if above when off).
- **Schedule** (optional, YAML): Paste a weekly schedule. See examples below.

You can change or remove options later by editing the integration entry.

## Schedule YAML format

Provide a dictionary where keys are lowercase weekday names and values are lists of events with `time`, and optional `temperature`, `hvac_mode`.
Times use 24h `HH:MM` format.

Example 1: Basic temperature setpoints (mode unchanged)

```yaml
monday:
  - time: "06:30"
    temperature: 21
  - time: "22:00"
    temperature: 18
weekday:
  - time: "07:00"
    temperature: 21
  - time: "23:00"
    temperature: 18
```

Example 2: Including HVAC mode changes

```yaml
monday:
  - time: "06:30"
    temperature: 21
    hvac_mode: heat
  - time: "22:00"
    hvac_mode: off
saturday:
  - time: "09:00"
    temperature: 20
    hvac_mode: heat_cool
```

Behavior notes:
- The schedule checks every minute for the latest event at or before "now" for that day.
- Manual changes set a temporary override until the next schedule event time.

## Created entities

- **Climate**: `climate.enhanced_thermostat` (has entity name set to "Enhanced Thermostat").
- **Sensors**:
  - Heating runtime today: `sensor.heating_runtime_today`
  - Cooling runtime today: `sensor.cooling_runtime_today`

Entity IDs will include the config entry's unique ID and may vary; use the UI to find the exact IDs.

## File structure

- `custom_components/enhanced_thermostat/__init__.py`: Integration setup and shared storage handle.
- `custom_components/enhanced_thermostat/climate.py`: Enhanced climate entity, safety checks, schedule application, runtime tracking.
- `custom_components/enhanced_thermostat/config_flow.py`: UI configuration flow.
- `custom_components/enhanced_thermostat/schedule.py`: YAML scheduler parsing and logic.
- `custom_components/enhanced_thermostat/sensor.py`: Runtime sensors (heating/cooling today).
- `custom_components/enhanced_thermostat/store.py`: Simple JSON persistence in HA `.storage`.
- `custom_components/enhanced_thermostat/manifest.json`: HA integration manifest.
- `hacs.json`: HACS metadata.

## Troubleshooting

- **Integration not found after install**: Restart Home Assistant and clear browser cache. Verify the directory is `config/custom_components/enhanced_thermostat/`.
- **HACS does not show the repo**: Ensure the repository URL is correct and the repo is public (or add it as a custom repository). Confirm `hacs.json` exists at the repo root.
- **Schedule not applying**: Check the YAML is valid and follows the format. Look for errors in the Home Assistant logs.
- **Safety not triggering**: Confirm the underlying thermostat is `off` and that current temperature crosses your safety thresholds. There is a small hysteresis buffer to prevent rapid cycling.
- **Runtime sensors show 0**: They update based on changes in `hvac_action`. Ensure the underlying thermostat reports `heating`/`cooling` `hvac_action` states.

## Privacy and storage

Runtime data is stored in Home Assistant's `.storage/` under a key derived from the integration entry ID, e.g. `.storage/enhanced_thermostat_<id>_runtime`.

## Contributing / Issues

Pull requests and issues are welcome. If reporting a bug, please include logs and your config (omit sensitive details), the underlying thermostat model, and a sample schedule if relevant.

## License

MIT
