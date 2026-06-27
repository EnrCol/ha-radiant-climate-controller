"""Number platform for Radiant Climate Controller."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DATA_COORDINATOR,
    DEFAULT_DEW_POINT_MARGIN,
    DEFAULT_PRECOOL_BOOST_TEMP,
    DEFAULT_PRECOOL_NORMAL_TEMP,
    DEFAULT_PRECOOL_RECOVERY_TEMP,
    DEFAULT_TARGET_BOOST,
    DEFAULT_TARGET_MAINTENANCE,
    DEFAULT_TARGET_NORMAL,
    DEFAULT_TARGET_RECOVERY,
    DEFAULT_THRESHOLD_BOOST,
    DEFAULT_THRESHOLD_NORMAL,
    DEFAULT_THRESHOLD_RECOVERY,
    DEFAULT_TREND_BOOST,
    DEFAULT_TREND_NORMAL,
    DEFAULT_TREND_RECOVERY,
    DOMAIN,
    OPT_DEW_POINT_MARGIN,
    OPT_PRECOOL_BOOST_TEMP,
    OPT_PRECOOL_NORMAL_TEMP,
    OPT_PRECOOL_RECOVERY_TEMP,
    OPT_TARGET_BOOST,
    OPT_TARGET_MAINTENANCE,
    OPT_TARGET_NORMAL,
    OPT_TARGET_RECOVERY,
    OPT_THRESHOLD_BOOST,
    OPT_THRESHOLD_NORMAL,
    OPT_THRESHOLD_RECOVERY,
    OPT_TREND_BOOST,
    OPT_TREND_NORMAL,
    OPT_TREND_RECOVERY,
)
from .coordinator import RadiantClimateCoordinator


@dataclass(frozen=True, kw_only=True)
class RadiantNumberDescription(NumberEntityDescription):
    """Description for configurable controller numbers."""

    option_key: str
    default_value: float


NUMBERS: tuple[RadiantNumberDescription, ...] = (
    RadiantNumberDescription(
        key="threshold_normal",
        translation_key="threshold_normal",
        option_key=OPT_THRESHOLD_NORMAL,
        default_value=DEFAULT_THRESHOLD_NORMAL,
        native_min_value=22.0,
        native_max_value=28.0,
        native_step=0.1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode=NumberMode.BOX,
    ),
    RadiantNumberDescription(
        key="threshold_boost",
        translation_key="threshold_boost",
        option_key=OPT_THRESHOLD_BOOST,
        default_value=DEFAULT_THRESHOLD_BOOST,
        native_min_value=22.0,
        native_max_value=29.0,
        native_step=0.1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode=NumberMode.BOX,
    ),
    RadiantNumberDescription(
        key="threshold_recovery",
        translation_key="threshold_recovery",
        option_key=OPT_THRESHOLD_RECOVERY,
        default_value=DEFAULT_THRESHOLD_RECOVERY,
        native_min_value=22.0,
        native_max_value=30.0,
        native_step=0.1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode=NumberMode.BOX,
    ),
    RadiantNumberDescription(
        key="precool_normal_temp",
        translation_key="precool_normal_temp",
        option_key=OPT_PRECOOL_NORMAL_TEMP,
        default_value=DEFAULT_PRECOOL_NORMAL_TEMP,
        native_min_value=22.0,
        native_max_value=28.0,
        native_step=0.1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode=NumberMode.BOX,
    ),
    RadiantNumberDescription(
        key="precool_boost_temp",
        translation_key="precool_boost_temp",
        option_key=OPT_PRECOOL_BOOST_TEMP,
        default_value=DEFAULT_PRECOOL_BOOST_TEMP,
        native_min_value=22.0,
        native_max_value=29.0,
        native_step=0.1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode=NumberMode.BOX,
    ),
    RadiantNumberDescription(
        key="precool_recovery_temp",
        translation_key="precool_recovery_temp",
        option_key=OPT_PRECOOL_RECOVERY_TEMP,
        default_value=DEFAULT_PRECOOL_RECOVERY_TEMP,
        native_min_value=22.0,
        native_max_value=30.0,
        native_step=0.1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode=NumberMode.BOX,
    ),
    RadiantNumberDescription(
        key="trend_normal",
        translation_key="trend_normal",
        option_key=OPT_TREND_NORMAL,
        default_value=DEFAULT_TREND_NORMAL,
        native_min_value=0.0,
        native_max_value=1.0,
        native_step=0.01,
        native_unit_of_measurement="°C/h",
        mode=NumberMode.BOX,
    ),
    RadiantNumberDescription(
        key="trend_boost",
        translation_key="trend_boost",
        option_key=OPT_TREND_BOOST,
        default_value=DEFAULT_TREND_BOOST,
        native_min_value=0.0,
        native_max_value=1.0,
        native_step=0.01,
        native_unit_of_measurement="°C/h",
        mode=NumberMode.BOX,
    ),
    RadiantNumberDescription(
        key="trend_recovery",
        translation_key="trend_recovery",
        option_key=OPT_TREND_RECOVERY,
        default_value=DEFAULT_TREND_RECOVERY,
        native_min_value=0.0,
        native_max_value=1.0,
        native_step=0.01,
        native_unit_of_measurement="°C/h",
        mode=NumberMode.BOX,
    ),
    RadiantNumberDescription(
        key="target_maintenance",
        translation_key="target_maintenance",
        option_key=OPT_TARGET_MAINTENANCE,
        default_value=DEFAULT_TARGET_MAINTENANCE,
        native_min_value=17.0,
        native_max_value=22.0,
        native_step=0.1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode=NumberMode.BOX,
    ),
    RadiantNumberDescription(
        key="target_normal",
        translation_key="target_normal",
        option_key=OPT_TARGET_NORMAL,
        default_value=DEFAULT_TARGET_NORMAL,
        native_min_value=17.0,
        native_max_value=22.0,
        native_step=0.1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode=NumberMode.BOX,
    ),
    RadiantNumberDescription(
        key="target_boost",
        translation_key="target_boost",
        option_key=OPT_TARGET_BOOST,
        default_value=DEFAULT_TARGET_BOOST,
        native_min_value=17.0,
        native_max_value=22.0,
        native_step=0.1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode=NumberMode.BOX,
    ),
    RadiantNumberDescription(
        key="target_recovery",
        translation_key="target_recovery",
        option_key=OPT_TARGET_RECOVERY,
        default_value=DEFAULT_TARGET_RECOVERY,
        native_min_value=17.0,
        native_max_value=22.0,
        native_step=0.1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode=NumberMode.BOX,
    ),
    RadiantNumberDescription(
        key="dew_point_margin",
        translation_key="dew_point_margin",
        option_key=OPT_DEW_POINT_MARGIN,
        default_value=DEFAULT_DEW_POINT_MARGIN,
        native_min_value=1.0,
        native_max_value=5.0,
        native_step=0.1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode=NumberMode.BOX,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities."""
    coordinator: RadiantClimateCoordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    async_add_entities(
        RadiantClimateNumber(coordinator, entry, description) for description in NUMBERS
    )


class RadiantClimateNumber(CoordinatorEntity[RadiantClimateCoordinator], NumberEntity):
    """Configurable controller number."""

    entity_description: RadiantNumberDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: RadiantClimateCoordinator,
        entry: ConfigEntry,
        description: RadiantNumberDescription,
    ) -> None:
        """Initialize number."""
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
    def native_value(self) -> float:
        """Return current number value."""
        return float(
            self.coordinator.setting(
                self.entity_description.option_key,
                self.entity_description.default_value,
            )
        )

    async def async_set_native_value(self, value: float) -> None:
        """Set number value."""
        await self.coordinator.async_set_option(self.entity_description.option_key, value)
