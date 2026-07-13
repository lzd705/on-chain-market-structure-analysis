"""Build the standardized event table from curated candidate records.

The first version does not require an event API. Researchers add source-backed
records to data/curated/event_candidates.csv, then this script validates and
normalizes them for the research pipeline.
"""

import csv
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from datetime import timezone
from pathlib import Path


TOKEN_CONFIG_PATH = Path("config/tokens.csv")
CANDIDATE_PATH = Path("data/curated/event_candidates.csv")
OUTPUT_PATH = Path("data/processed/event_table.csv")

PANEL_START = date(2026, 1, 9)
PANEL_END = date(2026, 7, 5)

ALLOWED_EVENT_TYPES = {
    "unlock",
    "airdrop",
    "cex_listing",
}

ALLOWED_CONFIDENCE = {
    "low",
    "medium",
    "high",
}

NUMERIC_FIELDS = [
    "event_size_token",
    "event_size_usd",
    "event_size_supply_pct",
]

OUTPUT_FIELDS = [
    "token_id",
    "event_type",
    "event_time",
    "event_name",
    "event_window_start",
    "event_window_end",
    "event_size_token",
    "event_size_usd",
    "event_size_supply_pct",
    "source",
    "secondary_source",
    "confidence",
    "is_analysis_eligible",
    "notes",
]


def read_allowed_tokens(path):
    """Read token symbols from config/tokens.csv."""
    tokens = set()

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            token_symbol = row.get("token_symbol", "").strip().upper()
            if token_symbol:
                tokens.add(token_symbol)

    return tokens


def read_candidate_rows(path):
    """Read curated event candidates from CSV."""
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def parse_event_time(value):
    """Parse a date or timezone-aware timestamp and return UTC."""
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("event_time is required")

    try:
        if len(cleaned) == 10:
            parsed_date = date.fromisoformat(cleaned)
            return datetime.combine(parsed_date, time.min, timezone.utc)

        iso_value = cleaned
        if iso_value.endswith("Z"):
            iso_value = iso_value[:-1] + "+00:00"

        parsed_time = datetime.fromisoformat(iso_value)
    except ValueError as error:
        raise ValueError("event_time must be an ISO-8601 date or timestamp") from error

    if parsed_time.tzinfo is None:
        raise ValueError("event_time timestamp must include a timezone")

    return parsed_time.astimezone(timezone.utc)


def validate_number(row, field_name):
    """Validate one optional non-negative numeric field."""
    value = row.get(field_name, "").strip()
    if not value:
        return ""

    try:
        number = float(value)
    except ValueError as error:
        raise ValueError(field_name + " must be numeric or blank") from error

    if number < 0:
        raise ValueError(field_name + " cannot be negative")

    return value


def validate_url(value, field_name, required=False):
    """Validate one source URL."""
    cleaned = value.strip()
    if not cleaned:
        if required:
            raise ValueError(field_name + " is required")
        return ""

    if not cleaned.startswith("https://") and not cleaned.startswith("http://"):
        raise ValueError(field_name + " must be an http or https URL")

    return cleaned


def build_event_rows(candidate_rows, allowed_tokens, panel_start, panel_end):
    """Validate, normalize, de-duplicate, and sort event candidates."""
    output_rows = []
    seen_events = set()

    for row_number, candidate in enumerate(candidate_rows, start=2):
        try:
            token_id = candidate.get("token_id", "").strip().upper()
            event_type = candidate.get("event_type", "").strip().lower()
            event_name = candidate.get("event_name", "").strip()
            source = validate_url(candidate.get("source", ""), "source", required=True)
            secondary_source = validate_url(
                candidate.get("secondary_source", ""),
                "secondary_source",
            )
            confidence = candidate.get("confidence", "").strip().lower()

            if token_id not in allowed_tokens:
                raise ValueError("token_id is not in config/tokens.csv")
            if event_type not in ALLOWED_EVENT_TYPES:
                raise ValueError("event_type is not supported")
            if not event_name:
                raise ValueError("event_name is required")
            if confidence and confidence not in ALLOWED_CONFIDENCE:
                raise ValueError("confidence must be low, medium, high, or blank")

            parsed_time = parse_event_time(candidate.get("event_time", ""))
            event_date = parsed_time.date()
            if event_date < panel_start or event_date > panel_end:
                raise ValueError("event_time is outside the panel date range")

            numeric_values = {}
            for field_name in NUMERIC_FIELDS:
                numeric_values[field_name] = validate_number(candidate, field_name)

            event_time = parsed_time.isoformat(timespec="seconds").replace("+00:00", "Z")
            duplicate_key = (
                token_id,
                event_type,
                event_time,
                event_name.casefold(),
            )
            if duplicate_key in seen_events:
                continue
            seen_events.add(duplicate_key)

            window_start = event_date - timedelta(days=7)
            window_end = event_date + timedelta(days=14)
            is_eligible = window_start >= panel_start and window_end <= panel_end

            output_row = {
                "token_id": token_id,
                "event_type": event_type,
                "event_time": event_time,
                "event_name": event_name,
                "event_window_start": window_start.isoformat(),
                "event_window_end": window_end.isoformat(),
                "event_size_token": numeric_values["event_size_token"],
                "event_size_usd": numeric_values["event_size_usd"],
                "event_size_supply_pct": numeric_values["event_size_supply_pct"],
                "source": source,
                "secondary_source": secondary_source,
                "confidence": confidence,
                "is_analysis_eligible": "1" if is_eligible else "0",
                "notes": candidate.get("notes", "").strip(),
            }
            output_rows.append(output_row)
        except ValueError as error:
            raise ValueError("candidate CSV row " + str(row_number) + ": " + str(error)) from error

    output_rows.sort(
        key=lambda row: (
            row["event_time"],
            row["token_id"],
            row["event_type"],
        )
    )
    return output_rows


def write_event_rows(rows, path):
    """Write the processed event table."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    """Build data/processed/event_table.csv."""
    allowed_tokens = read_allowed_tokens(TOKEN_CONFIG_PATH)
    candidate_rows = read_candidate_rows(CANDIDATE_PATH)
    event_rows = build_event_rows(
        candidate_rows,
        allowed_tokens,
        PANEL_START,
        PANEL_END,
    )
    write_event_rows(event_rows, OUTPUT_PATH)
    print("Wrote " + str(len(event_rows)) + " event rows to " + str(OUTPUT_PATH))


if __name__ == "__main__":
    main()
