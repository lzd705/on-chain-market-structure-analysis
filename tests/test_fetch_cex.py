import unittest

from scripts.fetch_cex import convert_binance_kline
from scripts.fetch_cex import convert_bybit_kline
from scripts.fetch_cex import convert_okx_kline
from scripts.fetch_cex import make_bybit_symbol
from scripts.fetch_cex import make_binance_symbol
from scripts.fetch_cex import make_okx_inst_id
from scripts.fetch_cex import aggregate_cex_rows


class FetchCexTests(unittest.TestCase):
    def test_make_binance_symbol_removes_slash(self):
        result = make_binance_symbol("UNI/USDT")
        self.assertEqual(result, "UNIUSDT")

    def test_make_okx_inst_id_replaces_slash_with_dash(self):
        result = make_okx_inst_id("UNI/USDT")
        self.assertEqual(result, "UNI-USDT")

    def test_make_bybit_symbol_removes_slash(self):
        result = make_bybit_symbol("UNI/USDT")
        self.assertEqual(result, "UNIUSDT")

    def test_convert_binance_kline_uses_quote_volume(self):
        kline = [
            1704067200000,
            "7.10",
            "7.50",
            "7.00",
            "7.30",
            "1000",
            1704153599999,
            "7300",
            123,
            "500",
            "3650",
            "0",
        ]

        result = convert_binance_kline(kline, "UNI", "UNI/USDT", "binance")

        self.assertEqual(result["date"], "2024-01-01")
        self.assertEqual(result["token_symbol"], "UNI")
        self.assertEqual(result["exchange"], "binance")
        self.assertEqual(result["cex_symbol"], "UNI/USDT")
        self.assertEqual(result["open"], 7.10)
        self.assertEqual(result["high"], 7.50)
        self.assertEqual(result["low"], 7.00)
        self.assertEqual(result["close"], 7.30)
        self.assertEqual(result["base_volume"], 1000.0)
        self.assertEqual(result["quote_volume_usd"], 7300.0)

    def test_convert_okx_kline_uses_quote_volume(self):
        kline = [
            "1704067200000",
            "7.10",
            "7.50",
            "7.00",
            "7.30",
            "1000",
            "7300",
            "7300",
            "1",
        ]

        result = convert_okx_kline(kline, "UNI", "UNI/USDT")

        self.assertEqual(result["date"], "2024-01-01")
        self.assertEqual(result["exchange"], "okx")
        self.assertEqual(result["base_volume"], 1000.0)
        self.assertEqual(result["quote_volume_usd"], 7300.0)

    def test_convert_bybit_kline_uses_turnover_as_quote_volume(self):
        kline = [
            "1704067200000",
            "7.10",
            "7.50",
            "7.00",
            "7.30",
            "1000",
            "7300",
        ]

        result = convert_bybit_kline(kline, "UNI", "UNI/USDT")

        self.assertEqual(result["date"], "2024-01-01")
        self.assertEqual(result["exchange"], "bybit")
        self.assertEqual(result["base_volume"], 1000.0)
        self.assertEqual(result["quote_volume_usd"], 7300.0)

    def test_aggregate_cex_rows_sums_volume_and_keeps_binance_close(self):
        rows = [
            {
                "date": "2024-01-01",
                "token_symbol": "UNI",
                "exchange": "binance",
                "close": 7.30,
                "quote_volume_usd": 100.0,
            },
            {
                "date": "2024-01-01",
                "token_symbol": "UNI",
                "exchange": "okx",
                "close": 7.31,
                "quote_volume_usd": 200.0,
            },
            {
                "date": "2024-01-01",
                "token_symbol": "UNI",
                "exchange": "bybit",
                "close": 7.32,
                "quote_volume_usd": 300.0,
            },
        ]

        result = aggregate_cex_rows(rows)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["date"], "2024-01-01")
        self.assertEqual(result[0]["token_symbol"], "UNI")
        self.assertEqual(result[0]["close"], 7.30)
        self.assertEqual(result[0]["cex_volume_usd"], 600.0)
        self.assertEqual(result[0]["exchange_count"], 3)
        self.assertEqual(result[0]["included_exchanges"], "binance;bybit;okx")


if __name__ == "__main__":
    unittest.main()
