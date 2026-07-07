"""Build factor rows from the merged CEX / DEX volume panel.

Input file:
    data/processed/merged_volume_panel.csv

Output file:
    data/processed/factor_table.csv
"""

import csv
import math
from pathlib import Path


MERGED_PANEL_PATH = Path("data/processed/merged_volume_panel.csv")
FACTOR_TABLE_PATH = Path("data/processed/factor_table.csv")


def safe_float(value):
    """Convert a CSV value to float."""
    if value is None:
        return 0.0
    if value == "":
        return 0.0
    return float(value)


def read_csv_rows(path):
    """Read a CSV file into a list of dictionaries."""
    with path.open("r", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    return rows


def calculate_log_ratio(current_value, past_value):
    """Calculate log(current / past), returning None for invalid values."""
    if current_value <= 0:
        return None
    if past_value <= 0:
        return None
    return math.log(current_value / past_value)


def calculate_zscore(values):
    """Calculate the z-score of the last value in a list."""
    if len(values) == 0:
        return None

    mean = sum(values) / len(values)
    variance = 0.0

    for value in values:
        variance += (value - mean) ** 2

    variance = variance / len(values)
    std = math.sqrt(variance)

    if std == 0:
        return 0.0

    return (values[-1] - mean) / std


def add_factor(rows, date, token_symbol, factor_name, factor_value, lookback_window):
    """Append one factor row if the factor value is available."""
    if factor_value is None:
        return

    rows.append(
        {
            "date": date,
            "token_symbol": token_symbol,
            "factor_name": factor_name,
            "factor_value": factor_value,
            "lookback_window": lookback_window,
            "data_source": "merged_volume_panel",
        }
    )


def build_token_factor_rows(token_rows):
    """Build factor rows for one token."""
    factor_rows = []
    token_rows = sorted(token_rows, key=lambda row: row["date"])

    dates = [row["date"] for row in token_rows]
    token_symbol = token_rows[0]["token_symbol"]
    prices = [safe_float(row["price_usd"]) for row in token_rows]
    cex_volumes = [safe_float(row["cex_volume_usd"]) for row in token_rows]
    dex_volumes = [safe_float(row["dex_volume_usd"]) for row in token_rows]
    dex_shares = [safe_float(row["dex_share"]) for row in token_rows]

    cex_growth_7d = [None] * len(token_rows)
    dex_growth_7d = [None] * len(token_rows)
    cex_vol_z_30d = [None] * len(token_rows)

    for index in range(len(token_rows)):
        date = dates[index]

        add_factor(factor_rows, date, token_symbol, "DEX_SHARE", dex_shares[index], "1d")

        for window in [7, 14, 30]:
            if index >= window:
                factor_value = calculate_log_ratio(prices[index], prices[index - window])
                add_factor(factor_rows, date, token_symbol, "MOM_%sD" % window, factor_value, "%sd" % window)

        if index >= 8:
            factor_value = calculate_log_ratio(prices[index - 1], prices[index - 8])
            add_factor(factor_rows, date, token_symbol, "MOM_7D_SKIP_1D", factor_value, "7d_skip_1d")

        if index >= 13:
            current_cex_volume = sum(cex_volumes[index - 6 : index + 1])
            previous_cex_volume = sum(cex_volumes[index - 13 : index - 6])
            current_dex_volume = sum(dex_volumes[index - 6 : index + 1])
            previous_dex_volume = sum(dex_volumes[index - 13 : index - 6])

            cex_growth_7d[index] = calculate_log_ratio(current_cex_volume, previous_cex_volume)
            dex_growth_7d[index] = calculate_log_ratio(current_dex_volume, previous_dex_volume)

            add_factor(
                factor_rows,
                date,
                token_symbol,
                "CEX_VOL_GROWTH_7D",
                cex_growth_7d[index],
                "7d_vs_prev_7d",
            )
            add_factor(
                factor_rows,
                date,
                token_symbol,
                "DEX_VOL_GROWTH_7D",
                dex_growth_7d[index],
                "7d_vs_prev_7d",
            )

        if index >= 29:
            cex_logs = [math.log(1 + value) for value in cex_volumes[index - 29 : index + 1]]
            dex_logs = [math.log(1 + value) for value in dex_volumes[index - 29 : index + 1]]

            cex_vol_z_30d[index] = calculate_zscore(cex_logs)
            dex_vol_z_30d = calculate_zscore(dex_logs)

            add_factor(factor_rows, date, token_symbol, "CEX_VOL_Z_30D", cex_vol_z_30d[index], "30d")
            add_factor(factor_rows, date, token_symbol, "DEX_VOL_Z_30D", dex_vol_z_30d, "30d")

        if index >= 7 and cex_vol_z_30d[index] is not None:
            mom_7d = calculate_log_ratio(prices[index], prices[index - 7])
            factor_value = mom_7d * cex_vol_z_30d[index]
            add_factor(factor_rows, date, token_symbol, "CEX_VOLUME_CONFIRMED_MOM", factor_value, "7d_price_30d_volume")

        if index >= 42:
            cex_growth_window = cex_growth_7d[index - 29 : index + 1]
            dex_growth_window = dex_growth_7d[index - 29 : index + 1]

            if None not in cex_growth_window and None not in dex_growth_window:
                cex_growth_z = calculate_zscore(cex_growth_window)
                dex_growth_z = calculate_zscore(dex_growth_window)
                factor_value = dex_growth_z - cex_growth_z
                add_factor(factor_rows, date, token_symbol, "VOL_DIVERGENCE", factor_value, "7d_growth_30d_z")

    return factor_rows


def group_rows_by_token(panel_rows):
    """Group merged panel rows by token symbol."""
    rows_by_token = {}

    for row in panel_rows:
        token_symbol = row["token_symbol"]

        if token_symbol not in rows_by_token:
            rows_by_token[token_symbol] = []

        rows_by_token[token_symbol].append(row)

    return rows_by_token


def build_factor_rows(panel_rows):
    """Build long-format factor rows from merged panel rows."""
    rows_by_token = group_rows_by_token(panel_rows)
    factor_rows = []

    for token_symbol in sorted(rows_by_token):
        token_factor_rows = build_token_factor_rows(rows_by_token[token_symbol])
        factor_rows.extend(token_factor_rows)

    factor_rows = sorted(
        factor_rows,
        key=lambda row: (row["token_symbol"], row["date"], row["factor_name"]),
    )

    return factor_rows


def write_factor_rows(rows, path):
    """Write factor rows to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "date",
        "token_symbol",
        "factor_name",
        "factor_value",
        "lookback_window",
        "data_source",
    ]

    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Build factor table."""
    panel_rows = read_csv_rows(MERGED_PANEL_PATH)
    factor_rows = build_factor_rows(panel_rows)
    write_factor_rows(factor_rows, FACTOR_TABLE_PATH)

    print("Read %s panel rows from %s" % (len(panel_rows), MERGED_PANEL_PATH))
    print("Wrote %s factor rows to %s" % (len(factor_rows), FACTOR_TABLE_PATH))


if __name__ == "__main__":
    main()
