"""Sensor entities for observed ENGWE bicycle attributes."""
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfLength, UnitOfSpeed, UnitOfTime
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

# Code, display name, unit, device class, conversion from the reported raw unit.
SENSORS = {
    "vehicleBatterySOC": ("Battery", PERCENTAGE, SensorDeviceClass.BATTERY, 1),
    "vehicleBatterySOH": ("Battery health", PERCENTAGE, None, 1),
    "iotBatterySOC": ("IoT battery", PERCENTAGE, SensorDeviceClass.BATTERY, 1),
    "totalRideTime": ("Total ride duration", UnitOfTime.MINUTES, SensorDeviceClass.DURATION, 1),
    "totalMileages": ("Total distance", UnitOfLength.KILOMETERS, SensorDeviceClass.DISTANCE, 0.1),
    "currentSpeed": ("Current speed", UnitOfSpeed.KILOMETERS_PER_HOUR, SensorDeviceClass.SPEED, 0.1),
    "maxSpeed": ("Maximum speed", UnitOfSpeed.KILOMETERS_PER_HOUR, SensorDeviceClass.SPEED, 0.1),
    "avgSpeed": ("Average speed", UnitOfSpeed.KILOMETERS_PER_HOUR, SensorDeviceClass.SPEED, 0.1),
    "pedallingRate": ("Cadence", "rpm", None, 1),
    "maxPedallingRate": ("Maximum cadence", "rpm", None, 1),
}


ICONS = {
    "vehicleBatterySOH": "mdi:battery-heart-variant",
    "pedallingRate": "mdi:bike",
    "maxPedallingRate": "mdi:bike-fast",
    "totalMileages": "mdi:map-marker-distance",
}


def numeric_attributes(data):
    """Extract numeric values while preserving missing data as unknown."""
    result = {}
    for item in data.get("attributes", []):
        if not isinstance(item, dict):
            continue
        meta = item.get("attrDict") or {}
        value = item.get("attrLatestValue") or {}
        code = meta.get("attributeCode")
        if not isinstance(code, str):
            continue
        number = next((value.get(k) for k in ("longValue", "doubleValue") if value.get(k) is not None), None)
        if isinstance(number, (int, float)) and not isinstance(number, bool):
            result[code] = number
    return result


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(EngweSensor(coordinator, entry, code, definition) for code, definition in SENSORS.items())


class EngweSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, entry, code, definition):
        super().__init__(coordinator)
        name, unit, device_class, self.factor = definition
        self.code = code
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        if code in ICONS:
            self._attr_icon = ICONS[code]
        self._attr_unique_id = f"{entry.entry_id}_{code}"
        self._attr_device_info = {"identifiers": {(DOMAIN, entry.entry_id)}, "name": "ENGWE E-bike", "manufacturer": "ENGWE"}

    @property
    def native_value(self):
        value = numeric_attributes(self.coordinator.data).get(self.code)
        return value * self.factor if value is not None else None

    @property
    def extra_state_attributes(self):
        """Expose the API value and unit separately from the HA state."""
        raw = numeric_attributes(self.coordinator.data).get(self.code)
        unit = None
        for item in self.coordinator.data.get("attributes", []):
            if not isinstance(item, dict):
                continue
            metadata = item.get("attrDict") or {}
            if metadata.get("attributeCode") == self.code:
                unit = metadata.get("attributeValueUnit")
                break
        return {
            "api_attribute_code": self.code,
            "api_raw_value": raw,
            "api_raw_unit": unit,
            "api_scale_factor": self.factor,
        }
