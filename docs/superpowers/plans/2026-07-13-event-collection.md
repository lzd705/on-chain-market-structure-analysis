# Event Collection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reusable, no-API event collection path that turns auditable candidate records into a standardized event table.

**Architecture:** A committed curated CSV stores source-backed candidate events. A small standard-library Python script validates and transforms those records into the processed event table, so later API imports can reuse the same schema and processing rules.

**Tech Stack:** Python standard library, CSV, `datetime`, `unittest`.

## Global Constraints

- Keep the implementation simple and direct.
- Do not require an API key.
- Do not estimate missing event-size values.
- Preserve source URLs and research limitations.
- Do not stage or modify the unrelated deleted `readme.md`.

---

### Task 1: Event transformation behavior

**Files:**
- Create: `tests/test_build_event_table.py`
- Create: `scripts/build_event_table.py`

**Interfaces:**
- Consumes: candidate dictionaries, configured token symbols, and panel date bounds.
- Produces: `build_event_rows(candidate_rows, allowed_tokens, panel_start, panel_end) -> list[dict]`.

- [ ] **Step 1: Write failing tests**

Add tests showing that the builder normalizes UTC timestamps, computes the `-7/+14` window, marks edge events ineligible, removes exact duplicates, and raises `ValueError` for invalid tokens, event types, timestamps, and missing sources.

- [ ] **Step 2: Verify the tests fail**

Run: `/opt/anaconda3/bin/python -m unittest tests.test_build_event_table -v`

Expected: import failure because `scripts/build_event_table.py` does not exist.

- [ ] **Step 3: Implement the minimal transformation**

Implement these simple functions:

```python
read_allowed_tokens(path)
read_candidate_rows(path)
build_event_rows(candidate_rows, allowed_tokens, panel_start, panel_end)
write_event_rows(rows, path)
main()
```

Use explicit loops and conditions. Use `datetime.fromisoformat` after converting a trailing `Z` to `+00:00`.

- [ ] **Step 4: Verify the focused tests pass**

Run: `/opt/anaconda3/bin/python -m unittest tests.test_build_event_table -v`

Expected: all event-table tests pass.

### Task 2: Curated event dataset

**Files:**
- Create: `data/curated/event_candidates.csv`
- Create: `data/processed/event_table.csv`

**Interfaces:**
- Consumes: primary and secondary web sources for the ten configured tokens.
- Produces: candidate rows matching the schema in the design document.

- [ ] **Step 1: Search the panel period**

For each configured token, search 2026-01-09 through 2026-07-05 for unlocks, airdrops, and CEX listings. Prefer official sources and retain a secondary source when dates or amounts require cross-checking.

- [ ] **Step 2: Record only verifiable candidates**

Write an event only when the token, type, date, name, and source are known. Leave unknown numeric values blank. Put any date ambiguity in `notes` and exclude rows whose event day cannot be established.

- [ ] **Step 3: Build the processed table**

Run: `/opt/anaconda3/bin/python scripts/build_event_table.py`

Expected: `data/processed/event_table.csv` is written and the script prints its row count.

### Task 3: Pipeline and documentation

**Files:**
- Modify: `scripts/run_pipeline.py`
- Modify: `tests/test_run_pipeline.py`
- Modify: `docs/data_pipeline.md`

**Interfaces:**
- Consumes: `scripts.build_event_table.main`.
- Produces: a full pipeline that rebuilds the processed event table without network access.

- [ ] **Step 1: Add a failing pipeline test**

Extend the existing dependency-injection test to assert that `build_event_table` is called once after the other processed tables are built.

- [ ] **Step 2: Verify the test fails**

Run: `/opt/anaconda3/bin/python -m unittest tests.test_run_pipeline -v`

Expected: failure because `run_pipeline` does not yet accept or call `build_event_table`.

- [ ] **Step 3: Add event-table construction to the runner**

Import `scripts.build_event_table`, inject its `main` function in `run_pipeline`, and print `Building event table` before calling it.

- [ ] **Step 4: Document the new inputs and output**

Add the curated candidate table and processed event table to the pipeline flow. Explain that event discovery is curated and transformation is reproducible.

### Task 4: Verification

**Files:**
- Inspect all files changed by Tasks 1-3.

**Interfaces:**
- Consumes: the completed event collection implementation.
- Produces: verification evidence and a clean scoped diff.

- [ ] **Step 1: Run the event build**

Run: `/opt/anaconda3/bin/python scripts/build_event_table.py`

Expected: exits 0 and reports the number of processed events.

- [ ] **Step 2: Run all tests**

Run: `/opt/anaconda3/bin/python -m unittest discover -s tests -v`

Expected: all tests pass.

- [ ] **Step 3: Inspect the generated table and diff**

Run: `git diff --check` and `git status --short`.

Expected: no whitespace errors; the unrelated `D readme.md` remains unstaged and untouched.
