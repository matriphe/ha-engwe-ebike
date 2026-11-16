"""Optional location based on coordinates reported by the bicycle API."""
import math
from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .sensor import numeric_attributes

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([EngweTracker(coordinator, entry)])

class EngweTracker(CoordinatorEntity, TrackerEntity):
    _attr_has_entity_name = True
    _attr_name = "Location"
    _attr_source_type = SourceType.GPS
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_location"
        self._attr_device_info = {"identifiers": {(DOMAIN, entry.entry_id)}, "name": "ENGWE E-bike", "manufacturer": "ENGWE"}

    def _coordinates(self):
        data = numeric_attributes(self.coordinator.data)
        lat, lon = data.get("latitude"), data.get("longitude")
        if lat is None or lon is None or not math.isfinite(lat) or not math.isfinite(lon):
            return None
        if not (-90 <= lat <= 90 and -180 <= lon <= 180) or (lat == 0 and lon == 0):
            return None
        return lat, lon

    @property
    def latitude(self):
        coords = self._coordinates()
        return coords[0] if coords else None

    @property
    def longitude(self):
        coords = self._coordinates()
        return coords[1] if coords else None
