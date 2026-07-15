# Dynamic Event Query Design

## Goal

Separate event facts from event-study windows so that the same event table can
support any future token set, market-data date range, and user-selected event
window.

## Canonical event table

`data/processed/event_table.csv` is the canonical fact table. It contains every
validated event in `data/curated/event_candidates.csv` for a configured token.
It does not decide whether an event is eligible for one particular study.

The output keeps these fields:

- `token_id`
- `event_type`
- `event_time`
- `event_name`
- `event_size_token`
- `event_size_usd`
- `event_size_supply_pct`
- `source`
- `secondary_source`
- `confidence`
- `notes`

The output removes these window-specific fields:

- `event_window_start`
- `event_window_end`
- `is_analysis_eligible`

Unknown event sizes remain blank. They are never replaced with zero.

## Event builder behavior

`scripts/build_event_table.py` continues to validate token IDs, event types,
timestamps, numeric fields, URLs, confidence values, duplicates, and sort order.
It no longer has hard-coded market-panel start or end dates and does not reject
an event because market data is unavailable around that date.

This allows the table to grow beyond the current six-month research panel and
remain usable when the token configuration changes.

## Website query behavior

The website treats event lookup and event-study analysis as separate actions.

1. Event lookup filters the full fact table by query start date, query end date,
   token, and event type.
2. Selecting an event allows the user to choose `pre_days` and `post_days`.
3. Window completeness is calculated at query time from the actual dates
   available for that token in the research panel.
4. An event remains visible when its selected analysis window is incomplete.
   The interface reports which dates are missing instead of hiding the event.

The window calculation belongs in the research or website layer and is not
written back into the canonical event table.

## Generic validation

Tests must not assume 30 tokens, 174 dates, or a fixed `[-7,+14]` window.

- The allowed token set is read from `config/tokens.csv`.
- Every valid candidate is retained regardless of market-panel boundaries.
- Duplicate fact rows are removed using token, event type, timestamp, and name.
- The canonical output contains no permanent window or eligibility fields.
- A downstream window test supplies its own `pre_days` and `post_days` and
  checks the actual token-date keys in the research panel.

## Migration and compatibility

The current 67 events remain in the canonical event table. Removing the three
window-specific columns is an intentional schema change. Downstream research
and dashboard code must calculate window start, window end, and completeness
dynamically rather than reading the removed columns.

## Out of scope

This change does not add new airdrop or listing records, infer missing event
sizes, alter the CEX comparison basket, or implement the website event view.
Those are separate data and presentation tasks.
