"""Build a research panel with realized and future returns.

Input file:
    data/processed/merged_volume_panel.csv

Output file:
    data/processed/research_panel.csv
"""

import csv
from pathlib import Path


MERGED_PANEL_PATH = Path("data/processed/merged_volume_panel.csv")
RESEARCH_PANEL_PATH = Path("data/processed/research_panel.csv")


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


def calculate_return(start_price, end_price):
    """Calculate simple return from start price to end price."""
    if start_price <= 0:
        return ""
    if end_price <= 0:
        return ""
    return (end_price / start_price) - 1


def group_rows_by_token(rows):
    """Group panel rows by token symbol."""
    rows_by_token = {}

    for row in rows:
        token_symbol = row["token_symbol"]

        if token_symbol not in rows_by_token:
            rows_by_token[token_symbol] = []

        rows_by_token[token_symbol].append(row)

    return rows_by_token


def add_return_columns_for_token(token_rows):
    """Add return columns to rows for one token."""
    token_rows = sorted(token_rows, key=lambda row: row["date"])
    prices = [safe_float(row["price_usd"]) for row in token_rows]
    output_rows = []

    for index in range(len(token_rows)):
        row = dict(token_rows[index])
        current_price = prices[index]

        if index >= 1:
            row["return_1d"] = calculate_return(prices[index - 1], current_price)
        else:
            row["return_1d"] = ""

        for horizon in [1, 3, 7]:
            future_index = index + horizon
            column_name = "future_return_%sd" % horizon

            if future_index < len(token_rows):
                row[column_name] = calculate_return(current_price, prices[future_index])
            else:
                row[column_name] = ""

        output_rows.append(row)

    return output_rows


def build_research_panel_rows(merged_rows):
    """Build research panel rows from merged panel rows."""
    rows_by_token = group_rows_by_token(merged_rows)
    output_rows = []

    for token_symbol in sorted(rows_by_token):
        token_rows = add_return_columns_for_token(rows_by_token[token_symbol])
        output_rows.extend(token_rows)

    output_rows = sorted(output_rows, key=lambda row: (row["token_symbol"], row["date"]))

    return output_rows


def build_fieldnames(rows):
    """Build output CSV columns."""
    base_fieldnames = []

    if rows:
        base_fieldnames = list(rows[0].keys())

    return_columns = [
        "return_1d",
        "future_return_1d",
        "future_return_3d",
        "future_return_7d",
    ]

    fieldnames = []

    for fieldname in base_fieldnames:
        if fieldname not in return_columns:
            fieldnames.append(fieldname)

    for column in return_columns:
        fieldnames.append(column)

    return fieldnames


def write_research_panel_rows(rows, path):
    """Write research panel rows to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = build_fieldnames(rows)

    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Build the research panel."""
    merged_rows = read_csv_rows(MERGED_PANEL_PATH)
    research_rows = build_research_panel_rows(merged_rows)
    write_research_panel_rows(research_rows, RESEARCH_PANEL_PATH)

    print("Read %s merged rows from %s" % (len(merged_rows), MERGED_PANEL_PATH))
    print("Wrote %s research rows to %s" % (len(research_rows), RESEARCH_PANEL_PATH))


if __name__ == "__main__":
    main()
