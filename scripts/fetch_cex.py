"""Fetch daily CEX OHLCV and volume data.

This version is intentionally simple:
    - Read token symbols from config/tokens.csv
    - Fetch Binance, OKX, and Bybit 1d klines
    - Write exchange-level rows to data/processed/cex_exchange_volume_daily.csv
    - Write aggregated token-date rows to data/processed/cex_volume_daily.csv
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
EXCHANGE_OUTPUT_PATH = Path("data/processed/cex_exchange_volume_daily.csv")
OUTPUT_PATH = Path("data/processed/cex_volume_daily.csv")
LIMIT_DAYS = 180

BINANCE_BASE_URLS = [
    "https://api.binance.com",
    "https://data-api.binance.vision",
]

EXCHANGES = ["binance", "okx", "bybit"]


def make_binance_symbol(cex_symbol: str) -> str:
    """Convert UNI/USDT to UNIUSDT for Binance REST API."""
    return cex_symbol.replace("/", "").upper()


def make_okx_inst_id(cex_symbol: str) -> str:
    """Convert UNI/USDT to UNI-USDT for OKX REST API."""
    return cex_symbol.replace("/", "-").upper()


def make_bybit_symbol(cex_symbol: str) -> str:
    """Convert UNI/USDT to UNIUSDT for Bybit REST API."""
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


def convert_okx_kline(kline, token_symbol: str, cex_symbol: str):
    """Convert one OKX kline list into one output CSV row."""
    open_time_ms = int(kline[0])
    date = datetime.fromtimestamp(open_time_ms / 1000, timezone.utc).strftime("%Y-%m-%d")

    row = {
        "date": date,
        "token_symbol": token_symbol,
        "exchange": "okx",
        "cex_symbol": cex_symbol,
        "open": float(kline[1]),
        "high": float(kline[2]),
        "low": float(kline[3]),
        "close": float(kline[4]),
        "base_volume": float(kline[5]),
        "quote_volume_usd": float(kline[7]),
    }

    return row


def convert_bybit_kline(kline, token_symbol: str, cex_symbol: str):
    """Convert one Bybit kline list into one output CSV row."""
    open_time_ms = int(kline[0])
    date = datetime.fromtimestamp(open_time_ms / 1000, timezone.utc).strftime("%Y-%m-%d")

    row = {
        "date": date,
        "token_symbol": token_symbol,
        "exchange": "bybit",
        "cex_symbol": cex_symbol,
        "open": float(kline[1]),
        "high": float(kline[2]),
        "low": float(kline[3]),
        "close": float(kline[4]),
        "base_volume": float(kline[5]),
        "quote_volume_usd": float(kline[6]),
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


def request_json(url: str):
    """Request JSON with a basic User-Agent."""
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    with urllib.request.urlopen(request, timeout=30) as response:
        text = response.read().decode("utf-8")
        data = json.loads(text)

    return data


def fetch_okx_klines(inst_id: str, limit_days: int):
    """Fetch daily klines from OKX."""
    query = {
        "instId": inst_id,
        "bar": "1Dutc",
        "limit": str(limit_days),
    }

    encoded_query = urllib.parse.urlencode(query)
    url = "https://www.okx.com/api/v5/market/candles?" + encoded_query

    data = request_json(url)

    if data.get("code") != "0":
        raise RuntimeError("OKX error for %s: %s" % (inst_id, data))

    return data.get("data", [])


def fetch_bybit_klines(symbol: str, limit_days: int):
    """Fetch daily klines from Bybit."""
    query = {
        "category": "spot",
        "symbol": symbol,
        "interval": "D",
        "limit": str(limit_days),
    }

    encoded_query = urllib.parse.urlencode(query)
    url = "https://api.bybit.com/v5/market/kline?" + encoded_query

    data = request_json(url)

    if data.get("retCode") != 0:
        raise RuntimeError("Bybit error for %s: %s" % (symbol, data))

    result = data.get("result", {})
    return result.get("list", [])


def fetch_exchange_rows(token_symbol: str, cex_symbol: str, exchange: str):
    """Fetch rows for one token on one exchange."""
    if exchange == "binance":
        binance_symbol = make_binance_symbol(cex_symbol)
        klines = fetch_binance_klines(binance_symbol, LIMIT_DAYS)
        rows = []

        for kline in klines:
            row = convert_binance_kline(kline, token_symbol, cex_symbol, "binance")
            rows.append(row)

        return rows

    if exchange == "okx":
        inst_id = make_okx_inst_id(cex_symbol)
        klines = fetch_okx_klines(inst_id, LIMIT_DAYS)
        rows = []

        for kline in klines:
            row = convert_okx_kline(kline, token_symbol, cex_symbol)
            rows.append(row)

        return rows

    if exchange == "bybit":
        symbol = make_bybit_symbol(cex_symbol)
        klines = fetch_bybit_klines(symbol, LIMIT_DAYS)
        rows = []

        for kline in klines:
            row = convert_bybit_kline(kline, token_symbol, cex_symbol)
            rows.append(row)

        return rows

    raise ValueError("Unsupported exchange: %s" % exchange)


def build_rows(token_rows):
    """Fetch all CEX rows for configured tokens."""
    all_rows = []

    for token in token_rows:
        token_symbol = token["token_symbol"]
        cex_symbol = token["cex_symbol"]

        for exchange in EXCHANGES:
            try:
                rows = fetch_exchange_rows(token_symbol, cex_symbol, exchange)
            except Exception as error:
                print("Failed %s on %s: %s" % (token_symbol, exchange, error))
                continue

            all_rows.extend(rows)

            print("Fetched %s on %s: %s rows" % (token_symbol, exchange, len(rows)))
            time.sleep(0.2)

    return all_rows


def aggregate_cex_rows(rows):
    """Aggregate exchange-level rows into token-date CEX volume rows."""
    grouped_rows = {}

    for row in rows:
        key = (row["date"], row["token_symbol"])

        if key not in grouped_rows:
            grouped_rows[key] = {
                "date": row["date"],
                "token_symbol": row["token_symbol"],
                "close": None,
                "cex_volume_usd": 0.0,
                "exchanges": set(),
            }

        grouped = grouped_rows[key]
        grouped["cex_volume_usd"] = grouped["cex_volume_usd"] + row["quote_volume_usd"]
        grouped["exchanges"].add(row["exchange"])

        if row["exchange"] == "binance":
            grouped["close"] = row["close"]

    output_rows = []

    for key in sorted(grouped_rows.keys()):
        grouped = grouped_rows[key]
        exchanges = sorted(grouped["exchanges"])

        output_row = {
            "date": grouped["date"],
            "token_symbol": grouped["token_symbol"],
            "close": grouped["close"],
            "cex_volume_usd": grouped["cex_volume_usd"],
            "exchange_count": len(exchanges),
            "included_exchanges": ";".join(exchanges),
        }

        output_rows.append(output_row)

    return output_rows


def write_exchange_rows(rows, output_path: Path):
    """Write exchange-level output CSV."""
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

    rows = sorted(rows, key=lambda row: (row["token_symbol"], row["exchange"], row["date"]))

    with output_path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_aggregated_rows(rows, output_path: Path):
    """Write token-date aggregated CEX output CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "date",
        "token_symbol",
        "close",
        "cex_volume_usd",
        "exchange_count",
        "included_exchanges",
    ]

    with output_path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Fetch CEX data into processed CSV files."""
    token_rows = read_token_config(TOKEN_CONFIG_PATH)
    rows = build_rows(token_rows)
    aggregated_rows = aggregate_cex_rows(rows)

    write_exchange_rows(rows, EXCHANGE_OUTPUT_PATH)
    write_aggregated_rows(aggregated_rows, OUTPUT_PATH)

    print("Wrote %s rows to %s" % (len(rows), EXCHANGE_OUTPUT_PATH))
    print("Wrote %s rows to %s" % (len(aggregated_rows), OUTPUT_PATH))


if __name__ == "__main__":
    main()
