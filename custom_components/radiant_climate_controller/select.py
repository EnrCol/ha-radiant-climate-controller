"""Select platform for Radiant Climate Controller."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DATA_COORDINATOR,
    DOMAIN,
    MANUAL_AUTO,
    MANUAL_OPTIONS,
    OPT_MANUAL_STATE,
)
from .coordinator import RadiantClimateCoordinator


@dataclass(frozen=True, kw_only=True)
class RadiantSelectDescription(SelectEntityDescription):
    """Description for controller select entities."""

    option_key: str
    default_value: str


SELECTS: tuple[RadiantSelectDescription, ...] = (
    RadiantSelectDescription(
        key="manual_state",
        translation_key="manual_state",
        option_key=OPT_MANUAL_STATE,
        default_value=MANUAL_AUTO,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select entities."""
    coordinator: RadiantClimateCoordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    async_add_entities(
        RadiantClimateSelect(coordinator, entry, description) for description in SELECTS
    )


class RadiantClimateSelect(CoordinatorEntity[RadiantClimateCoordinator], SelectEntity):
    """Configurable controller select."""

    entity_description: RadiantSelectDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: RadiantClimateCoordinator,
        entry: ConfigEntry,
        description: RadiantSelectDescription,
    ) -> None:
        """Initialize select."""
        super().__init__(coordinator)
        self._entry = entry
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "EnrCol",
            "model": "Radiant Climate Controller",
        }

    @property
    def options(self) -> list[str]:
        """Return available options."""
        return list(MANUAL_OPTIONS)

    @property
    def current_option(self) -> str:
        """Return selected option."""
        return str(
            self.coordinator.setting(
                self.entity_description.option_key,
                self.entity_description.default_value,
            )
        )

    async def async_select_option(self, option: str) -> None:
        """Select option."""
        if option not in self.options:
            return
        await self.coordinator.async_set_option(self.entity_description.option_key, option)
