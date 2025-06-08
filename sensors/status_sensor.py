# sensors/status_sensor.py

from datetime import datetime, timedelta
from homeassistant.components.sensor import SensorEntity

class HalachicContextStatusSensor(SensorEntity):
    """Sensor that determines the current halachic context: weekday, night or day of a holiday/shabbat."""

    _attr_has_entity_name = True
    _attr_translation_key = "halachic_context_status"
    _attr_unique_id = "halachic_context_status"
    _attr_icon = "mdi:candle"
    _attr_device_class = "enum"
    _attr_options = ["night", "day", "weekday"]

    def __init__(self, hass):
        self.hass = hass
        self._attr_native_value = None
        self._attr_extra_state_attributes = {}

    async def async_update(self):
        """Update the sensor state based on current time and halachic conditions."""
        try:
            now = datetime.now()

            candle = self.hass.states.get("sensor.jewish_calendar_upcoming_candle_lighting")
            havdalah = self.hass.states.get("sensor.jewish_calendar_upcoming_havdalah")
            issur_melacha = self.hass.states.is_state("binary_sensor.jewish_calendar_issur_melacha_in_effect", "on")

            candle_str = candle.state if candle and candle.state not in ["unknown", "unavailable"] else None
            havdalah_str = havdalah.state if havdalah and havdalah.state not in ["unknown", "unavailable"] else None

            if not candle_str or not havdalah_str:
                self._attr_native_value = None
                self._attr_extra_state_attributes = {
                    "now": now.isoformat(),
                    "candle_lighting_raw": candle.state if candle else "missing",
                    "havdalah_raw": havdalah.state if havdalah else "missing",
                    "issur_melacha": issur_melacha
                }
                return

            candle_dt = datetime.fromisoformat(candle_str.replace("Z", "+00:00"))
            havdalah_dt = datetime.fromisoformat(havdalah_str.replace("Z", "+00:00"))

            candle_midnight = candle_dt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            havdalah_midnight = havdalah_dt.replace(hour=0, minute=0, second=0, microsecond=0)

            if issur_melacha:
                if now < candle_midnight:
                    value = "night"
                elif now < havdalah_dt and now >= candle_midnight:
                    value = "day"
                elif candle_midnight.date() == havdalah_midnight.date() and now >= havdalah_dt:
                    value = "weekday"
                else:
                    if now < havdalah_midnight:
                        value = "night"
                    elif now < havdalah_dt:
                        value = "day"
                    else:
                        value = "weekday"
            else:
                value = "weekday"

            self._attr_native_value = value
            self._attr_extra_state_attributes = {
                "now": now.isoformat(),
                "candle_lighting_raw": candle_str,
                "havdalah_raw": havdalah_str,
                "issur_melacha": issur_melacha,
                "candle_midnight": candle_midnight.isoformat(),
                "havdalah_midnight": havdalah_midnight.isoformat()
            }

        except Exception as e:
            self._attr_native_value = None
            self._attr_extra_state_attributes = {"error": str(e)}
