"""Data coordinator for Radiant Climate Controller."""

from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
import logging
import math
import time
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
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

TREND_HISTORY_RETENTION_SECONDS = 7200
TREND_MIN_COVERAGE = 0.8
TREND_WINDOWS_SECONDS = {
    "15m": 15 * 60,
    "30m": 30 * 60,
    "60m": 60 * 60,
}

STATE_HYSTERESIS_C = 0.3
HOTTEST_ROOM_SWITCH_DELTA_C = 0.2
TREND_REASON_STABLE_C_PER_H = 0.05
STATE_RANK = {
    STATE_MAINTENANCE: 0,
    STATE_NORMAL: 1,
    STATE_BOOST: 2,
    STATE_RECOVERY: 3,
}


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
        self._temperature_history: list[tuple[float, float]] = []
        self._last_comfort_state: str | None = None
        self._last_hottest_room_key: str | None = None
        self._remove_state_listener: Callable[[], None] | None = None
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

    def async_start_listeners(self) -> None:
        """Start listening to source entity changes."""
        if self._remove_state_listener is not None:
            return

        entity_ids = sorted(self._watched_entity_ids())
        if not entity_ids:
            return

        self._remove_state_listener = async_track_state_change_event(
            self.hass,
            entity_ids,
            self._async_source_state_changed,
        )
        _LOGGER.debug("Watching %s source entities", len(entity_ids))

    def async_stop_listeners(self) -> None:
        """Stop listening to source entity changes."""
        if self._remove_state_listener is not None:
            self._remove_state_listener()
            self._remove_state_listener = None

    def _watched_entity_ids(self) -> set[str]:
        """Return all HA entities that can change calculated data."""
        data = self.entry.data
        entity_ids: set[str] = {
            data.get(CONF_SEASON_ENTITY),
            ENTITY_DEW_POINT_MARGIN,
            ENTITY_DEW_POINT_MAX_HOUSE,
            ENTITY_STANDBY_RUGIADA,
            ENTITY_STANDBY_PORTE,
            ENTITY_STANDBY_ATTIVO,
            ENTITY_ACS_BLOCK,
        }

        for cfg in ROOMS.values():
            entity_ids.update(
                {
                    cfg.get("temperature"),
                    cfg.get("humidity"),
                    cfg.get("dew_point"),
                    cfg.get("safety_boolean"),
                }
            )

        for cfg in ZONE_DEHUMIDIFIERS.values():
            entity_ids.update(
                {
                    cfg.get("request"),
                    cfg.get("consent"),
                    cfg.get("average_temperature"),
                    cfg.get("average_humidity"),
                    cfg.get("humidity_threshold"),
                }
            )

        return {entity_id for entity_id in entity_ids if entity_id}

    @callback
    def _async_source_state_changed(self, event: Event) -> None:
        """Refresh calculated data when a source entity changes."""
        self.async_set_updated_data(self._calculate())

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

    def _select_hottest_room(self, rooms: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
        """Return a stable hottest room to avoid fast flips between similar rooms."""
        candidates = [room for room in rooms.values() if room["temperature"] is not None]
        if not candidates:
            self._last_hottest_room_key = None
            return None

        candidate = max(candidates, key=lambda item: item["temperature"])
        last_key = self._last_hottest_room_key
        if last_key in rooms and candidate["key"] != last_key:
            last_room = rooms[last_key]
            last_temp = last_room.get("temperature")
            candidate_temp = candidate.get("temperature")
            if (
                last_temp is not None
                and candidate_temp is not None
                and candidate_temp <= last_temp + HOTTEST_ROOM_SWITCH_DELTA_C
            ):
                return last_room

        self._last_hottest_room_key = candidate["key"]
        return candidate

    def _record_temperature_sample(self, temperature: float | None, now_ts: float) -> None:
        """Store a rolling history of max house temperature."""
        if temperature is None:
            return

        if self._temperature_history:
            last_ts, last_temp = self._temperature_history[-1]
            if now_ts - last_ts < DEFAULT_SCAN_INTERVAL_SECONDS * 0.8 and last_temp == temperature:
                return

        self._temperature_history.append((now_ts, temperature))
        cutoff = now_ts - TREND_HISTORY_RETENTION_SECONDS
        self._temperature_history = [
            (sample_ts, sample_temp)
            for sample_ts, sample_temp in self._temperature_history
            if sample_ts >= cutoff
        ]

    def _trend_from_history(self, current_temperature: float | None, window_seconds: int, now_ts: float) -> float | None:
        """Calculate filtered trend over a time window in C/h."""
        if current_temperature is None or not self._temperature_history:
            return None

        target_ts = now_ts - window_seconds
        baseline: tuple[float, float] | None = None

        for sample in reversed(self._temperature_history):
            sample_ts, _sample_temp = sample
            if sample_ts <= target_ts:
                baseline = sample
                break

        if baseline is None:
            oldest = self._temperature_history[0]
            elapsed_from_oldest = now_ts - oldest[0]
            if elapsed_from_oldest < window_seconds * TREND_MIN_COVERAGE:
                return None
            baseline = oldest

        baseline_ts, baseline_temp = baseline
        elapsed = now_ts - baseline_ts
        if elapsed <= 0:
            return None
        return (current_temperature - baseline_temp) / (elapsed / 3600.0)

    def _calculate_trends(self, current_temperature: float | None) -> dict[str, Any]:
        """Return trend values and the trend selected for control logic."""
        now_ts = time.monotonic()
        self._record_temperature_sample(current_temperature, now_ts)

        trend_15m = self._trend_from_history(current_temperature, TREND_WINDOWS_SECONDS["15m"], now_ts)
        trend_30m = self._trend_from_history(current_temperature, TREND_WINDOWS_SECONDS["30m"], now_ts)
        trend_60m = self._trend_from_history(current_temperature, TREND_WINDOWS_SECONDS["60m"], now_ts)

        if trend_30m is not None:
            trend_used = trend_30m
            trend_source = "30m"
        elif trend_15m is not None:
            trend_used = trend_15m
            trend_source = "15m"
        else:
            trend_used = None
            trend_source = "non_disponibile"

        return {
            "trend_used": trend_used,
            "trend_source": trend_source,
            "trend_15m": trend_15m,
            "trend_30m": trend_30m,
            "trend_60m": trend_60m,
            "trend_sample_count": len(self._temperature_history),
        }

    def _trend_text_for_reason(self, trend: float | None, trend_source: str | None) -> str:
        """Return a stable textual trend summary for reason sensors."""
        if trend is None or trend_source in (None, "non_disponibile"):
            return "trend filtrato non ancora disponibile"
        if abs(trend) < TREND_REASON_STABLE_C_PER_H:
            return f"trend {trend_source} stabile"
        if trend > 0:
            return f"trend {trend_source} in aumento"
        return f"trend {trend_source} in calo"

    def _exit_threshold_for_state(self, state: str, thresholds: dict[str, float]) -> float | None:
        """Return the lower threshold used to leave the current state."""
        if state == STATE_RECOVERY:
            return thresholds[STATE_RECOVERY] - STATE_HYSTERESIS_C
        if state == STATE_BOOST:
            return thresholds[STATE_BOOST] - STATE_HYSTERESIS_C
        if state == STATE_NORMAL:
            return thresholds[STATE_NORMAL] - STATE_HYSTERESIS_C
        return None

    def _base_comfort_state(
        self,
        hottest_temp: float,
        trend_value: float,
        trend_text: str,
        thresholds: dict[str, float],
        precool: dict[str, float],
        trend_thresholds: dict[str, float],
    ) -> tuple[str, str, bool]:
        """Calculate the comfort state before hysteresis is applied."""
        if hottest_temp >= thresholds[STATE_RECOVERY]:
            return STATE_RECOVERY, f"recupero: temperatura {hottest_temp:.1f} C, {trend_text}", False

        if hottest_temp >= thresholds[STATE_BOOST]:
            return STATE_BOOST, f"spinto: temperatura {hottest_temp:.1f} C, {trend_text}", False
        if hottest_temp >= precool[STATE_BOOST] and trend_value >= trend_thresholds[STATE_BOOST]:
            return STATE_BOOST, f"spinto anticipato: temperatura {hottest_temp:.1f} C, {trend_text}", True

        if hottest_temp >= thresholds[STATE_NORMAL]:
            return STATE_NORMAL, f"normale: temperatura {hottest_temp:.1f} C, {trend_text}", False
        if hottest_temp >= precool[STATE_NORMAL] and trend_value >= trend_thresholds[STATE_NORMAL]:
            return STATE_NORMAL, f"normale anticipato: temperatura {hottest_temp:.1f} C, {trend_text}", True

        return STATE_MAINTENANCE, f"mantenimento: temperatura {hottest_temp:.1f} C, {trend_text}", False

    def _comfort_state_and_target(
        self, hottest_temp: float | None, trend: float | None, trend_source: str | None
    ) -> tuple[str, float, str, bool]:
        manual_state = self.setting(OPT_MANUAL_STATE, MANUAL_AUTO)
        if manual_state != MANUAL_AUTO:
            self._last_comfort_state = None
            target = self._target_for_state(manual_state)
            return manual_state, target, f"stato radiante forzato manualmente: {manual_state}", False

        if hottest_temp is None:
            self._last_comfort_state = None
            return (
                STATE_UNKNOWN,
                self._target_for_state(STATE_MAINTENANCE),
                "temperatura massima casa non disponibile",
                False,
            )

        trend_value = trend or 0.0
        trend_text = self._trend_text_for_reason(trend, trend_source)

        thresholds = {
            STATE_RECOVERY: float(self.setting(OPT_THRESHOLD_RECOVERY, DEFAULT_THRESHOLD_RECOVERY)),
            STATE_BOOST: float(self.setting(OPT_THRESHOLD_BOOST, DEFAULT_THRESHOLD_BOOST)),
            STATE_NORMAL: float(self.setting(OPT_THRESHOLD_NORMAL, DEFAULT_THRESHOLD_NORMAL)),
        }
        precool = {
            STATE_RECOVERY: float(self.setting(OPT_PRECOOL_RECOVERY_TEMP, DEFAULT_PRECOOL_RECOVERY_TEMP)),
            STATE_BOOST: float(self.setting(OPT_PRECOOL_BOOST_TEMP, DEFAULT_PRECOOL_BOOST_TEMP)),
            STATE_NORMAL: float(self.setting(OPT_PRECOOL_NORMAL_TEMP, DEFAULT_PRECOOL_NORMAL_TEMP)),
        }
        trend_thresholds = {
            STATE_RECOVERY: float(self.setting(OPT_TREND_RECOVERY, DEFAULT_TREND_RECOVERY)),
            STATE_BOOST: float(self.setting(OPT_TREND_BOOST, DEFAULT_TREND_BOOST)),
            STATE_NORMAL: float(self.setting(OPT_TREND_NORMAL, DEFAULT_TREND_NORMAL)),
        }

        base_state, base_reason, predictive_trigger = self._base_comfort_state(
            hottest_temp,
            trend_value,
            trend_text,
            thresholds,
            precool,
            trend_thresholds,
        )

        last_state = self._last_comfort_state
        if (
            last_state in STATE_RANK
            and base_state in STATE_RANK
            and STATE_RANK[last_state] > STATE_RANK[base_state]
        ):
            exit_threshold = self._exit_threshold_for_state(last_state, thresholds)
            if exit_threshold is not None and hottest_temp > exit_threshold:
                self._last_comfort_state = last_state
                return (
                    last_state,
                    self._target_for_state(last_state),
                    f"{last_state} mantenuto: temperatura {hottest_temp:.1f} C sopra uscita {exit_threshold:.1f} C, {trend_text}",
                    False,
                )

        self._last_comfort_state = base_state
        return base_state, self._target_for_state(base_state), base_reason, predictive_trigger

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

        hottest_room = self._select_hottest_room(rooms)
        nearest_dew_room = min(valid_deltas, key=lambda item: item["dew_delta"]) if valid_deltas else None

        zone_temperature = max(valid_temperatures) if valid_temperatures else None
        zone_humidity = max(valid_humidities) if valid_humidities else None
        house_dew_point = self._float_state(ENTITY_DEW_POINT_MAX_HOUSE)
        if house_dew_point is None and valid_dew_points:
            house_dew_point = max(valid_dew_points)

        trends = self._calculate_trends(zone_temperature)
        trend = trends["trend_used"]
        trend_source = trends["trend_source"]
        climate_state, target_requested, target_reason, predictive_trigger = self._comfort_state_and_target(
            zone_temperature, trend, trend_source
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
            action_reason = f"rischio rugiada in zona {nearest_dew_room_zone}: priorita deumidificazione zona"
        elif recommended_action == ACTION_ACS_BLOCK:
            action_reason = "ACS attiva o blocco miscelatrice: non usare il target come comando utile"
        elif recommended_action == ACTION_DOOR_STANDBY:
            action_reason = "porte/finestre in standby: evitare raffrescamento attivo"
        elif recommended_action == ACTION_DISABLED:
            action_reason = "modalita stagionale diversa da Estate"
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
            "thermal_trend_source": trend_source,
            "thermal_trend_15m_per_hour": trends["trend_15m"],
            "thermal_trend_30m_per_hour": trends["trend_30m"],
            "thermal_trend_60m_per_hour": trends["trend_60m"],
            "thermal_trend_sample_count": trends["trend_sample_count"],
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
