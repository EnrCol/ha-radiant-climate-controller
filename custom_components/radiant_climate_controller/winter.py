"""Minimal, read-only winter heating calculations.

The curve mirrors the existing ESP32 winter limits. It must never
drive a mixing valve or the heat pump without a separate activation.
"""

from __future__ import annotations

from collections.abc import Iterable
import math

OUTDOOR_ENTITY = "sensor.ecodan_ashp_outside_temperature"
OUTDOOR_MIN_C = 0.0
OUTDOOR_MAX_C = 18.0
FLOW_AT_COLD_C = 30.0
FLOW_AT_WARM_C = 26.0


def winter_curve_target(outdoor_temperature: float | None) -> float | None:
    """Weather-compensated heating supply target, clamped to 26–30 C."""
    if outdoor_temperature is None:
        return None
    try:
        outdoor = float(outdoor_temperature)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(outdoor):
        return None

    fraction = (outdoor - OUTDOOR_MIN_C) / (OUTDOOR_MAX_C - OUTDOOR_MIN_C)
    fraction = max(0.0, min(1.0, fraction))
    return round(FLOW_AT_COLD_C + fraction * (FLOW_AT_WARM_C - FLOW_AT_COLD_C), 1)


def winter_demand_status(
    thermostats: Iterable[tuple[str | None, str | None]], *, acs_active: bool
) -> str:
    """Report heating demand; never modify thermostats for an ACS cycle."""
    if acs_active:
        return "acs_prioritaria"

    has_valid_thermostat = False
    for hvac_mode, hvac_action in thermostats:
        if hvac_mode in ("heat", "heat_cool", "cool", "off"):
            has_valid_thermostat = True
        if hvac_mode in ("heat", "heat_cool") and hvac_action == "heating":
            return "richiesta_riscaldamento"

    return "nessuna_richiesta" if has_valid_thermostat else "termostati_non_disponibili"
