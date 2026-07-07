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

    def make_pool_daily(self, token_symbol: str = "AAA", days: int = 40) -> pd.DataFrame:
        rows = []
        for day in range(days):
            date = pd.Timestamp("2026-01-01") + pd.Timedelta(days=day)
            for pool_index, pool_share in enumerate([0.7, 0.3], start=1):
                rows.append(
                    {
                        "date": date,
                        "token_symbol": token_symbol,
                        "pool_address": f"pool_{pool_index}",
                        "open": 10 + day,
                        "high": 12 + day,
                        "low": 9 + day,
                        "close": 11 + day if pool_index == 1 else 10 + day,
                        "dex_volume_usd": 100_000 * pool_share,
                        "pool_tvl_usd": 1_000_000 * pool_share,
                    }
                )
        return pd.DataFrame(rows)

    def test_add_factors_creates_expected_columns(self) -> None:
        panel = self.make_panel()
        result = run_research.add_factors(panel, drop_last_date=False)

        self.assertIn("cex_vol_z", result.columns)
        self.assertIn("token_group", result.columns)
        self.assertIn("dex_vol_z", result.columns)
        self.assertIn("mom_7d", result.columns)
        self.assertIn("mom_14d", result.columns)
        self.assertIn("mom_30d", result.columns)
        self.assertIn("mom_7d_skip_1d", result.columns)
        self.assertIn("reversal_1d", result.columns)
        self.assertIn("realized_vol_14d", result.columns)
        self.assertIn("momentum_vol_adj_7d", result.columns)
        self.assertIn("total_vol_z", result.columns)
        self.assertIn("cex_vol_growth_7d", result.columns)
        self.assertIn("dex_vol_growth_7d", result.columns)
        self.assertIn("total_vol_growth_7d", result.columns)
        self.assertIn("dex_share_z", result.columns)
        self.assertIn("dex_share_change_7d", result.columns)
        self.assertIn("cex_dex_ratio_z", result.columns)
        self.assertIn("volume_growth_divergence_7d", result.columns)
        self.assertIn("joint_vol_z_mean", result.columns)
        self.assertIn("cex_dex_z_product", result.columns)
        self.assertIn("dex_share_x_dex_vol_z", result.columns)
        self.assertIn("cex_volume_confirmed_mom_7d", result.columns)
        self.assertIn("dex_volume_confirmed_mom_7d", result.columns)
        self.assertIn("joint_volume_confirmed_mom_7d", result.columns)
        self.assertIn("dex_share_confirmed_mom_7d", result.columns)
        self.assertIn("dex_net_buy_ratio_proxy", result.columns)
        self.assertIn("dex_buy_pressure_proxy_z", result.columns)
        self.assertIn("dex_net_buy_confirmed_mom_7d", result.columns)
        self.assertIn("top_pool_volume_share", result.columns)
        self.assertIn("dex_pool_herfindahl", result.columns)
        self.assertIn("dex_pool_diversification", result.columns)
        self.assertIn("dex_volume_to_tvl_z", result.columns)
        self.assertIn("pool_diversified_dex_mom_7d", result.columns)
        self.assertIn("dex_share", result.columns)
        self.assertIn("future_return_7d", result.columns)
        self.assertIn("future_return_14d", result.columns)
        self.assertAlmostEqual(result.loc[0, "future_return_1d"], 0.1)
        self.assertGreater(result["cex_vol_z"].notna().sum(), 0)
        self.assertGreater(result["mom_7d"].notna().sum(), 0)
        self.assertGreater(result["cex_vol_growth_7d"].notna().sum(), 0)
        self.assertGreater(result["joint_vol_z_mean"].notna().sum(), 0)

    def test_dex_pool_features_create_direction_and_concentration_metrics(self) -> None:
        pool_daily = self.make_pool_daily()
        features = run_research.calculate_dex_pool_features(pool_daily)

        self.assertIn("dex_buy_volume_proxy_usd", features.columns)
        self.assertIn("dex_sell_volume_proxy_usd", features.columns)
        self.assertIn("dex_net_buy_ratio_proxy", features.columns)
        self.assertIn("top_pool_volume_share", features.columns)
        self.assertIn("dex_pool_herfindahl", features.columns)
        self.assertIn("dex_volume_to_tvl", features.columns)
        self.assertAlmostEqual(features.loc[0, "top_pool_volume_share"], 0.7)
        self.assertAlmostEqual(features.loc[0, "dex_pool_herfindahl"], 0.58)
        self.assertGreater(features.loc[0, "dex_net_buy_ratio_proxy"], 0)

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

    def test_candidate_factor_summary_is_written(self) -> None:
        panel = self.make_panel("AAA", 50)
        factor_panel = run_research.add_factors(panel, drop_last_date=False)

        run_research.write_candidate_factor_forward_returns(factor_panel)

        output = run_research.pd.read_csv(run_research.CANDIDATE_FACTOR_RETURNS_PATH)
        self.assertIn("factor_name", output.columns)
        self.assertIn("mom_7d", set(output["factor_name"]))
        self.assertIn("joint_vol_z_mean", set(output["factor_name"]))
        self.assertIn("future_return_14d_mean", output.columns)

    def test_factor_robustness_checks_are_written(self) -> None:
        panel = pd.concat(
            [
                self.make_panel("AAVE", 55),
                self.make_panel("ARB", 55),
                self.make_panel("PEPE", 55),
            ],
            ignore_index=True,
        )
        factor_panel = run_research.add_factors(panel, drop_last_date=False)

        run_research.write_factor_robustness_checks(factor_panel)

        output = run_research.pd.read_csv(run_research.FACTOR_ROBUSTNESS_PATH)
        self.assertIn("check_type", output.columns)
        self.assertIn("overall", set(output["check_type"]))
        self.assertIn("exclude_pepe_arb", set(output["subset_name"]))


if __name__ == "__main__":
    unittest.main()
