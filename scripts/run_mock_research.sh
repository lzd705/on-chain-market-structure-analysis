#!/usr/bin/env bash
set -euo pipefail

python3 research/make_mock_data.py --output-dir data/mock/processed
python3 research/run_research.py \
  --input-dir data/mock/processed \
  --research-dir data/mock/research \
  --figures-dir figures/mock
python3 research/summarize_results.py \
  --research-dir data/mock/research \
  --figures-dir figures/mock \
  --output reports/mock_research_findings_summary.md

