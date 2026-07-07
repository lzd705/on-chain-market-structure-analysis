import math
import unittest

from scripts.build_factors import build_factor_rows


class BuildFactorsTests(unittest.TestCase):
    def test_build_factor_rows_calculates_supported_basic_factors(self):
        panel_rows = []

        for day in range(1, 16):
            panel_rows.append(
                {
                    "date": "2024-01-%02d" % day,
                    "token_symbol": "UNI",
                    "price_usd": str(10 + day),
                    "cex_volume_usd": str(100 * day),
                    "dex_volume_usd": str(10 * day),
                    "dex_share": str((10 * day) / ((100 * day) + (10 * day))),
                }
            )

        factor_rows = build_factor_rows(panel_rows)
        factor_index = {}

        for row in factor_rows:
            key = (row["date"], row["token_symbol"], row["factor_name"])
            factor_index[key] = row

        mom_key = ("2024-01-08", "UNI", "MOM_7D")
        cex_growth_key = ("2024-01-14", "UNI", "CEX_VOL_GROWTH_7D")
        dex_share_key = ("2024-01-01", "UNI", "DEX_SHARE")

        self.assertIn(mom_key, factor_index)
        self.assertIn(cex_growth_key, factor_index)
        self.assertIn(dex_share_key, factor_index)

        expected_mom = math.log(18 / 11)
        expected_growth = math.log((800 + 900 + 1000 + 1100 + 1200 + 1300 + 1400) / (100 + 200 + 300 + 400 + 500 + 600 + 700))

        self.assertAlmostEqual(float(factor_index[mom_key]["factor_value"]), expected_mom)
        self.assertAlmostEqual(float(factor_index[cex_growth_key]["factor_value"]), expected_growth)
        self.assertAlmostEqual(float(factor_index[dex_share_key]["factor_value"]), 10 / 110)
        self.assertEqual(factor_index[mom_key]["lookback_window"], "7d")
        self.assertEqual(factor_index[cex_growth_key]["lookback_window"], "7d_vs_prev_7d")
        self.assertEqual(factor_index[dex_share_key]["data_source"], "merged_volume_panel")


if __name__ == "__main__":
    unittest.main()
