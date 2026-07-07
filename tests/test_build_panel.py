import unittest

from scripts.build_panel import merge_volume_rows


class BuildPanelTests(unittest.TestCase):
    def test_merge_volume_rows_inner_joins_and_calculates_basic_metrics(self):
        cex_rows = [
            {
                "date": "2024-01-01",
                "token_symbol": "UNI",
                "close": "7.30",
                "cex_volume_usd": "700.0",
                "exchange_count": "3",
                "included_exchanges": "binance;bybit;okx",
            },
            {
                "date": "2024-01-02",
                "token_symbol": "UNI",
                "close": "7.40",
                "cex_volume_usd": "900.0",
                "exchange_count": "3",
                "included_exchanges": "binance;bybit;okx",
            },
        ]

        dex_rows = [
            {
                "date": "2024-01-01",
                "token_symbol": "UNI",
                "chain": "eth",
                "selected_chains": "arbitrum;eth",
                "dex_volume_usd": "300.0",
                "pool_count": "3",
                "included_dexes": "uniswap_v3",
                "included_pool_addresses": "0xpool",
            },
            {
                "date": "2024-01-03",
                "token_symbol": "UNI",
                "chain": "eth",
                "dex_volume_usd": "400.0",
                "pool_count": "3",
                "included_dexes": "uniswap_v3",
                "included_pool_addresses": "0xpool",
            },
        ]

        result = merge_volume_rows(cex_rows, dex_rows)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["date"], "2024-01-01")
        self.assertEqual(result[0]["token_symbol"], "UNI")
        self.assertEqual(result[0]["price_usd"], 7.30)
        self.assertEqual(result[0]["cex_volume_usd"], 700.0)
        self.assertEqual(result[0]["dex_volume_usd"], 300.0)
        self.assertEqual(result[0]["total_volume_usd"], 1000.0)
        self.assertEqual(result[0]["dex_share"], 0.3)
        self.assertEqual(result[0]["cex_to_dex_ratio"], 700.0 / 300.0)
        self.assertEqual(result[0]["exchange_count"], 3)
        self.assertEqual(result[0]["pool_count"], 3)
        self.assertEqual(result[0]["selected_chains"], "arbitrum;eth")


if __name__ == "__main__":
    unittest.main()
