# Research Workflow

This folder contains the B-side research layer. It assumes the A-side data
pipeline will eventually write:

```text
data/processed/merged_volume_panel.csv
```

If the merged panel is not present, `run_research.py` can build a temporary
panel from:

```text
data/processed/cex_volume_daily.csv
data/processed/dex_volume_daily.csv
```

## Outputs

```text
data/research/factor_panel.csv
data/research/coverage_summary.csv
data/research/cex_dex_correlation.csv
data/research/lead_lag_correlation.csv
data/research/factor_forward_returns.csv
data/research/candidate_factor_forward_returns.csv
data/research/factor_robustness_checks.csv
data/research/confirmation_forward_returns.csv

figures/time_series/*.png
figures/lead_lag_heatmap.png
figures/dex_share_timeseries.png
figures/factor_forward_return_bins.png
figures/confirmation_forward_return_bars.png
```

## Run

```bash
python research/run_research.py
```

Use this command before A-side data is available:

```bash
python research/run_research.py --allow-missing
```

## Mock Test

Before A-side data is available, generate deterministic mock inputs and run the
research workflow end to end:

```bash
python research/make_mock_data.py --output-dir data/mock/processed
python research/run_research.py \
  --input-dir data/mock/processed \
  --research-dir data/mock/research \
  --figures-dir figures/mock
python research/summarize_results.py \
  --research-dir data/mock/research \
  --figures-dir figures/mock \
  --output reports/mock_research_findings_summary.md
```

Or run the same workflow with:

```bash
./scripts/run_mock_research.sh
```

The mock script writes test-only files to `data/mock/processed/`. Keep real
A-side outputs in `data/processed/` before drawing research conclusions.

## Real Data Check

Before using A-side data in the report:

```bash
python research/check_data_inputs.py --input-dir data/processed
python research/run_research.py
python research/summarize_results.py
```
