"""Data coordinator for Radiant Climate Controller."""

from __future__ import annotations

from datetime import timedelta
import logging
import math
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_HUMIDITY_ENTITIES,
    CONF_SEASON_ENTITY,
    CONF_TEMPERATURE_ENTITIES,
    DEFAULT_DEW_POINT_MARGIN,
    DEFAULT_SCAN_INTERVAL_SECONDS,
    DEFAULT_TARGET_BOOST,
    DEFAULT_TARGET_MAINTENANCE,
    DEFAULT_TARGET_NORMAL,
    DEFAULT_TARGET_RECOVERY,
    DEFAULT_THRESHOLD_BOOST,
    DEFAULT_THRESHOLD_NORMAL,
    DEFAULT_THRESHOLD_RECOVERY,
    DOMAIN,
    STATE_BOOST,
    STATE_MAINTENANCE,
    STATE_NORMAL,
    STATE_RECOVERY,
    STATE_UNKNOWN,
)

_LOGGER = logging.getLogger(__name__)


def _split_entities(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def _as_float(value: Any) -> float | None:
    try:
        if value in (None, "unknown", "unavailable"):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _dew_point_celsius(temperature: float, humidity: float) -> float | None:
    if humidity <= 0:
        return None
    a = 17.62
    b = 243.12
    gamma = ((a * temperature) / (b + temperature)) + math.log(humidity / 100.0)
    return (b * gamma) / (a - gamma)


class RadiantClimateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL_SECONDS),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        return self._calculate()

    def _temperature_from_entity(self, entity_id: str) -> float | None:
        state = self.hass.states.get(entity_id)
        if state is None:
            return None
        current_temperature = _as_float(state.attributes.get("current_temperature"))
        if current_temperature is not None:
            return current_temperature
        return _as_float(state.state)

    def _humidity_from_entity(self, entity_id: str) -> float | None:
        state = self.hass.states.get(entity_id)
        if state is None:
            return None
        return _as_float(state.state)

    def _calculate(self) -> dict[str, Any]:
        data = self.entry.data

        temperature_entities = _split_entities(data.get(CONF_TEMPERATURE_ENTITIES))
        humidity_entities = _split_entities(data.get(CONF_HUMIDITY_ENTITIES))
        season_entity = data.get(CONF_SEASON_ENTITY)

        temperatures = [
            value
            for entity_id in temperature_entities
            if (value := self._temperature_from_entity(entity_id)) is not None
        ]
        humidities = [
            value
            for entity_id in humidity_entities
            if (value := self._humidity_from_entity(entity_id)) is not None
        ]

        zone_temperature = max(temperatures) if temperatures else None
        zone_humidity = max(humidities) if humidities else None
        dew_point = (
            _dew_point_celsius(zone_temperature, zone_humidity)
            if zone_temperature is not None and zone_humidity is not None
            else None
        )

        if zone_temperature is None:
            climate_state = STATE_UNKNOWN
        elif zone_temperature >= DEFAULT_THRESHOLD_RECOVERY:
            climate_state = STATE_RECOVERY
        elif zone_temperature >= DEFAULT_THRESHOLD_BOOST:
            climate_state = STATE_BOOST
        elif zone_temperature >= DEFAULT_THRESHOLD_NORMAL:
            climate_state = STATE_NORMAL
        else:
            climate_state = STATE_MAINTENANCE

        if climate_state == STATE_RECOVERY:
            target_requested = DEFAULT_TARGET_RECOVERY
        elif climate_state == STATE_BOOST:
            target_requested = DEFAULT_TARGET_BOOST
        elif climate_state == STATE_NORMAL:
            target_requested = DEFAULT_TARGET_NORMAL
        else:
            target_requested = DEFAULT_TARGET_MAINTENANCE

        target_safe = dew_point + DEFAULT_DEW_POINT_MARGIN if dew_point is not None else 19.0

        season_state_obj = self.hass.states.get(season_entity) if season_entity else None
        season_state = season_state_obj.state if season_state_obj is not None else None
        summer_enabled = season_state == "Estate"
        target_final = max(target_requested, target_safe) if summer_enabled else None

        return {
            "zone_temperature": zone_temperature,
            "zone_humidity": zone_humidity,
            "dew_point": dew_point,
            "climate_state": climate_state,
            "target_requested": target_requested,
            "target_safe": target_safe,
            "target_final": target_final,
            "dew_point_delta": target_final - dew_point
            if target_final is not None and dew_point is not None
            else None,
            "summer_enabled": summer_enabled,
            "season_state": season_state,
        }
