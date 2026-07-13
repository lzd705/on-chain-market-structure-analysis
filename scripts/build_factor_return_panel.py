"""Merge factor values with realized and future returns.

Input files:
    data/processed/factor_table.csv
    data/processed/research_panel.csv

Output file:
    data/processed/factor_return_panel.csv
"""

import csv
from pathlib import Path


FACTOR_TABLE_PATH = Path("data/processed/factor_table.csv")
RESEARCH_PANEL_PATH = Path("data/processed/research_panel.csv")
FACTOR_RETURN_PANEL_PATH = Path("data/processed/factor_return_panel.csv")


def read_csv_rows(path):
    """Read a CSV file into a list of dictionaries."""
    with path.open("r", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    return rows


def build_research_index(research_rows):
    """Build lookup table for research rows by date and token."""
    index = {}

    for row in research_rows:
        key = (row["date"], row["token_symbol"])
        index[key] = row

    return index


def build_factor_return_panel_rows(factor_rows, research_rows):
    """Join factor rows to research panel rows."""
    research_index = build_research_index(research_rows)
    output_rows = []

    for factor_row in factor_rows:
        key = (factor_row["date"], factor_row["token_symbol"])

        if key not in research_index:
            continue

        research_row = research_index[key]
        output_row = {
            "date": factor_row["date"],
            "token_symbol": factor_row["token_symbol"],
            "factor_name": factor_row["factor_name"],
            "factor_value": factor_row["factor_value"],
            "lookback_window": factor_row["lookback_window"],
            "factor_data_source": factor_row["data_source"],
            "price_usd": research_row["price_usd"],
            "cex_volume_usd": research_row["cex_volume_usd"],
            "dex_volume_usd": research_row["dex_volume_usd"],
            "dex_share": research_row["dex_share"],
            "return_1d": research_row["return_1d"],
            "future_return_1d": research_row["future_return_1d"],
            "future_return_3d": research_row["future_return_3d"],
            "future_return_7d": research_row["future_return_7d"],
        }
        output_rows.append(output_row)

    output_rows = sorted(
        output_rows,
        key=lambda row: (row["date"], row["token_symbol"], row["factor_name"]),
    )

    return output_rows


def write_factor_return_panel_rows(rows, path):
    """Write factor return panel rows to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "date",
        "token_symbol",
        "factor_name",
        "factor_value",
        "lookback_window",
        "factor_data_source",
        "price_usd",
        "cex_volume_usd",
        "dex_volume_usd",
        "dex_share",
        "return_1d",
        "future_return_1d",
        "future_return_3d",
        "future_return_7d",
    ]

    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Build the factor return panel."""
    factor_rows = read_csv_rows(FACTOR_TABLE_PATH)
    research_rows = read_csv_rows(RESEARCH_PANEL_PATH)
    output_rows = build_factor_return_panel_rows(factor_rows, research_rows)
    write_factor_return_panel_rows(output_rows, FACTOR_RETURN_PANEL_PATH)

    print("Read %s factor rows from %s" % (len(factor_rows), FACTOR_TABLE_PATH))
    print("Read %s research rows from %s" % (len(research_rows), RESEARCH_PANEL_PATH))
    print("Wrote %s factor return rows to %s" % (len(output_rows), FACTOR_RETURN_PANEL_PATH))


if __name__ == "__main__":
    main()
