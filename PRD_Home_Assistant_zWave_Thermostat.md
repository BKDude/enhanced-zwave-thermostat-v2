# Z-Wave Thermostat Companion for Home Assistant (HACS)

## Background

Google is discontinuing support for Gen 1 and Gen 2 Nest thermostats, removing remote control functionality. Many users are disappointed and not eligible for upgrade offers. This project aims to create a Home Assistant HACS app that replicates key Nest/Google Home features for Z-Wave thermostats like the Honeywell T6 and Ecobee.

## Goals

- Provide Nest-like climate control features for Z-Wave thermostats via Home Assistant.
- Ensure easy installation and removal via HACS.
- Deliver a clean, modular implementation suitable for AI-assisted development.

## Features

### ✅ Supported Thermostats

- Z-Wave thermostats (e.g., Honeywell T6)
- Wi-Fi thermostats (e.g., Ecobee)
- Any thermostat exposed as a `climate` entity in Home Assistant

---

### 🎛️ UI Design

- Circular temperature spinner (similar to Nest)
- Lovelace Thermostat Card or custom card
- Mode toggle (heat/cool/off)
- Safety and schedule indicators

---

### 🔥 Safety Temperature Feature

- Configurable minimum/maximum safety temperature
- Auto-activates heating/cooling when thermostat is off and threshold is crossed
- Hysteresis buffer to prevent rapid cycling
- Notification via Home Assistant when triggered

---

### 📅 Scheduling

- 7-day schedule with multiple time blocks per day
- Copy/paste schedule from one day to another
- Manual override holds until next scheduled event
- Configurable via UI or YAML (initial version)

**Example Schedule Table:**

| Day       | Schedule                          |
|-----------|-----------------------------------|
| Monday    | 6:00 – 20°C, 8:30 – OFF, 17:30 – 21°C |
| Tuesday   | *Copy from Monday*                |
| Wednesday | 6:30 – 20°C, 8:30 – OFF, 17:30 – 21°C |
| Sunday    | 7:00 – 18°C, 22:00 – 15°C          |

---

### 📊 Reporting

- Daily runtime tracking (heating/cooling)
- Graphical report (bar chart)
- Tabular report with CSV export

**Example Usage Table:**

| Date       | Heating Hours | Cooling Hours |
|------------|----------------|----------------|
| 2025-10-01 | 5.2 h          | 0.0 h          |
| 2025-10-02 | 4.5 h          | 0.0 h          |
| 2025-10-03 | 3.1 h          | 0.0 h          |

---

### 🛠️ HACS Best Practices

- Config Flow for UI-based setup
- Proper manifest and versioning
- Modular code structure
- Async programming for performance
- Clean removal and fallback to original thermostat entity

---

## Development Plan

1. **Scaffold Integration**
   - Create file structure and config flow
   - Select thermostat entity and configure safety/schedule

2. **Climate Proxy Entity**
   - Mirror real thermostat state
   - Forward control commands

3. **Safety Logic**
   - Monitor temperature
   - Trigger HVAC override
   - Send notifications

4. **Scheduling Engine**
   - Store and execute schedule
   - Handle copy/paste and manual overrides

5. **Schedule UI**
   - YAML or basic UI editor
   - Future: custom Lovelace panel

6. **Usage Tracking**
   - Monitor `hvac_action`
   - Create daily sensors
   - Export CSV

7. **Testing**
   - Simulate safety triggers
   - Validate schedule execution
   - Confirm usage tracking

8. **Documentation**
   - README with setup instructions
   - Screenshots and usage examples

---

## Comparison Table

| Feature                  | Generic Thermostat | Better Thermostat | Awesome Thermostat | This Integration |
|--------------------------|--------------------|-------------------|--------------------|------------------|
| Scheduling               | ❌                 | ❌                | ❌                 | ✅               |
| Safety Temperature       | ❌                 | ❌                | ❌                 | ✅               |
| Usage Reporting          | ❌                 | ❌                | ❌                 | ✅               |
| Window/Door Detection    | ❌                 | ✅                | ✅                 | ❌ (future)      |
| Presence Automation      | ❌                 | ❌                | ✅                 | ❌ (future)      |
| External Sensor Support  | ❌                 | ✅                | ❌                 | ❌ (manual only) |
| Multi-Thermostat Grouping| ❌                 | ✅                | ❌                 | ❌ (future)      |
| Easy Setup via UI        | ❌                 | ✅                | ❌                 | ✅               |

---

Let me know if you'd like this saved as a `.md` file or pushed to a repo.