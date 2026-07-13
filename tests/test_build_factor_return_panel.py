import unittest

from scripts.build_factor_return_panel import build_factor_return_panel_rows


class BuildFactorReturnPanelTests(unittest.TestCase):
    def test_build_factor_return_panel_rows_joins_factors_to_future_returns(self):
        factor_rows = [
            {
                "date": "2024-01-01",
                "token_symbol": "UNI",
                "factor_name": "MOM_7D",
                "factor_value": "0.12",
                "lookback_window": "7d",
                "data_source": "merged_volume_panel",
            },
            {
                "date": "2024-01-02",
                "token_symbol": "UNI",
                "factor_name": "DEX_SHARE",
                "factor_value": "0.30",
                "lookback_window": "1d",
                "data_source": "merged_volume_panel",
            },
            {
                "date": "2024-01-03",
                "token_symbol": "AAVE",
                "factor_name": "MOM_7D",
                "factor_value": "0.08",
                "lookback_window": "7d",
                "data_source": "merged_volume_panel",
            },
        ]
        research_rows = [
            {
                "date": "2024-01-01",
                "token_symbol": "UNI",
                "price_usd": "10",
                "cex_volume_usd": "100",
                "dex_volume_usd": "20",
                "dex_share": "0.1666666667",
                "return_1d": "",
                "future_return_1d": "0.10",
                "future_return_3d": "0.20",
                "future_return_7d": "0.30",
            },
            {
                "date": "2024-01-02",
                "token_symbol": "UNI",
                "price_usd": "11",
                "cex_volume_usd": "110",
                "dex_volume_usd": "30",
                "dex_share": "0.2142857143",
                "return_1d": "0.10",
                "future_return_1d": "0.05",
                "future_return_3d": "0.15",
                "future_return_7d": "",
            },
        ]

        rows = build_factor_return_panel_rows(factor_rows, research_rows)

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["date"], "2024-01-01")
        self.assertEqual(rows[0]["token_symbol"], "UNI")
        self.assertEqual(rows[0]["factor_name"], "MOM_7D")
        self.assertEqual(rows[0]["factor_value"], "0.12")
        self.assertEqual(rows[0]["price_usd"], "10")
        self.assertEqual(rows[0]["future_return_7d"], "0.30")
        self.assertEqual(rows[1]["factor_name"], "DEX_SHARE")
        self.assertEqual(rows[1]["future_return_7d"], "")


if __name__ == "__main__":
    unittest.main()
