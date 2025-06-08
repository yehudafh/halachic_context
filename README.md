# Halachic Context – Home Assistant Integration

A Home Assistant custom integration that adds sensors to determine the **halachic (Jewish law) context** of the current day, such as whether it's a regular weekday, a holiday or Shabbat night/day, and whether **Tachanun (supplicatory prayer)** should be recited today.

---

## ✡️ Features

- `halachic_context_status`: Indicates whether the current halachic time context is "weekday", "night", or "day" of Shabbat/holiday.
- `tachanun_status`: Determines if Tachanun should be said today according to standard **siddur rules**, based only on the Hebrew date.
- Multilingual support (English + Hebrew).
- Fully local, no external API.

---

## 📦 Requirements

- Home Assistant `2023.0.0` or higher
- The built-in [`jewish_calendar`](https://www.home-assistant.io/integrations/jewish_calendar/) integration must be installed and configured
  - Required entities:
    - `sensor.jewish_calendar_date`
    - `sensor.jewish_calendar_holiday`
    - Optionally: `sensor.jewish_calendar_day_in_2_days`, `sensor.jewish_calendar_month_in_2_days`

---

## 🚀 Installation

### Manual

1. Copy this repository to your Home Assistant config folder:

2. Restart Home Assistant

### HACS (optional)

1. Go to **HACS → Integrations → Custom repositories**
2. Add: as **Integration**
3. Search for "Halachic Context" and install
4. Restart Home Assistant

---

## ⚙️ Configuration

No YAML configuration needed.
Go to **Settings → Devices & Services → Add Integration**, search for "Halachic Context", and install.

---

## 🧠 Available Sensors

| Entity ID | Description |
|-----------|-------------|
| `sensor.halachic_context_status` | `"weekday"` / `"night"` / `"day"` based on holiday/Shabbat rules |
| `sensor.tachanun_status` | `"yes"` or `"no"` based on Hebrew calendar |

Each sensor includes rich attributes such as:

- Hebrew date
- Explanation of Tachanun status
- Raw values (e.g., candle lighting, havdalah)

---

## 🖼️ Example Lovelace Card

```yaml
type: entities
title: Halachic Context
entities:
- entity: sensor.halachic_context_status
- entity: sensor.tachanun_status

