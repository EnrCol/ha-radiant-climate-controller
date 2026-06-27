"""Data coordinator for Radiant Climate Controller."""

from __future__ import annotations

from datetime import timedelta
import logging
import math
import time
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    ACTION_ACS_BLOCK,
    ACTION_ACTIVE_COOLING,
    ACTION_DEHUMIDIFY,
    ACTION_DISABLED,
    ACTION_DOOR_STANDBY,
    ACTION_GLOBAL_PROTECTION,
    ACTION_IDLE,
    ACTION_LOCAL_PROTECTION,
    ACTION_PRECOOL,
    CONF_SEASON_ENTITY,
    DEFAULT_DEW_POINT_MARGIN,
    DEFAULT_PRECOOL_BOOST_TEMP,
    DEFAULT_PRECOOL_NORMAL_TEMP,
    DEFAULT_PRECOOL_RECOVERY_TEMP,
    DEFAULT_SCAN_INTERVAL_SECONDS,
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
    ENTITY_ACS_BLOCK,
    ENTITY_DEW_POINT_MARGIN,
    ENTITY_DEW_POINT_MAX_HOUSE,
    ENTITY_STANDBY_ATTIVO,
    ENTITY_STANDBY_PORTE,
    ENTITY_STANDBY_RUGIADA,
    MANUAL_AUTO,
    OPT_DEW_POINT_MARGIN,
    OPT_MANUAL_STATE,
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
    STATE_BOOST,
    STATE_MAINTENANCE,
    STATE_NORMAL,
    STATE_RECOVERY,
    STATE_UNKNOWN,
)
from .rooms import ROOMS, ZONE_DEHUMIDIFIERS

_LOGGER = logging.getLogger(__name__)


def _as_float(value: Any) -> float | None:
    """Convert a Home Assistant value to float."""
    try:
        if value in (None, "unknown", "unavailable"):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _dew_point_celsius(temperature: float, humidity: float) -> float | None:
    """Calculate dew point with the Magnus formula."""
    if humidity <= 0:
        return None
    a = 17.62
    b = 243.12
    gamma = ((a * temperature) / (b + temperature)) + math.log(humidity / 100.0)
    return (b * gamma) / (a - gamma)


class RadiantClimateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that calculates radiant climate values from HA states."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        self.entry = entry
        self._last_temperature: float | None = None
        self._last_timestamp: float | None = None
        self._last_trend: float | None = None
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL_SECONDS),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update calculated data."""
        return self._calculate()

    def setting(self, key: str, default: Any) -> Any:
        """Return an integration option with fallback."""
        return self.entry.options.get(key, default)

    async def async_set_option(self, key: str, value: Any) -> None:
        """Persist one option and refresh calculated data."""
        options = dict(self.entry.options)
        options[key] = value
        self.hass.config_entries.async_update_entry(self.entry, options=options)
        await self.async_request_refresh()

    def _state(self, entity_id: str | None) -> str | None:
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        return state.state if state is not None else None

    def _is_on(self, entity_id: str | None) -> bool:
        return self._state(entity_id) == "on"

    def _float_state(self, entity_id: str | None) -> float | None:
        return _as_float(self._state(entity_id))

    def _safety_margin(self) -> float:
        """Return dew point safety margin.

        If the integration number is changed, it overrides the existing HA helper.
        Otherwise the existing HA helper remains the source of truth.
        """
        if OPT_DEW_POINT_MARGIN in self.entry.options:
            return float(self.entry.options[OPT_DEW_POINT_MARGIN])
        return self._float_state(ENTITY_DEW_POINT_MARGIN) or DEFAULT_DEW_POINT_MARGIN

    def _target_for_state(self, state: str) -> float:
        """Return configured target supply temperature for a radiant state."""
        if state == STATE_RECOVERY:
            return float(self.setting(OPT_TARGET_RECOVERY, DEFAULT_TARGET_RECOVERY))
        if state == STATE_BOOST:
            return float(self.setting(OPT_TARGET_BOOST, DEFAULT_TARGET_BOOST))
        if state == STATE_NORMAL:
            return float(self.setting(OPT_TARGET_NORMAL, DEFAULT_TARGET_NORMAL))
        return float(self.setting(OPT_TARGET_MAINTENANCE, DEFAULT_TARGET_MAINTENANCE))

    def _calculate_rooms(self, safety_margin: float) -> dict[str, dict[str, Any]]:
        rooms: dict[str, dict[str, Any]] = {}
        for key, cfg in ROOMS.items():
            temperature = self._float_state(cfg.get("temperature"))
            humidity = self._float_state(cfg.get("humidity"))
            dew_point = self._float_state(cfg.get("dew_point"))
            if dew_point is None and temperature is not None and humidity is not None:
                dew_point = _dew_point_celsius(temperature, humidity)

            dew_delta = None
            if temperature is not None and dew_point is not None:
                dew_delta = temperature - dew_point

            safety_boolean = self._is_on(cfg.get("safety_boolean"))
            if dew_delta is None:
                risk = "unknown"
            elif safety_boolean or dew_delta <= safety_margin:
                risk = "critico"
            elif dew_delta <= safety_margin + 1.0:
                risk = "attenzione"
            else:
                risk = "ok"

            rooms[key] = {
                "key": key,
                "name": cfg.get("name", key),
                "zone": cfg.get("zone"),
                "temperature": temperature,
                "humidity": humidity,
                "dew_point": dew_point,
                "dew_delta": dew_delta,
                "risk": risk,
                "climate": cfg.get("climate"),
                "safety_boolean": safety_boolean,
            }
        return rooms

    def _calculate_zone_states(self) -> dict[str, dict[str, Any]]:
        zones: dict[str, dict[str, Any]] = {}
        for key, cfg in ZONE_DEHUMIDIFIERS.items():
            zones[key] = {
                "key": key,
                "name": cfg.get("name", key),
                "request": self._is_on(cfg.get("request")),
                "consent": self._is_on(cfg.get("consent")),
                "average_temperature": self._float_state(cfg.get("average_temperature")),
                "average_humidity": self._float_state(cfg.get("average_humidity")),
                "humidity_threshold": self._float_state(cfg.get("humidity_threshold")),
            }
        return zones

    def _trend_per_hour(self, current_temperature: float | None) -> float | None:
        now_ts = time.monotonic()
        if current_temperature is None:
            return self._last_trend
        if self._last_temperature is None or self._last_timestamp is None:
            self._last_temperature = current_temperature
            self._last_timestamp = now_ts
            return self._last_trend
        elapsed = now_ts - self._last_timestamp
        if elapsed < 60:
            return self._last_trend
        trend = (current_temperature - self._last_temperature) / (elapsed / 3600.0)
        self._last_temperature = current_temperature
        self._last_timestamp = now_ts
        self._last_trend = trend
        return trend

    def _comfort_state_and_target(
        self, hottest_temp: float | None, trend: float | None
    ) -> tuple[str, float, str, bool]:
        manual_state = self.setting(OPT_MANUAL_STATE, MANUAL_AUTO)
        if manual_state != MANUAL_AUTO:
            target = self._target_for_state(manual_state)
            return manual_state, target, f"stato radiante forzato manualmente: {manual_state}", False

        if hottest_temp is None:
            return (
                STATE_UNKNOWN,
                self._target_for_state(STATE_MAINTENANCE),
                "temperatura massima casa non disponibile",
                False,
            )

        if trend is None:
            trend_value = 0.0
            trend_text = "trend non ancora disponibile"
        else:
            trend_value = trend
            trend_text = f"trend {trend_value:.2f}°C/h"

        threshold_recovery = float(self.setting(OPT_THRESHOLD_RECOVERY, DEFAULT_THRESHOLD_RECOVERY))
        threshold_boost = float(self.setting(OPT_THRESHOLD_BOOST, DEFAULT_THRESHOLD_BOOST))
        threshold_normal = float(self.setting(OPT_THRESHOLD_NORMAL, DEFAULT_THRESHOLD_NORMAL))
        precool_recovery = float(self.setting(OPT_PRECOOL_RECOVERY_TEMP, DEFAULT_PRECOOL_RECOVERY_TEMP))
        precool_boost = float(self.setting(OPT_PRECOOL_BOOST_TEMP, DEFAULT_PRECOOL_BOOST_TEMP))
        precool_normal = float(self.setting(OPT_PRECOOL_NORMAL_TEMP, DEFAULT_PRECOOL_NORMAL_TEMP))
        trend_recovery = float(self.setting(OPT_TREND_RECOVERY, DEFAULT_TREND_RECOVERY))
        trend_boost = float(self.setting(OPT_TREND_BOOST, DEFAULT_TREND_BOOST))
        trend_normal = float(self.setting(OPT_TREND_NORMAL, DEFAULT_TREND_NORMAL))

        if hottest_temp >= threshold_recovery:
            return (
                STATE_RECOVERY,
                self._target_for_state(STATE_RECOVERY),
                f"recupero: temperatura {hottest_temp:.1f}°C, {trend_text}",
                False,
            )
        if hottest_temp >= precool_recovery and trend_value >= trend_recovery:
            return (
                STATE_RECOVERY,
                self._target_for_state(STATE_RECOVERY),
                f"recupero anticipato: temperatura {hottest_temp:.1f}°C, {trend_text}",
                True,
            )

        if hottest_temp >= threshold_boost:
            return (
                STATE_BOOST,
                self._target_for_state(STATE_BOOST),
                f"spinto: temperatura {hottest_temp:.1f}°C, {trend_text}",
                False,
            )
        if hottest_temp >= precool_boost and trend_value >= trend_boost:
            return (
                STATE_BOOST,
                self._target_for_state(STATE_BOOST),
                f"spinto anticipato: temperatura {hottest_temp:.1f}°C, {trend_text}",
                True,
            )

        if hottest_temp >= threshold_normal:
            return (
                STATE_NORMAL,
                self._target_for_state(STATE_NORMAL),
                f"normale: temperatura {hottest_temp:.1f}°C, {trend_text}",
                False,
            )
        if hottest_temp >= precool_normal and trend_value >= trend_normal:
            return (
                STATE_NORMAL,
                self._target_for_state(STATE_NORMAL),
                f"normale anticipato: temperatura {hottest_temp:.1f}°C, {trend_text}",
                True,
            )

        return (
            STATE_MAINTENANCE,
            self._target_for_state(STATE_MAINTENANCE),
            f"mantenimento: temperatura {hottest_temp:.1f}°C, {trend_text}",
            False,
        )

    def _calculate(self) -> dict[str, Any]:
        data = self.entry.data
        season_entity = data.get(CONF_SEASON_ENTITY)
        season_state = self._state(season_entity)
        summer_enabled = season_state == "Estate"

        safety_margin = self._safety_margin()
        rooms = self._calculate_rooms(safety_margin)
        zones = self._calculate_zone_states()

        valid_temperatures = [
            room["temperature"] for room in rooms.values() if room["temperature"] is not None
        ]
        valid_humidities = [
            room["humidity"] for room in rooms.values() if room["humidity"] is not None
        ]
        valid_dew_points = [
            room["dew_point"] for room in rooms.values() if room["dew_point"] is not None
        ]
        valid_deltas = [
            room for room in rooms.values() if room["dew_delta"] is not None
        ]

        hottest_room = (
            max(
                rooms.values(),
                key=lambda item: item["temperature"] if item["temperature"] is not None else -999,
            )
            if valid_temperatures
            else None
        )
        nearest_dew_room = min(valid_deltas, key=lambda item: item["dew_delta"]) if valid_deltas else None

        zone_temperature = max(valid_temperatures) if valid_temperatures else None
        zone_humidity = max(valid_humidities) if valid_humidities else None
        house_dew_point = self._float_state(ENTITY_DEW_POINT_MAX_HOUSE)
        if house_dew_point is None and valid_dew_points:
            house_dew_point = max(valid_dew_points)

        trend = self._trend_per_hour(zone_temperature)
        climate_state, target_requested, target_reason, predictive_trigger = self._comfort_state_and_target(
            zone_temperature, trend
        )

        target_safe = house_dew_point + safety_margin if house_dew_point is not None else 19.0
        target_final = max(target_requested, target_safe) if summer_enabled else None

        acs_block = self._is_on(ENTITY_ACS_BLOCK)
        standby_porte = self._is_on(ENTITY_STANDBY_PORTE)
        standby_rugiada = self._is_on(ENTITY_STANDBY_RUGIADA)
        standby_attivo = self._is_on(ENTITY_STANDBY_ATTIVO)

        critical_rooms = [room for room in rooms.values() if room["risk"] == "critico"]
        warning_rooms = [room for room in rooms.values() if room["risk"] == "attenzione"]
        critical_zones = {room["zone"] for room in critical_rooms if room.get("zone")}

        recommended_action = ACTION_IDLE
        if not summer_enabled:
            recommended_action = ACTION_DISABLED
        elif acs_block:
            recommended_action = ACTION_ACS_BLOCK
        elif standby_porte:
            recommended_action = ACTION_DOOR_STANDBY
        elif len(critical_rooms) >= 2 or len(critical_zones) >= 2 or standby_rugiada:
            recommended_action = ACTION_GLOBAL_PROTECTION
        elif nearest_dew_room is not None and nearest_dew_room["risk"] == "critico":
            zone = nearest_dew_room.get("zone")
            if zone and not zones.get(zone, {}).get("request"):
                recommended_action = ACTION_DEHUMIDIFY
            else:
                recommended_action = ACTION_LOCAL_PROTECTION
        elif climate_state in (STATE_NORMAL, STATE_BOOST, STATE_RECOVERY):
            recommended_action = ACTION_PRECOOL if predictive_trigger else ACTION_ACTIVE_COOLING

        if nearest_dew_room is not None:
            dew_delta = nearest_dew_room["dew_delta"]
            nearest_dew_room_name = nearest_dew_room["name"]
            nearest_dew_room_zone = nearest_dew_room["zone"]
            nearest_dew_state = nearest_dew_room["risk"]
        else:
            dew_delta = None
            nearest_dew_room_name = None
            nearest_dew_room_zone = None
            nearest_dew_state = "unknown"

        action_reason = target_reason
        if recommended_action == ACTION_GLOBAL_PROTECTION:
            action_reason = "rischio rugiada diffuso o standby rugiada attivo: protezione globale mandata"
        elif recommended_action == ACTION_LOCAL_PROTECTION and nearest_dew_room_name:
            action_reason = f"rischio rugiada localizzato in {nearest_dew_room_name}: preferire azione locale/testina"
        elif recommended_action == ACTION_DEHUMIDIFY and nearest_dew_room_zone:
            action_reason = f"rischio rugiada in zona {nearest_dew_room_zone}: priorità deumidificazione zona"
        elif recommended_action == ACTION_ACS_BLOCK:
            action_reason = "ACS attiva o blocco miscelatrice: non usare il target come comando utile"
        elif recommended_action == ACTION_DOOR_STANDBY:
            action_reason = "porte/finestre in standby: evitare raffrescamento attivo"
        elif recommended_action == ACTION_DISABLED:
            action_reason = "modalità stagionale diversa da Estate"
        elif recommended_action == ACTION_ACTIVE_COOLING:
            action_reason = f"raffrescamento attivo: {target_reason}"
        elif recommended_action == ACTION_PRECOOL:
            action_reason = f"anticipo raffrescamento: {target_reason}"

        return {
            "zone_temperature": zone_temperature,
            "zone_humidity": zone_humidity,
            "dew_point": house_dew_point,
            "climate_state": climate_state,
            "target_requested": target_requested,
            "target_safe": target_safe,
            "target_final": target_final,
            "dew_point_delta": target_final - house_dew_point
            if target_final is not None and house_dew_point is not None
            else None,
            "summer_enabled": summer_enabled,
            "season_state": season_state,
            "hottest_room": hottest_room["name"] if hottest_room else None,
            "hottest_room_temperature": hottest_room["temperature"] if hottest_room else None,
            "thermal_trend_per_hour": trend,
            "critical_dew_room": nearest_dew_room_name,
            "critical_dew_zone": nearest_dew_room_zone,
            "critical_dew_delta": dew_delta,
            "critical_dew_state": nearest_dew_state,
            "critical_room_count": len(critical_rooms),
            "warning_room_count": len(warning_rooms),
            "recommended_action": recommended_action,
            "target_reason": target_reason,
            "action_reason": action_reason,
            "zone_giorno_dehumidification_request": zones.get("giorno", {}).get("request"),
            "zone_notte_dehumidification_request": zones.get("notte", {}).get("request"),
            "zone_giorno_dehumidifier_on": zones.get("giorno", {}).get("consent"),
            "zone_notte_dehumidifier_on": zones.get("notte", {}).get("consent"),
            "standby_rugiada": standby_rugiada,
            "standby_porte": standby_porte,
            "standby_attivo": standby_attivo,
            "acs_block": acs_block,
            "room_count": len(rooms),
            "manual_state": self.setting(OPT_MANUAL_STATE, MANUAL_AUTO),
            "safety_margin": safety_margin,
        }
