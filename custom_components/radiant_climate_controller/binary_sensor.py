"""Binary sensor platform for Radiant Climate Controller."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import RadiantClimateCoordinator


@dataclass(frozen=True, kw_only=True)
class RadiantBinarySensorDescription(BinarySensorEntityDescription):
    """Description for calculated radiant binary sensors."""

    value_key: str


BINARY_SENSORS: tuple[RadiantBinarySensorDescription, ...] = (
    RadiantBinarySensorDescription(
        key="target_commandable",
        translation_key="target_commandable",
        value_key="target_commandable",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor entities."""
    coordinator: RadiantClimateCoordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    async_add_entities(
        RadiantClimateBinarySensor(coordinator, entry, description)
        for description in BINARY_SENSORS
    )


class RadiantClimateBinarySensor(CoordinatorEntity[RadiantClimateCoordinator], BinarySensorEntity):
    """Calculated radiant climate binary sensor."""

    entity_description: RadiantBinarySensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: RadiantClimateCoordinator,
        entry: ConfigEntry,
        description: RadiantBinarySensorDescription,
    ) -> None:
        """Initialize binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "EnrCol",
            "model": "Radiant Climate Controller",
        }

    @property
    def is_on(self) -> bool | None:
        """Return binary sensor state."""
        value = self.coordinator.data.get(self.entity_description.value_key)
        if value is None:
            return None
        return bool(value)
