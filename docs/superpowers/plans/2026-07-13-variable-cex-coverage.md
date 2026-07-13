# Variable CEX Coverage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fetch CEX data for 20 additional tokens and aggregate each token over its own fixed set of stable exchanges.

**Architecture:** Keep the existing exchange adapters. Add one coverage-selection step between raw fetching and aggregation, write a coverage CSV, and require every selected exchange to be present on an included token-date.

**Tech Stack:** Python standard library, CSV, unittest, existing exchange REST APIs.

## Global Constraints

- Code remains simple and direct.
- Try all ten configured exchanges.
- A stable exchange has at least 120 daily observations.
- Require at least three stable exchanges and Binance.
- Do not include the unrelated local deletion of `readme.md`.

---

### Task 1: Test fixed exchange-set selection

**Files:**
- Modify: `tests/test_fetch_cex.py`
- Modify: `scripts/fetch_cex.py`

**Interfaces:**
- Produces: `select_stable_exchanges(rows, minimum_history_days, minimum_exchange_count, price_exchange) -> dict[str, list[str]]`
- Produces: `build_coverage_rows(rows, stable_exchanges_by_token) -> list[dict]`

- [ ] Add a test where three exchanges have enough history and one does not.
- [ ] Run `python -m unittest tests.test_fetch_cex -v` and confirm the missing function fails.
- [ ] Implement observation-day counting and stable exchange selection.
- [ ] Run the same test and confirm it passes.

### Task 2: Test complete-date aggregation

**Files:**
- Modify: `tests/test_fetch_cex.py`
- Modify: `scripts/fetch_cex.py`

**Interfaces:**
- Consumes: `stable_exchanges_by_token` from Task 1.
- Produces: `aggregate_cex_rows(rows, stable_exchanges_by_token=...)`.

- [ ] Add a test with one complete date and one date missing a selected exchange.
- [ ] Run the test and confirm the incomplete date currently remains.
- [ ] Filter aggregation to the fixed exchange set and omit incomplete dates.
- [ ] Run all CEX tests and confirm they pass.

### Task 3: Add tokens and write outputs

**Files:**
- Modify: `config/tokens.csv`
- Modify: `scripts/fetch_cex.py`
- Modify: `docs/data_pipeline.md`
- Create: `data/processed/cex_exchange_coverage.csv`
- Modify: `data/processed/cex_exchange_volume_daily.csv`
- Modify: `data/processed/cex_volume_daily.csv`

**Interfaces:**
- Consumes: the existing ten exchange adapters and 30-token config.
- Produces: raw CEX rows, coverage rows, and stable-set daily aggregates.

- [ ] Add the 20 approved tokens to `config/tokens.csv`.
- [ ] Update `main()` to select stable exchanges and write the coverage CSV.
- [ ] Document the variable-coverage rule.
- [ ] Run `python scripts/fetch_cex.py` to refresh all 30 tokens.
- [ ] Validate token counts, stable exchange counts, date coverage, and CSV schema.
- [ ] Run the full unit test suite and `git diff --check`.
