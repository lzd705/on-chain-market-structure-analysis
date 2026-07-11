# Market Structure Dashboard

This local dashboard turns the B-side research outputs into an interactive CEX / DEX comparison tool.

![Dashboard overview](assets/dashboard-overview.png)

## Run

```bash
./scripts/run_dashboard.sh
```

Then open `http://127.0.0.1:8765`.

The server reads the richest available panel in this order:

1. `DASHBOARD_DATA` environment override
2. `data/a_review/research/factor_panel.csv`
3. `data/research/factor_panel.csv`
4. `data/processed/research_panel.csv`
5. `data/processed/merged_volume_panel.csv`

Filters, notes, and checklist status are saved to `dashboard/state/work_status.local.json`. The file is intentionally ignored by Git; `work_status.example.json` is the source-controlled initial state.

## Main views

- Overview: CEX / DEX totals, observed DEX share, metric trends, token comparison, scope sensitivity, and coverage details.
- Factors: candidate-factor buckets versus 1d / 3d / 7d / 14d future returns.
- Research status: persistent checklist, notes, source path, freshness, and data completeness.

`Observed DEX Share` is deliberately named to avoid implying global market coverage. The current DEX input contains selected pools, not every DEX venue.

## Public sample

Run the versioned synthetic sample without relying on redistributed exchange
data:

```bash
./scripts/run_dashboard.sh --data data/mock/research/factor_panel.csv
```

See `dashboard/sample/manifest.json` and `DATA_USAGE.md` for provenance and
licensing boundaries.

## Refresh observed data

After the A-side pipeline has written its processed panel, rebuild the B-side
research outputs with:

```bash
./scripts/refresh_research_dashboard.sh
```

The dashboard reads the refreshed `data/a_review/research/factor_panel.csv` on
the next page reload.
