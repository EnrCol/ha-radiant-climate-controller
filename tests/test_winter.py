"""Unit tests for winter preview without a Home Assistant runtime."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / "custom_components" / "radiant_climate_controller" / "winter.py"
SPEC = importlib.util.spec_from_file_location("radiant_winter_test", MODULE)
assert SPEC is not None and SPEC.loader is not None
winter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(winter)


class WinterPreviewTests(unittest.TestCase):
    def test_climate_curve_limits(self):
        for outside, expected in [
            (-15, 30.0),
            (0, 30.0),
            (9, 28.0),
            (10, 27.8),
            (18, 26.0),
            (28, 26.0),
        ]:
            with self.subTest(outside=outside):
                self.assertEqual(winter.winter_curve_target(outside), expected)

    def test_missing_or_invalid_outdoor_data_fails_closed(self):
        for value in [None, "unknown", "unavailable", float("nan"), float("inf"), float("-inf")]:
            with self.subTest(value=value):
                self.assertIsNone(winter.winter_curve_target(value))

    def test_heating_demand(self):
        self.assertEqual(
            winter.winter_demand_status([("heat", "idle"), ("heat", "heating")], acs_active=False),
            "richiesta_riscaldamento",
        )
        self.assertEqual(
            winter.winter_demand_status([("heat", "idle"), ("off", "off")], acs_active=False),
            "nessuna_richiesta",
        )
        self.assertEqual(
            winter.winter_demand_status([(None, None), ("unavailable", None)], acs_active=False),
            "termostati_non_disponibili",
        )
        self.assertEqual(
            winter.winter_demand_status([("cool", "heating")], acs_active=False),
            "nessuna_richiesta",
        )

    def test_acs_priority_is_observational(self):
        self.assertEqual(
            winter.winter_demand_status([("heat", "heating")], acs_active=True),
            "acs_prioritaria",
        )


if __name__ == "__main__":
    unittest.main()
