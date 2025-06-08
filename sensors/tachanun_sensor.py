import re
from datetime import datetime
from homeassistant.components.sensor import SensorEntity

NO_TACHANUN_DATES = [
    ("15", "Shevat"), ("15", "Av"), ("9", "Av"),
    ("18", "Iyyar"), ("14", "Iyyar"),
    ("14", "Adar"), ("15", "Adar"),
    ("14", "Adar II"), ("15", "Adar II"),
    ("11", "Cheshvan"), ("28", "Iyyar"),
    ("29", "Elul"), ("9", "Tishrei"),
    ("6", "Sivan"), ("7", "Sivan")
]

NO_TACHANUN_MONTHS = ["Nisan"]
NO_TACHANUN_RANGES = [
    ("1", "Sivan", "13", "Sivan"),
    ("10", "Tishrei", "30", "Tishrei")
]

HEBREW_MONTHS = {
    "ניסן": "Nisan", "אייר": "Iyyar", "סיון": "Sivan", "תמוז": "Tammuz",
    "אב": "Av", "אלול": "Elul", "תשרי": "Tishrei", "חשוון": "Cheshvan",
    "כסלו": "Kislev", "טבת": "Tevet", "שבט": "Shevat",
    "אדר": "Adar", "אדר א": "Adar I", "אדר ב": "Adar II"
}

def parse_hebrew_date(date_str):
    """Parses 'י׳ סיון תשפ״ה' → ('10', 'Sivan')"""
    parts = date_str.split()
    if len(parts) < 2:
        return None, None
    day_heb = parts[0].replace("״", "").replace("׳", "")
    month_heb = parts[1]
    # המרה פשוטה ליום עברי (עשרות ואחדות) – נשתמש במספרים פשוטים
    hebrew_numbers = {
        'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
        'י': 10, 'כ': 20, 'ל': 30
    }
    total = 0
    for char in day_heb:
        total += hebrew_numbers.get(char, 0)
    day = str(total)
    month = HEBREW_MONTHS.get(month_heb, None)
    return day, month

def compare_hebrew_dates(day1, month1, day2, month2):
    months_order = [
        "Nisan", "Iyyar", "Sivan", "Tammuz", "Av", "Elul",
        "Tishrei", "Cheshvan", "Kislev", "Tevet", "Shevat", "Adar", "Adar I", "Adar II"
    ]
    i1 = months_order.index(month1)
    i2 = months_order.index(month2)
    if i1 != i2:
        return i1 - i2
    return int(day1) - int(day2)

class TachanunStatusSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "tachanun_status"
    _attr_unique_id = "tachanun_status"
    _attr_icon = "mdi:note-remove"
    _attr_device_class = "enum"
    _attr_options = ["yes", "no"]

    def __init__(self, hass):
        self.hass = hass
        self._attr_native_value = None
        self._attr_extra_state_attributes = {}

    async def async_update(self):
        try:
            now = datetime.now()
            hebrew_date = self.hass.states.get("sensor.jewish_calendar_date")
            holiday = self.hass.states.get("sensor.jewish_calendar_holiday")

            if not hebrew_date or hebrew_date.state in ["unknown", "unavailable"]:
                self._attr_native_value = None
                self._attr_extra_state_attributes = {"error": "jewish_calendar_date unavailable"}
                return

            day, month = parse_hebrew_date(hebrew_date.state)
            if not day or not month:
                self._attr_native_value = None
                self._attr_extra_state_attributes = {"error": "failed to parse hebrew date"}
                return

            if (day, month) in NO_TACHANUN_DATES:
                result = "no"
                reason = f"{day} {month} – יום מיוחד"
            elif month in NO_TACHANUN_MONTHS:
                result = "no"
                reason = f"חודש {month} – אין תחנון כל החודש"
            elif any(compare_hebrew_dates(day, month, start_day, start_month) >= 0 and
                     compare_hebrew_dates(day, month, end_day, end_month) <= 0
                     for (start_day, start_month, end_day, end_month) in NO_TACHANUN_RANGES):
                result = "no"
                reason = f"{day} {month} – בטווח ימים ללא תחנון"
            elif holiday and holiday.state not in ["", "unknown", "unavailable"]:
                result = "no"
                reason = f"חג: {holiday.state}"
            else:
                result = "yes"
                reason = "אין סיבה מיוחדת"

            self._attr_native_value = result
            self._attr_extra_state_attributes = {
                "hebrew_date": hebrew_date.state,
                "parsed_day": day,
                "parsed_month": month,
                "reason": reason
            }

        except Exception as e:
            self._attr_native_value = None
            self._attr_extra_state_attributes = {"error": str(e)}
