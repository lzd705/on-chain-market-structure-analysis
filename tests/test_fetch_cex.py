import unittest

from scripts.fetch_cex import convert_binance_kline
from scripts.fetch_cex import make_binance_symbol


class FetchCexTests(unittest.TestCase):
    def test_make_binance_symbol_removes_slash(self):
        result = make_binance_symbol("UNI/USDT")
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


if __name__ == "__main__":
    unittest.main()
