"""Runtime bugfixes for the Radiant Climate coordinator.

Kept separate from coordinator.py to make the 0.4.2 safety fix small and easy to review.
"""

from __future__ import annotations

import time
from typing import Any

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
    ENTITY_ACS_BLOCK,
    ENTITY_DEW_POINT_MAX_HOUSE,
    ENTITY_STANDBY_ATTIVO,
    ENTITY_STANDBY_PORTE,
    ENTITY_STANDBY_RUGIADA,
    MANUAL_AUTO,
    OPT_MANUAL_STATE,
    STATE_BOOST,
    STATE_MAINTENANCE,
    STATE_NORMAL,
    STATE_RECOVERY,
    STATE_UNKNOWN,
)
from .coordinator import TARGET_COMMAND_MAX_C, TARGET_COMMAND_MIN_C


def _patched_base_comfort_state(
    self,
    hottest_temp: float,
    trend_value: float,
    trend_text: str,
    thresholds: dict[str, float],
    precool: dict[str, float],
    trend_thresholds: dict[str, float],
) -> tuple[str, str, bool]:
    """Calculate comfort state, including the missing recovery precool branch."""
    if hottest_temp >= thresholds[STATE_RECOVERY]:
        return STATE_RECOVERY, "recupero: soglia recupero attiva", False
    if hottest_temp >= precool[STATE_RECOVERY] and trend_value >= trend_thresholds[STATE_RECOVERY]:
        return STATE_RECOVERY, f"recupero anticipato: soglia anticipo recupero attiva, {trend_text}", True

    if hottest_temp >= thresholds[STATE_BOOST]:
        return STATE_BOOST, "spinto: soglia spinto attiva", False
    if hottest_temp >= precool[STATE_BOOST] and trend_value >= trend_thresholds[STATE_BOOST]:
        return STATE_BOOST, f"spinto anticipato: soglia anticipo spinto attiva, {trend_text}", True

    if hottest_temp >= thresholds[STATE_NORMAL]:
        return STATE_NORMAL, "normale: soglia normale attiva", False
    if hottest_temp >= precool[STATE_NORMAL] and trend_value >= trend_thresholds[STATE_NORMAL]:
        return STATE_NORMAL, f"normale anticipato: soglia anticipo normale attiva, {trend_text}", True

    return STATE_MAINTENANCE, "mantenimento: sotto soglie raffrescamento", False


def _patched_command_gate(
    self,
    *,
    summer_enabled: bool,
    target_final: float | None,
    climate_state: str,
    recommended_action: str,
    acs_block: bool,
    standby_porte: bool,
    standby_rugiada: bool,
    manual_state: str,
) -> tuple[bool, str]:
    """Return whether the final target can be used as an external command."""
    if not summer_enabled:
        return False, "non comandabile: modalita stagionale diversa da Estate"
    if manual_state != MANUAL_AUTO:
        return False, "non comandabile: stato manuale attivo"
    if climate_state == STATE_UNKNOWN:
        return False, "non comandabile: stato radiante sconosciuto"
    if target_final is None:
        return False, "non comandabile: target mandata non disponibile"
    if target_final < TARGET_COMMAND_MIN_C or target_final > TARGET_COMMAND_MAX_C:
        return False, "non comandabile: target mandata fuori range sicuro"
    if acs_block:
        return False, "non comandabile: ACS attiva o blocco miscelatrice"
    if self._is_on(ENTITY_STANDBY_ATTIVO):
        return False, "non comandabile: standby attivo"
    if standby_porte:
        return False, "non comandabile: standby porte/finestre attivo"
    if standby_rugiada or recommended_action == ACTION_GLOBAL_PROTECTION:
        return False, "non comandabile: protezione rugiada globale attiva"
    if recommended_action in (ACTION_LOCAL_PROTECTION, ACTION_DEHUMIDIFY):
        return False, "non comandabile: rischio rugiada locale da gestire prima"
    if recommended_action == ACTION_DISABLED:
        return False, "non comandabile: raffrescamento non abilitato"
    return True, "comandabile: target valido e sicurezze ok"


def _room_with_lowest_delta(rooms: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the room with the lowest dew delta from a non-empty-like list."""
    if not rooms:
        return None
    return min(
        rooms,
        key=lambda item: item["dew_delta"] if item.get("dew_delta") is not None else float("inf"),
    )


def _patched_calculate(self) -> dict[str, Any]:
    """Calculate coordinator data with command-safe fixes applied."""
    data = self.entry.data
    season_entity = data.get(CONF_SEASON_ENTITY)
    season_state = self._state(season_entity)
    summer_enabled = season_state == "Estate"

    safety_margin = self._safety_margin()
    rooms = self._calculate_rooms(safety_margin)
    zones = self._calculate_zone_states()

    valid_temperatures = [room["temperature"] for room in rooms.values() if room["temperature"] is not None]
    valid_humidities = [room["humidity"] for room in rooms.values() if room["humidity"] is not None]
    valid_dew_points = [room["dew_point"] for room in rooms.values() if room["dew_point"] is not None]
    valid_deltas = [room for room in rooms.values() if room["dew_delta"] is not None]

    hottest_room = self._select_hottest_room(rooms)
    hottest_temperature = hottest_room["temperature"] if hottest_room else None
    zone_temperature = max(valid_temperatures) if valid_temperatures else None
    zone_humidity = max(valid_humidities) if valid_humidities else None
    trend_temperature = hottest_temperature if hottest_temperature is not None else zone_temperature

    house_dew_point = self._float_state(ENTITY_DEW_POINT_MAX_HOUSE)
    if house_dew_point is None and valid_dew_points:
        house_dew_point = max(valid_dew_points)

    trends = self._calculate_trends(trend_temperature)
    trend = trends["trend_used"]
    trend_source = trends["trend_source"]
    climate_state, target_requested, target_reason, predictive_trigger = self._comfort_state_and_target(
        trend_temperature, trend, trend_source
    )

    target_safe = house_dew_point + safety_margin if house_dew_point is not None else 19.0
    target_final = max(target_requested, target_safe) if summer_enabled else None

    acs_block = self._is_on(ENTITY_ACS_BLOCK)
    standby_porte = self._is_on(ENTITY_STANDBY_PORTE)
    standby_rugiada = self._is_on(ENTITY_STANDBY_RUGIADA)
    standby_attivo = self._is_on(ENTITY_STANDBY_ATTIVO)
    manual_state = self.setting(OPT_MANUAL_STATE, MANUAL_AUTO)

    critical_rooms = [room for room in rooms.values() if room["risk"] == "critico"]
    warning_rooms = [room for room in rooms.values() if room["risk"] == "attenzione"]
    critical_zones = {room["zone"] for room in critical_rooms if room.get("zone")}
    critical_dew_room = _room_with_lowest_delta(critical_rooms)
    nearest_dew_room = _room_with_lowest_delta(valid_deltas)

    recommended_action = ACTION_IDLE
    if not summer_enabled:
        recommended_action = ACTION_DISABLED
    elif acs_block:
        recommended_action = ACTION_ACS_BLOCK
    elif standby_porte:
        recommended_action = ACTION_DOOR_STANDBY
    elif len(critical_rooms) >= 2 or len(critical_zones) >= 2 or standby_rugiada:
        recommended_action = ACTION_GLOBAL_PROTECTION
    elif critical_dew_room is not None:
        zone = critical_dew_room.get("zone")
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
    elif recommended_action == ACTION_LOCAL_PROTECTION and critical_dew_room is not None:
        action_reason = f"rischio rugiada localizzato in {critical_dew_room['name']}: preferire azione locale/testina"
    elif recommended_action == ACTION_DEHUMIDIFY and critical_dew_room is not None:
        action_reason = f"rischio rugiada in zona {critical_dew_room['zone']}: priorita deumidificazione zona"
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

    target_commandable, target_commandable_reason = self._command_gate(
        summer_enabled=summer_enabled,
        target_final=target_final,
        climate_state=climate_state,
        recommended_action=recommended_action,
        acs_block=acs_block,
        standby_porte=standby_porte,
        standby_rugiada=standby_rugiada,
        manual_state=manual_state,
    )

    return {
        "zone_temperature": zone_temperature,
        "zone_humidity": zone_humidity,
        "dew_point": house_dew_point,
        "climate_state": climate_state,
        "target_requested": target_requested,
        "target_safe": target_safe,
        "target_final": target_final,
        "target_commandable": target_commandable,
        "target_commandable_reason": target_commandable_reason,
        "command_heartbeat": int(time.time()),
        "dew_point_delta": target_final - house_dew_point if target_final is not None and house_dew_point is not None else None,
        "summer_enabled": summer_enabled,
        "season_state": season_state,
        "hottest_room": hottest_room["name"] if hottest_room else None,
        "hottest_room_temperature": hottest_temperature,
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
        "manual_state": manual_state,
        "safety_margin": safety_margin,
    }


def apply_coordinator_bugfixes(coordinator_class: type[Any]) -> None:
    """Install the 0.4.2 coordinator bugfix methods."""
    coordinator_class._base_comfort_state = _patched_base_comfort_state
    coordinator_class._command_gate = _patched_command_gate
    coordinator_class._calculate = _patched_calculate
