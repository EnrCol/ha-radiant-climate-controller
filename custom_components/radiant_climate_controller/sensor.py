"""Sensor platform for Radiant Climate Controller."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import RadiantClimateCoordinator


@dataclass(frozen=True, kw_only=True)
class RadiantSensorDescription(SensorEntityDescription):
    """Description for calculated radiant sensors."""

    value_key: str


SENSORS: tuple[RadiantSensorDescription, ...] = (
    RadiantSensorDescription(
        key="zone_temperature",
        translation_key="zone_temperature",
        value_key="zone_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    RadiantSensorDescription(
        key="zone_humidity",
        translation_key="zone_humidity",
        value_key="zone_humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
    ),
    RadiantSensorDescription(
        key="dew_point",
        translation_key="dew_point",
        value_key="dew_point",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    RadiantSensorDescription(
        key="climate_state",
        translation_key="climate_state",
        value_key="climate_state",
    ),
    RadiantSensorDescription(
        key="target_requested",
        translation_key="target_requested",
        value_key="target_requested",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    RadiantSensorDescription(
        key="target_safe",
        translation_key="target_safe",
        value_key="target_safe",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    RadiantSensorDescription(
        key="target_final",
        translation_key="target_final",
        value_key="target_final",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    RadiantSensorDescription(
        key="dew_point_delta",
        translation_key="dew_point_delta",
        value_key="dew_point_delta",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    RadiantSensorDescription(
        key="season_state",
        translation_key="season_state",
        value_key="season_state",
    ),
    RadiantSensorDescription(
        key="hottest_room",
        translation_key="hottest_room",
        value_key="hottest_room",
    ),
    RadiantSensorDescription(
        key="hottest_room_temperature",
        translation_key="hottest_room_temperature",
        value_key="hottest_room_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    RadiantSensorDescription(
        key="thermal_trend_per_hour",
        translation_key="thermal_trend_per_hour",
        value_key="thermal_trend_per_hour",
        native_unit_of_measurement="°C/h",
    ),
    RadiantSensorDescription(
        key="thermal_trend_source",
        translation_key="thermal_trend_source",
        value_key="thermal_trend_source",
    ),
    RadiantSensorDescription(
        key="thermal_trend_15m_per_hour",
        translation_key="thermal_trend_15m_per_hour",
        value_key="thermal_trend_15m_per_hour",
        native_unit_of_measurement="°C/h",
    ),
    RadiantSensorDescription(
        key="thermal_trend_30m_per_hour",
        translation_key="thermal_trend_30m_per_hour",
        value_key="thermal_trend_30m_per_hour",
        native_unit_of_measurement="°C/h",
    ),
    RadiantSensorDescription(
        key="thermal_trend_60m_per_hour",
        translation_key="thermal_trend_60m_per_hour",
        value_key="thermal_trend_60m_per_hour",
        native_unit_of_measurement="°C/h",
    ),
    RadiantSensorDescription(
        key="thermal_trend_sample_count",
        translation_key="thermal_trend_sample_count",
        value_key="thermal_trend_sample_count",
    ),
    RadiantSensorDescription(
        key="critical_dew_room",
        translation_key="critical_dew_room",
        value_key="critical_dew_room",
    ),
    RadiantSensorDescription(
        key="critical_dew_zone",
        translation_key="critical_dew_zone",
        value_key="critical_dew_zone",
    ),
    RadiantSensorDescription(
        key="critical_dew_delta",
        translation_key="critical_dew_delta",
        value_key="critical_dew_delta",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    RadiantSensorDescription(
        key="critical_dew_state",
        translation_key="critical_dew_state",
        value_key="critical_dew_state",
    ),
    RadiantSensorDescription(
        key="recommended_action",
        translation_key="recommended_action",
        value_key="recommended_action",
    ),
    RadiantSensorDescription(
        key="target_reason",
        translation_key="target_reason",
        value_key="target_reason",
    ),
    RadiantSensorDescription(
        key="action_reason",
        translation_key="action_reason",
        value_key="action_reason",
    ),
    RadiantSensorDescription(
        key="critical_room_count",
        translation_key="critical_room_count",
        value_key="critical_room_count",
    ),
    RadiantSensorDescription(
        key="warning_room_count",
        translation_key="warning_room_count",
        value_key="warning_room_count",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities."""
    coordinator: RadiantClimateCoordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    async_add_entities(
        RadiantClimateSensor(coordinator, entry, description) for description in SENSORS
    )


class RadiantClimateSensor(CoordinatorEntity[RadiantClimateCoordinator], SensorEntity):
    """Calculated radiant climate sensor."""

    entity_description: RadiantSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: RadiantClimateCoordinator,
        entry: ConfigEntry,
        description: RadiantSensorDescription,
    ) -> None:
        """Initialize sensor."""
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
    def native_value(self) -> Any:
        """Return native sensor value."""
        value = self.coordinator.data.get(self.entity_description.value_key)
        if isinstance(value, float):
            return round(value, 2)
        return value
