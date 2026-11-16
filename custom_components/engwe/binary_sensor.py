"""ENGWE connectivity sensor."""
from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([EngweOnlineSensor(hass.data[DOMAIN][entry.entry_id], entry)])

class EngweOnlineSensor(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_name = 'Online'
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f'{entry.entry_id}_online'
        self._attr_device_info = {'identifiers': {(DOMAIN, entry.entry_id)}, 'name': 'ENGWE E-bike', 'manufacturer': 'ENGWE'}

    @property
    def is_on(self):
        return self.coordinator.data.get('online')
