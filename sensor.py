from .sensors.status_sensor import HalachicContextStatusSensor
from .sensors.tachanun_sensor import TachanunStatusSensor

async def async_setup_entry(hass, entry, async_add_entities):
    entities = [
        HalachicContextStatusSensor(hass),
        TachanunStatusSensor(hass),
    ]
    async_add_entities(entities, update_before_add=True)
