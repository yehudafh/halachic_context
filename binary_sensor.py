from datetime import datetime, timedelta
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.util.dt as dt_util

SENSOR_NAME_NIGHT = "night_saturday_or_holiday"
SENSOR_NAME_DAY = "day_saturday_or_holiday"

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([
        HalachicNightSensor(hass, SENSOR_NAME_NIGHT),
        HalachicDaySensor(hass, SENSOR_NAME_DAY),
    ], True)

class HalachicSensorBase(BinarySensorEntity):
    def __init__(self, hass, name):
        self.hass = hass
        self._attr_name = name
        self._attr_unique_id = f"halachic_context_{name}"
        self._state = False
        self._attributes = {}

    @property
    def is_on(self):
        return self._state

    @property
    def state(self):
        return "on" if self._state else "off"

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def async_update(self):
        now = dt_util.now()
        today_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_midnight = today_midnight + timedelta(days=1)

        def get_dt(sensor_id):
            s = self.hass.states.get(sensor_id)
            try:
                return dt_util.parse_datetime(s.state).astimezone() if s and s.state else None
            except:
                return None

        def get_binary(sensor_id):
            s = self.hass.states.get(sensor_id)
            return s.state == "on" if s else False

        candle_lighting = get_dt("sensor.jewish_calendar_upcoming_candle_lighting")
        havdalah = get_dt("sensor.jewish_calendar_upcoming_havdalah")
        shkia = get_dt("sensor.jewish_calendar_shkia")
        issur_melacha = get_binary("binary_sensor.jewish_calendar_issur_melacha_in_effect")

        self._attributes = {
            "now": now,
            "candle_lighting": candle_lighting,
            "havdalah": havdalah,
            "shkia": shkia,
            "issur_melacha": issur_melacha,
        }

        self.evaluate_state(now, today_midnight, tomorrow_midnight, candle_lighting, havdalah, shkia, issur_melacha)

class HalachicNightSensor(HalachicSensorBase):
    def evaluate_state(self, now, midnight, tomorrow_midnight, candle_lighting, havdalah, shkia, issur_melacha):
        if not issur_melacha or candle_lighting is None:
            self._state = False
            return

        start = candle_lighting - timedelta(minutes=20)
        end = midnight + timedelta(hours=12)

        is_holiday_continuing = havdalah is not None and havdalah > tomorrow_midnight
        self._attributes["holiday_continues_tomorrow"] = is_holiday_continuing

        self._state = start <= now < end and is_holiday_continuing

class HalachicDaySensor(HalachicSensorBase):
    def evaluate_state(self, now, midnight, tomorrow_midnight, candle_lighting, havdalah, shkia, issur_melacha):
        if not issur_melacha:
            self._state = False
            return

        noon = midnight + timedelta(hours=12)

        if candle_lighting and candle_lighting < tomorrow_midnight:
            end = candle_lighting - timedelta(minutes=20)
        else:
            end = shkia + timedelta(minutes=50) if shkia else tomorrow_midnight

        self._attributes["day_start"] = noon
        self._attributes["day_end"] = end

        self._state = noon <= now < end
