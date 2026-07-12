"""Build the curated, read-only dataset used by the public dashboard."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = PROJECT_ROOT / "data/a_review/research"
DEFAULT_OUTPUT = PROJECT_ROOT / "data/public/research"

PANEL_COLUMNS = [
    "date",
    "token_symbol",
    "price_usd",
    "cex_volume_usd",
    "dex_volume_usd",
    "total_volume_usd",
    "dex_share",
    "cex_to_dex_ratio",
    "exchange_count",
    "pool_count",
    "return_1d",
    "future_return_1d",
    "future_return_3d",
    "future_return_7d",
    "future_return_14d",
    "active_pool_count",
    "top_pool_volume_share",
    "dex_pool_herfindahl",
    "dex_pool_tvl_usd",
    "top_pool_tvl_share",
    "dex_volume_to_tvl",
    "dex_pool_diversification",
    "token_group",
    "mom_7d",
    "mom_14d",
    "mom_30d",
    "mom_7d_skip_1d",
    "reversal_1d",
    "realized_vol_14d",
    "momentum_vol_adj_7d",
    "cex_vol_z",
    "dex_vol_z",
    "total_vol_z",
    "cex_dex_ratio_z",
    "dex_share_z",
    "dex_volume_to_tvl_z",
    "cex_vol_growth_7d",
    "dex_vol_growth_7d",
    "total_vol_growth_7d",
    "dex_pool_tvl_growth_7d",
    "dex_share_change_7d",
    "dex_pool_concentration_change_7d",
    "volume_divergence",
    "volume_growth_divergence_7d",
    "joint_vol_z_mean",
    "cex_dex_z_product",
    "dex_share_x_dex_vol_z",
    "cex_volume_confirmed_mom_7d",
    "dex_volume_confirmed_mom_7d",
    "joint_volume_confirmed_mom_7d",
    "dex_share_confirmed_mom_7d",
    "pool_diversified_dex_mom_7d",
    "cex_dex_confirmation",
    "volume_state",
]

COMPANION_FILES = [
    "candidate_factor_forward_returns.csv",
    "coverage_summary.csv",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_source_metadata(path: Path) -> tuple[str, str]:
    result = subprocess.run(
        ["git", "log", "-1", "--format=%H%n%cI", "--", str(path.relative_to(PROJECT_ROOT))],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    commit, committed_at = result.stdout.strip().splitlines()
    return commit, committed_at


def write_public_panel(source: Path, destination: Path) -> dict[str, object]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".tmp")
    row_count = 0
    tokens: set[str] = set()
    dates: list[str] = []

    with source.open("r", newline="", encoding="utf-8") as input_handle:
        reader = csv.DictReader(input_handle)
        available = set(reader.fieldnames or [])
        missing = [column for column in PANEL_COLUMNS if column not in available]
        if missing:
            raise ValueError("Source factor panel is missing columns: " + ", ".join(missing))

        with temporary.open("w", newline="", encoding="utf-8") as output_handle:
            writer = csv.DictWriter(output_handle, fieldnames=PANEL_COLUMNS, lineterminator="\n")
            writer.writeheader()
            for row in reader:
                writer.writerow({column: row.get(column, "") for column in PANEL_COLUMNS})
                row_count += 1
                tokens.add(row["token_symbol"])
                dates.append(row["date"])

    temporary.replace(destination)
    return {
        "rows": row_count,
        "tokens": sorted(tokens),
        "start_date": min(dates) if dates else None,
        "end_date": max(dates) if dates else None,
        "columns": len(PANEL_COLUMNS),
        "sha256": sha256(destination),
    }


def copy_companion(source_dir: Path, output_dir: Path, filename: str) -> dict[str, object]:
    source = source_dir / filename
    destination = output_dir / filename
    if not source.exists():
        raise FileNotFoundError(source)
    shutil.copyfile(source, destination)
    with destination.open("r", newline="", encoding="utf-8") as handle:
        row_count = sum(1 for _ in csv.DictReader(handle))
    return {"rows": row_count, "sha256": sha256(destination)}


def build_snapshot(source_dir: Path, output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    files: dict[str, object] = {}
    files["factor_panel.csv"] = write_public_panel(
        source_dir / "factor_panel.csv",
        output_dir / "factor_panel.csv",
    )
    for filename in COMPANION_FILES:
        files[filename] = copy_companion(source_dir, output_dir, filename)

    scope_source = PROJECT_ROOT / "dashboard/data/cex_scope_sensitivity.csv"
    scope_destination = output_dir / "cex_scope_sensitivity.csv"
    shutil.copyfile(scope_source, scope_destination)
    with scope_destination.open("r", newline="", encoding="utf-8") as handle:
        scope_rows = sum(1 for _ in csv.DictReader(handle))
    files[scope_destination.name] = {"rows": scope_rows, "sha256": sha256(scope_destination)}

    source_panel = source_dir / "factor_panel.csv"
    source_commit, source_committed_at = git_source_metadata(source_panel)
    manifest = {
        "snapshot_version": "1.0.0",
        "generated_at": source_committed_at,
        "source_commit": source_commit,
        "source_directory": str(source_dir.relative_to(PROJECT_ROOT)),
        "public_directory": str(output_dir.relative_to(PROJECT_ROOT)),
        "synthetic": False,
        "redistribution_note": "Curated research snapshot; review DATA_USAGE.md before redistribution.",
        "files": files,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_dir = args.source_dir.resolve()
    output_dir = args.output_dir.resolve()
    manifest = build_snapshot(source_dir, output_dir)
    panel = manifest["files"]["factor_panel.csv"]
    print(
        "Wrote public snapshot:",
        panel["rows"],
        "rows,",
        len(panel["tokens"]),
        "tokens,",
        panel["columns"],
        "columns",
    )


if __name__ == "__main__":
    main()
