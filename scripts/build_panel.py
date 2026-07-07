"""Build the merged CEX / DEX daily volume panel.

Input files:
    data/processed/cex_volume_daily.csv
    data/processed/dex_volume_daily.csv

Output file:
    data/processed/merged_volume_panel.csv
"""

import csv
from pathlib import Path


CEX_VOLUME_PATH = Path("data/processed/cex_volume_daily.csv")
DEX_VOLUME_PATH = Path("data/processed/dex_volume_daily.csv")
MERGED_PANEL_PATH = Path("data/processed/merged_volume_panel.csv")


def safe_float(value):
    """Convert a CSV value to float."""
    if value is None:
        return 0.0
    if value == "":
        return 0.0
    return float(value)


def safe_int(value):
    """Convert a CSV value to int."""
    if value is None:
        return 0
    if value == "":
        return 0
    return int(value)


def read_csv_rows(path):
    """Read a CSV file into a list of dictionaries."""
    with path.open("r", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    return rows


def build_dex_index(dex_rows):
    """Build lookup table for DEX rows by date and token."""
    index = {}

    for row in dex_rows:
        key = (row["date"], row["token_symbol"])
        index[key] = row

    return index


def calculate_ratio(numerator, denominator):
    """Calculate a ratio and return 0 when denominator is zero."""
    if denominator == 0:
        return 0.0
    return numerator / denominator


def merge_volume_rows(cex_rows, dex_rows):
    """Inner join CEX and DEX daily volume rows."""
    dex_index = build_dex_index(dex_rows)
    merged_rows = []

    for cex_row in cex_rows:
        key = (cex_row["date"], cex_row["token_symbol"])

        if key not in dex_index:
            continue

        dex_row = dex_index[key]

        cex_volume_usd = safe_float(cex_row["cex_volume_usd"])
        dex_volume_usd = safe_float(dex_row["dex_volume_usd"])
        total_volume_usd = cex_volume_usd + dex_volume_usd

        merged_row = {
            "date": cex_row["date"],
            "token_symbol": cex_row["token_symbol"],
            "price_usd": safe_float(cex_row["close"]),
            "cex_volume_usd": cex_volume_usd,
            "dex_volume_usd": dex_volume_usd,
            "total_volume_usd": total_volume_usd,
            "dex_share": calculate_ratio(dex_volume_usd, total_volume_usd),
            "cex_to_dex_ratio": calculate_ratio(cex_volume_usd, dex_volume_usd),
            "exchange_count": safe_int(cex_row["exchange_count"]),
            "included_exchanges": cex_row["included_exchanges"],
            "chain": dex_row["chain"],
            "selected_chains": dex_row.get("selected_chains", dex_row["chain"]),
            "pool_count": safe_int(dex_row["pool_count"]),
            "included_dexes": dex_row["included_dexes"],
            "included_pool_addresses": dex_row["included_pool_addresses"],
        }

        merged_rows.append(merged_row)

    merged_rows = sorted(merged_rows, key=lambda row: (row["token_symbol"], row["date"]))

    return merged_rows


def write_merged_rows(rows, path):
    """Write merged panel rows to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "date",
        "token_symbol",
        "price_usd",
        "cex_volume_usd",
        "dex_volume_usd",
        "total_volume_usd",
        "dex_share",
        "cex_to_dex_ratio",
        "exchange_count",
        "included_exchanges",
        "chain",
        "selected_chains",
        "pool_count",
        "included_dexes",
        "included_pool_addresses",
    ]

    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Build the merged panel."""
    cex_rows = read_csv_rows(CEX_VOLUME_PATH)
    dex_rows = read_csv_rows(DEX_VOLUME_PATH)
    merged_rows = merge_volume_rows(cex_rows, dex_rows)
    write_merged_rows(merged_rows, MERGED_PANEL_PATH)

    print("Read %s CEX rows from %s" % (len(cex_rows), CEX_VOLUME_PATH))
    print("Read %s DEX rows from %s" % (len(dex_rows), DEX_VOLUME_PATH))
    print("Wrote %s merged rows to %s" % (len(merged_rows), MERGED_PANEL_PATH))


if __name__ == "__main__":
    main()
