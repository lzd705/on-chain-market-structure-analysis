# Reports

This folder holds the B-side written output:

```text
research_report_draft.md
ppt_outline.md
mock_research_findings_summary.md
a_review_findings_summary.md
```

After the research script runs, fill the placeholders with tables from
`data/research/` and figures from `figures/`.

## Current Output Convention

```text
data/mock/                Mock inputs and mock research outputs for pipeline testing.
figures/mock/             Mock figures for checking plotting behavior.
reports/mock_*.md         Mock summaries. Do not use these as market findings.

data/a_review/            Latest reviewed A-side data analysis output.
figures/a_review/         Latest reviewed A-side figures.
reports/a_review_*.md     Latest reviewed A-side written summary.

data/processed/           Reserved for real A-side pipeline outputs on this branch.
data/research/            Reserved for default B-side research outputs on this branch.
figures/time_series/      Reserved for default B-side time-series figures.
```

Only one reviewed A-side output folder should be kept at a time. If a new check
is run, replace `a_review` rather than creating `a_review_latest`.
