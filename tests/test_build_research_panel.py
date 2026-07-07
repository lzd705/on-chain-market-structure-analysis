import unittest

from scripts.build_research_panel import build_research_panel_rows


class BuildResearchPanelTests(unittest.TestCase):
    def test_build_research_panel_rows_adds_returns_by_token(self):
        merged_rows = [
            {"date": "2024-01-01", "token_symbol": "UNI", "price_usd": "10", "cex_volume_usd": "100", "dex_volume_usd": "10"},
            {"date": "2024-01-02", "token_symbol": "UNI", "price_usd": "11", "cex_volume_usd": "110", "dex_volume_usd": "11"},
            {"date": "2024-01-03", "token_symbol": "UNI", "price_usd": "12", "cex_volume_usd": "120", "dex_volume_usd": "12"},
            {"date": "2024-01-04", "token_symbol": "UNI", "price_usd": "13", "cex_volume_usd": "130", "dex_volume_usd": "13"},
            {"date": "2024-01-01", "token_symbol": "AAVE", "price_usd": "20", "cex_volume_usd": "200", "dex_volume_usd": "20"},
            {"date": "2024-01-02", "token_symbol": "AAVE", "price_usd": "18", "cex_volume_usd": "180", "dex_volume_usd": "18"},
        ]

        rows = build_research_panel_rows(merged_rows)
        index = {}

        for row in rows:
            index[(row["date"], row["token_symbol"])] = row

        self.assertAlmostEqual(index[("2024-01-01", "UNI")]["future_return_1d"], 0.1)
        self.assertAlmostEqual(index[("2024-01-01", "UNI")]["future_return_3d"], 0.3)
        self.assertAlmostEqual(index[("2024-01-02", "UNI")]["return_1d"], 0.1)
        self.assertAlmostEqual(index[("2024-01-01", "AAVE")]["future_return_1d"], -0.1)
        self.assertEqual(index[("2024-01-04", "UNI")]["future_return_1d"], "")
        self.assertEqual(index[("2024-01-02", "AAVE")]["future_return_3d"], "")


if __name__ == "__main__":
    unittest.main()
