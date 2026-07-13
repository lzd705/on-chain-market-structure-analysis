# Event Collection Design

## Goal

Build a reproducible event table for the ten configured tokens without requiring a paid API. The first version covers token unlocks, airdrops, and CEX listings between 2026-01-09 and 2026-07-05.

## Source strategy

Event discovery and source verification are curated because the project has no event API key. Each candidate must cite a source URL. Official project tokenomics, official project announcements, and official exchange announcements are preferred. A reliable event database may be stored as a secondary source, but it does not replace the primary source when one is available.

The curated candidate file is committed so another researcher can audit or extend it. The processing script does not scrape changing web pages. If an API is added later, its output can be converted into the same candidate columns and reuse the rest of the pipeline.

## Files

- `data/curated/event_candidates.csv`: human-verifiable source records.
- `scripts/build_event_table.py`: validation, normalization, de-duplication, event-window calculation, and CSV output.
- `data/processed/event_table.csv`: standardized event table used by research code.
- `tests/test_build_event_table.py`: behavior tests.

## Candidate schema

Required fields:

- `token_id`
- `event_type`
- `event_time`
- `event_name`
- `source`

Optional fields:

- `event_size_token`
- `event_size_usd`
- `event_size_supply_pct`
- `secondary_source`
- `confidence`
- `notes`

Allowed event types are `unlock`, `airdrop`, and `cex_listing`. Event timestamps use ISO-8601 UTC. Unknown numeric values remain blank rather than being estimated.

## Processing rules

1. Read the allowed token symbols from `config/tokens.csv`.
2. Reject rows with an unknown token, unsupported event type, invalid timestamp, missing source, or event date outside the full panel range.
3. Normalize timestamps to UTC.
4. De-duplicate by token, event type, UTC timestamp, and normalized event name.
5. Calculate `event_window_start = event_date - 7 days` and `event_window_end = event_date + 14 days`.
6. Set `is_analysis_eligible` to 1 only when the full event window lies inside 2026-01-09 through 2026-07-05.
7. Sort by event time, token, and event type and write `data/processed/event_table.csv`.

Invalid rows stop the build with a readable message. This prevents silently dropping questionable research data.

## Scope limits

This table records dated market events; it is not a smart-contract log table. The first version does not infer whether an event is bullish or bearish, scrape arbitrary news, assign an importance score, or manufacture missing size values. On-chain transfer confirmation can be added later as a separate field.

## Verification

Unit tests cover valid rows, window eligibility, invalid inputs, and duplicate removal. The final verification runs the complete test suite and rebuilds the event table from the committed candidate file.
