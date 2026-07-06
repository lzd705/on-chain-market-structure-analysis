"""Check A-side data files before running research analysis."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

import run_research


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def resolve_path(path_text: str) -> Path:
    """Resolve a CLI path relative to the project root."""
    path = Path(path_text)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def load_input_panel(input_dir: Path) -> pd.DataFrame:
    """Load and normalize the available input panel."""
    run_research.configure_paths(input_dir, PROJECT_ROOT / "data" / "research", PROJECT_ROOT / "figures")
    run_research.load_analysis_dependencies()
    panel = run_research.load_panel()
    return run_research.normalize_columns(panel)


def write_markdown(report: pd.DataFrame, output_path: Path) -> None:
    """Write a concise Markdown checklist."""
    lines = [
        "# Data Input Check",
        "",
        f"- Tokens checked: {report['token_symbol'].nunique() if not report.empty else 0}",
        f"- Tokens ok: {(report['status'] == 'ok').sum() if not report.empty else 0}",
        f"- Tokens too short: {(report['status'] == 'too_short').sum() if not report.empty else 0}",
        f"- Missing dates total: {int(report['missing_dates'].sum()) if not report.empty else 0}",
        f"- Duplicate token-date rows total: {int(report['duplicate_rows'].sum()) if not report.empty else 0}",
        "",
        "Review the CSV output for token-level details before treating the data as final.",
        "",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", default="data/processed")
    parser.add_argument("--output-dir", default="data/research")
    parser.add_argument("--min-token-days", type=int, default=30)
    return parser.parse_args()


def main() -> None:
    """CLI entrypoint."""
    args = parse_args()
    input_dir = resolve_path(args.input_dir)
    output_dir = resolve_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    panel = load_input_panel(input_dir)
    report = run_research.build_data_quality_report(panel, args.min_token_days)
    csv_path = output_dir / "data_input_check.csv"
    md_path = output_dir / "data_input_check.md"
    report.to_csv(csv_path, index=False)
    write_markdown(report, md_path)
    print("Wrote", csv_path)
    print("Wrote", md_path)


if __name__ == "__main__":
    main()

