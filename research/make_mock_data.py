"""Generate mock CEX / DEX daily volume data for research script testing."""

from __future__ import annotations

import argparse
import csv
import math
import random
from datetime import date
from datetime import timedelta
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "mock" / "processed"

TOKENS = ["UNI", "AAVE", "LINK", "ARB", "OP"]
START_DATE = date(2026, 1, 1)
DAY_COUNT = 120


def generate_token_rows(token_symbol: str, token_index: int):
    """Generate deterministic mock rows for one token."""
    random.seed(1000 + token_index)

    price = 10.0 + token_index * 8.0
    cex_level = 20_000_000 * (1 + token_index * 0.4)
    dex_level = 300_000 * (1 + token_index * 0.5)
    cex_rows = []
    dex_rows = []

    for day_number in range(DAY_COUNT):
        current_date = START_DATE + timedelta(days=day_number)
        cycle = math.sin(day_number / 8.0 + token_index)
        slow_cycle = math.sin(day_number / 23.0)
        shock = 1.0

        if day_number in [35 + token_index, 75 - token_index]:
            shock = 3.0 + token_index * 0.2

        daily_return = 0.001 + 0.012 * slow_cycle + random.gauss(0, 0.018)
        price = max(0.05, price * (1 + daily_return))

        cex_volume = cex_level * (1.0 + 0.35 * cycle) * shock
        cex_volume = max(0.0, cex_volume * random.lognormvariate(0, 0.18))

        dex_lead_signal = 1.0
        if day_number in [32 + token_index, 72 - token_index]:
            dex_lead_signal = 4.0 + token_index * 0.2

        dex_volume = dex_level * (1.0 + 0.45 * math.sin(day_number / 8.0 + token_index + 0.7))
        dex_volume = max(0.0, dex_volume * dex_lead_signal * random.lognormvariate(0, 0.25))

        cex_rows.append(
            {
                "date": current_date.isoformat(),
                "token_symbol": token_symbol,
                "close": round(price, 8),
                "cex_volume_usd": round(cex_volume, 4),
                "exchange_count": 3,
                "included_exchanges": "binance;bybit;okx",
            }
        )

        dex_rows.append(
            {
                "date": current_date.isoformat(),
                "token_symbol": token_symbol,
                "chain": "eth",
                "dex": "mock_uniswap_v3",
                "pool_address": "mock_" + token_symbol.lower() + "_pool",
                "pool_name": token_symbol + " / USDC mock",
                "open": round(price * 0.99, 8),
                "high": round(price * 1.02, 8),
                "low": round(price * 0.98, 8),
                "close": round(price, 8),
                "dex_volume_usd": round(dex_volume, 4),
                "pool_tvl_usd": round(dex_level * 20, 4),
            }
        )

    return cex_rows, dex_rows


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    """Write rows to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_mock_data(output_dir: Path = DEFAULT_OUTPUT_DIR) -> None:
    """Generate mock processed inputs for the research layer."""
    cex_output_path = output_dir / "cex_volume_daily.csv"
    dex_output_path = output_dir / "dex_volume_daily.csv"
    all_cex_rows = []
    all_dex_rows = []

    for token_index, token_symbol in enumerate(TOKENS):
        cex_rows, dex_rows = generate_token_rows(token_symbol, token_index)
        all_cex_rows.extend(cex_rows)
        all_dex_rows.extend(dex_rows)

    cex_fieldnames = [
        "date",
        "token_symbol",
        "close",
        "cex_volume_usd",
        "exchange_count",
        "included_exchanges",
    ]
    dex_fieldnames = [
        "date",
        "token_symbol",
        "chain",
        "dex",
        "pool_address",
        "pool_name",
        "open",
        "high",
        "low",
        "close",
        "dex_volume_usd",
        "pool_tvl_usd",
    ]

    write_csv(cex_output_path, all_cex_rows, cex_fieldnames)
    write_csv(dex_output_path, all_dex_rows, dex_fieldnames)

    print("Wrote mock CEX rows:", len(all_cex_rows), cex_output_path)
    print("Wrote mock DEX rows:", len(all_dex_rows), dex_output_path)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for mock cex_volume_daily.csv and dex_volume_daily.csv.",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entrypoint."""
    args = parse_args()
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = PROJECT_ROOT / output_dir
    generate_mock_data(output_dir)


if __name__ == "__main__":
    main()
