#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INPUT_DIR="${INPUT_DIR:-data/processed}"
RESEARCH_DIR="${RESEARCH_DIR:-data/a_review/research}"
FIGURES_DIR="${FIGURES_DIR:-figures/a_review}"
REPORT_PATH="${REPORT_PATH:-reports/a_review_findings_summary.md}"

cd "$PROJECT_ROOT"

if [[ ! -f "$INPUT_DIR/research_panel.csv" && ! -f "$INPUT_DIR/merged_volume_panel.csv" ]]; then
  if [[ ! -f "$INPUT_DIR/cex_volume_daily.csv" || ! -f "$INPUT_DIR/dex_volume_daily.csv" ]]; then
    echo "No A-side research input found under $INPUT_DIR" >&2
    echo "Expected research_panel.csv, merged_volume_panel.csv, or both daily volume files." >&2
    exit 1
  fi
fi

python3 research/check_data_inputs.py \
  --input-dir "$INPUT_DIR" \
  --output-dir "$RESEARCH_DIR"

python3 research/run_research.py \
  --input-dir "$INPUT_DIR" \
  --research-dir "$RESEARCH_DIR" \
  --figures-dir "$FIGURES_DIR"

python3 research/summarize_results.py \
  --research-dir "$RESEARCH_DIR" \
  --figures-dir "$FIGURES_DIR" \
  --output "$REPORT_PATH"

echo "Research dashboard data refreshed in $RESEARCH_DIR"
