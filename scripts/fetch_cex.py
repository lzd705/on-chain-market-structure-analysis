"""Fetch daily CEX OHLCV and volume data from Binance.

This first version is intentionally simple:
    - Read token symbols from config/tokens.csv
    - Fetch Binance 1d klines
    - Write data/processed/cex_volume_daily.csv
"""

import csv
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime
from datetime import timezone
from pathlib import Path


TOKEN_CONFIG_PATH = Path("config/tokens.csv")
OUTPUT_PATH = Path("data/processed/cex_volume_daily.csv")
LIMIT_DAYS = 180

BINANCE_BASE_URLS = [
    "https://api.binance.com",
    "https://data-api.binance.vision",
]


def make_binance_symbol(cex_symbol: str) -> str:
    """Convert UNI/USDT to UNIUSDT for Binance REST API."""
    return cex_symbol.replace("/", "").upper()


def convert_binance_kline(kline, token_symbol: str, cex_symbol: str, exchange: str):
    """Convert one Binance kline list into one output CSV row."""
    open_time_ms = int(kline[0])
    date = datetime.fromtimestamp(open_time_ms / 1000, timezone.utc).strftime("%Y-%m-%d")

    row = {
        "date": date,
        "token_symbol": token_symbol,
        "exchange": exchange,
        "cex_symbol": cex_symbol,
        "open": float(kline[1]),
        "high": float(kline[2]),
        "low": float(kline[3]),
        "close": float(kline[4]),
        "base_volume": float(kline[5]),
        "quote_volume_usd": float(kline[7]),
    }

    return row


def read_token_config(path: Path):
    """Read token config rows."""
    with path.open("r", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    return rows


def fetch_binance_klines(binance_symbol: str, limit_days: int):
    """Fetch daily klines from Binance."""
    query = {
        "symbol": binance_symbol,
        "interval": "1d",
        "limit": str(limit_days),
    }

    encoded_query = urllib.parse.urlencode(query)
    last_error = None

    for base_url in BINANCE_BASE_URLS:
        url = base_url + "/api/v3/klines?" + encoded_query

        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                text = response.read().decode("utf-8")
                data = json.loads(text)
                return data
        except Exception as error:
            last_error = error

    raise RuntimeError("Failed to fetch %s: %s" % (binance_symbol, last_error))


def build_rows(token_rows):
    """Fetch all Binance rows for configured tokens."""
    all_rows = []

    for token in token_rows:
        token_symbol = token["token_symbol"]
        cex_symbol = token["cex_symbol"]
        primary_cex = token["primary_cex"]

        if primary_cex != "binance":
            print("Skipping %s because primary_cex is %s" % (token_symbol, primary_cex))
            continue

        binance_symbol = make_binance_symbol(cex_symbol)

        try:
            klines = fetch_binance_klines(binance_symbol, LIMIT_DAYS)
        except Exception as error:
            print("Failed %s: %s" % (token_symbol, error))
            continue

        for kline in klines:
            row = convert_binance_kline(kline, token_symbol, cex_symbol, "binance")
            all_rows.append(row)

        print("Fetched %s: %s rows" % (token_symbol, len(klines)))
        time.sleep(0.2)

    return all_rows


def write_rows(rows, output_path: Path):
    """Write output CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "date",
        "token_symbol",
        "exchange",
        "cex_symbol",
        "open",
        "high",
        "low",
        "close",
        "base_volume",
        "quote_volume_usd",
    ]

    with output_path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Fetch CEX data into data/processed/cex_volume_daily.csv."""
    token_rows = read_token_config(TOKEN_CONFIG_PATH)
    rows = build_rows(token_rows)
    write_rows(rows, OUTPUT_PATH)
    print("Wrote %s rows to %s" % (len(rows), OUTPUT_PATH))


if __name__ == "__main__":
    main()
