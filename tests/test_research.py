"""Unit tests for first-pass research factor logic."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from research import run_research


class ResearchFactorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        temp_root = Path(self.temp_dir.name)
        run_research.configure_paths(
            temp_root / "processed",
            temp_root / "research",
            temp_root / "figures",
        )
        run_research.ensure_output_dirs()
        run_research.load_analysis_dependencies()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def make_panel(self, token_symbol: str = "AAA", days: int = 40) -> pd.DataFrame:
        rows = []
        for day in range(days):
            rows.append(
                {
                    "date": pd.Timestamp("2026-01-01") + pd.Timedelta(days=day),
                    "token_symbol": token_symbol,
                    "price_usd": 10 + day,
                    "cex_volume_usd": 1_000_000 + day * 10_000,
                    "dex_volume_usd": 100_000 + day * 2_000,
                }
            )
        return pd.DataFrame(rows)

    def test_add_factors_creates_expected_columns(self) -> None:
        panel = self.make_panel()
        result = run_research.add_factors(panel, drop_last_date=False)

        self.assertIn("cex_vol_z", result.columns)
        self.assertIn("dex_vol_z", result.columns)
        self.assertIn("dex_share", result.columns)
        self.assertIn("future_return_7d", result.columns)
        self.assertAlmostEqual(result.loc[0, "future_return_1d"], 0.1)
        self.assertGreater(result["cex_vol_z"].notna().sum(), 0)

    def test_short_tokens_are_filtered(self) -> None:
        long_panel = self.make_panel("LONG", 40)
        short_panel = self.make_panel("SHORT", 12)
        combined = pd.concat([long_panel, short_panel], ignore_index=True)

        result = run_research.filter_short_tokens(combined, min_token_days=30)

        self.assertEqual(set(result["token_symbol"].unique()), {"LONG"})

    def test_data_quality_flags_short_history(self) -> None:
        panel = self.make_panel("SHORT", 12)
        report = run_research.build_data_quality_report(panel, min_token_days=30)

        self.assertEqual(report.loc[0, "status"], "too_short")
        self.assertEqual(report.loc[0, "row_count"], 12)

    def test_lead_lag_shape(self) -> None:
        panel = self.make_panel("AAA", 45)
        factor_panel = run_research.add_factors(panel, drop_last_date=False)
        result = run_research.calculate_lead_lag(factor_panel, max_lag=2)

        self.assertEqual(len(result), 5)
        self.assertEqual(set(result["lag"]), {-2, -1, 0, 1, 2})


if __name__ == "__main__":
    unittest.main()
