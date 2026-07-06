import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.fetch_dex import choose_main_pool
from scripts.fetch_dex import convert_ohlcv_row
from scripts.fetch_dex import get_retry_wait_seconds
from scripts.fetch_dex import get_token_side
from scripts.fetch_dex import safe_float
from scripts.fetch_dex import sort_pools_by_volume
from scripts.fetch_dex import write_pool_rows


class FetchDexTests(unittest.TestCase):
    def test_safe_float_converts_missing_values_to_zero(self):
        self.assertEqual(safe_float(None), 0.0)
        self.assertEqual(safe_float(""), 0.0)
        self.assertEqual(safe_float("123.45"), 123.45)

    def test_get_retry_wait_seconds_defaults_rate_limit_to_one_minute(self):
        result = get_retry_wait_seconds(429, None)
        self.assertEqual(result, 65)

    def test_choose_main_pool_uses_highest_24h_volume(self):
        pools = [
            {
                "attributes": {
                    "address": "0xsmall",
                    "name": "SMALL / WETH",
                    "reserve_in_usd": "100",
                    "volume_usd": {"h24": "1000"},
                },
                "relationships": {
                    "base_token": {"data": {"id": "eth_0xaaa"}},
                    "quote_token": {"data": {"id": "eth_0xbbb"}},
                    "dex": {"data": {"id": "uniswap_v2"}},
                },
            },
            {
                "attributes": {
                    "address": "0xbig",
                    "name": "BIG / WETH",
                    "reserve_in_usd": "5000",
                    "volume_usd": {"h24": "500"},
                },
                "relationships": {
                    "base_token": {"data": {"id": "eth_0xccc"}},
                    "quote_token": {"data": {"id": "eth_0xddd"}},
                    "dex": {"data": {"id": "uniswap_v3"}},
                },
            },
        ]

        result = choose_main_pool(pools)

        self.assertEqual(result["pool_address"], "0xsmall")
        self.assertEqual(result["dex"], "uniswap_v2")
        self.assertEqual(result["pool_name"], "SMALL / WETH")
        self.assertEqual(result["pool_tvl_usd"], 100.0)
        self.assertEqual(result["volume_24h_usd"], 1000.0)

    def test_get_token_side_detects_quote_token(self):
        pool = {
            "base_token_id": "eth_0xbase",
            "quote_token_id": "eth_0xtarget",
        }

        result = get_token_side(pool, "eth", "0xtarget")

        self.assertEqual(result, "quote")

    def test_sort_pools_by_volume_descending(self):
        pools = [
            {"attributes": {"volume_usd": {"h24": "10"}}},
            {"attributes": {"volume_usd": {"h24": "30"}}},
            {"attributes": {"volume_usd": {"h24": "20"}}},
        ]

        result = sort_pools_by_volume(pools)

        volumes = []
        for pool in result:
            volume = pool["attributes"]["volume_usd"]["h24"]
            volumes.append(volume)

        self.assertEqual(volumes, ["30", "20", "10"])

    def test_convert_ohlcv_row_maps_volume_to_dex_volume(self):
        ohlcv = [
            1704067200,
            7.10,
            7.50,
            7.00,
            7.30,
            7300.0,
        ]

        pool = {
            "token_symbol": "UNI",
            "chain": "eth",
            "dex": "uniswap_v3",
            "pool_address": "0xpool",
            "pool_name": "UNI / WETH",
            "pool_tvl_usd": 1000000.0,
        }

        result = convert_ohlcv_row(ohlcv, pool)

        self.assertEqual(result["date"], "2024-01-01")
        self.assertEqual(result["token_symbol"], "UNI")
        self.assertEqual(result["chain"], "eth")
        self.assertEqual(result["dex"], "uniswap_v3")
        self.assertEqual(result["pool_address"], "0xpool")
        self.assertEqual(result["open"], 7.10)
        self.assertEqual(result["high"], 7.50)
        self.assertEqual(result["low"], 7.00)
        self.assertEqual(result["close"], 7.30)
        self.assertEqual(result["dex_volume_usd"], 7300.0)
        self.assertEqual(result["pool_tvl_usd"], 1000000.0)

    def test_write_pool_rows_accepts_token_id_fields(self):
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "dex_pools.csv"
            pools = [
                {
                    "token_symbol": "UNI",
                    "chain": "eth",
                    "contract_address": "0xtoken",
                    "dex": "uniswap_v3",
                    "pool_address": "0xpool",
                    "pool_name": "UNI / WETH",
                    "pool_tvl_usd": 1000.0,
                    "volume_24h_usd": 100.0,
                    "ohlcv_token": "base",
                    "base_token_id": "eth_0xtoken",
                    "quote_token_id": "eth_0xquote",
                }
            ]

            write_pool_rows(pools, output_path)

            text = output_path.read_text()
            self.assertIn("base_token_id", text)
            self.assertIn("quote_token_id", text)


if __name__ == "__main__":
    unittest.main()
