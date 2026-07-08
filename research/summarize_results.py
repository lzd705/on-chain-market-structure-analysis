"""Create a report-ready Markdown summary from research CSV outputs."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def resolve_path(path_text: str) -> Path:
    """Resolve a CLI path relative to the project root."""
    path = Path(path_text)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def read_csv_if_exists(path: Path) -> pd.DataFrame:
    """Read a CSV if present, otherwise return an empty dataframe."""
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def pct(value) -> str:
    """Format a decimal return or rate."""
    if pd.isna(value):
        return "n/a"
    return f"{value:.2%}"


def number(value) -> str:
    """Format a numeric value."""
    if pd.isna(value):
        return "n/a"
    return f"{value:,.2f}"


def build_summary(research_dir: Path, figures_dir: Path) -> str:
    """Build Markdown summary text."""
    coverage = read_csv_if_exists(research_dir / "coverage_summary.csv")
    correlation = read_csv_if_exists(research_dir / "cex_dex_correlation.csv")
    lead_lag = read_csv_if_exists(research_dir / "lead_lag_correlation.csv")
    factor_returns = read_csv_if_exists(research_dir / "factor_forward_returns.csv")
    candidate_factor_returns = read_csv_if_exists(research_dir / "candidate_factor_forward_returns.csv")
    robustness = read_csv_if_exists(research_dir / "factor_robustness_checks.csv")
    confirmation = read_csv_if_exists(research_dir / "confirmation_forward_returns.csv")
    quality = read_csv_if_exists(research_dir / "data_quality_report.csv")
    dex_structure = read_csv_if_exists(research_dir / "dex_structure_daily.csv")

    lines = [
        "# Research Findings Summary",
        "",
        "This summary is generated from the selected research CSV outputs. If the inputs are mock data, treat the numbers as pipeline validation only.",
        "",
    ]

    if not coverage.empty:
        token_count = coverage["token_symbol"].nunique()
        start_date = coverage["start_date"].min()
        end_date = coverage["end_date"].max()
        total_rows = int(coverage["row_count"].sum())
        lines.extend(
            [
                "## Data Coverage",
                "",
                f"- Token count: {token_count}",
                f"- Date range: {start_date} to {end_date}",
                f"- Token-day rows: {total_rows:,}",
                f"- Median DEX share across token medians: {pct(coverage['dex_share_median'].median())}",
                "",
            ]
        )

    if not quality.empty:
        bad_rows = quality[quality["status"] != "ok"]
        lines.extend(
            [
                "## Data Checks",
                "",
                f"- Tokens passing minimum history check: {(quality['status'] == 'ok').sum()}",
                f"- Tokens flagged: {len(bad_rows)}",
                f"- Total missing dates across tokens: {int(quality['missing_dates'].sum())}",
                f"- Total duplicate token-date rows: {int(quality['duplicate_rows'].sum())}",
                "",
            ]
        )

    if not dex_structure.empty:
        has_signed_flow = "dex_net_buy_ratio" in dex_structure.columns and dex_structure["dex_net_buy_ratio"].notna().any()
        lines.extend(
            [
                "## DEX Direction And Pool Structure",
                "",
                "- DEX buy/sell/net-buy metrics are empty because current inputs do not include swap-level trade direction.",
                f"- Median net buy ratio: {pct(dex_structure['dex_net_buy_ratio'].median()) if has_signed_flow else 'n/a'}",
                f"- Median top-pool volume share: {pct(dex_structure['top_pool_volume_share'].median())}",
                f"- Median pool Herfindahl: {number(dex_structure['dex_pool_herfindahl'].median())}",
                f"- Median active pool count: {number(dex_structure['active_pool_count'].median())}",
                f"- Median DEX volume / pool TVL: {pct(dex_structure['dex_volume_to_tvl'].median())}",
                "",
            ]
        )

    if not correlation.empty:
        top_corr = correlation.sort_values("z_score_corr", ascending=False).head(3)
        lines.extend(["## CEX vs DEX Same-day Correlation", ""])
        for _, row in top_corr.iterrows():
            lines.append(
                f"- {row['token_symbol']}: z-score corr {number(row['z_score_corr'])}, log-volume corr {number(row['log_volume_corr'])}"
            )
        lines.append("")

    if not lead_lag.empty:
        best = lead_lag.sort_values("corr_cex_t_dex_t_plus_lag", ascending=False).head(5)
        lines.extend(["## Lead-lag Highlights", ""])
        for _, row in best.iterrows():
            lines.append(
                f"- {row['token_symbol']} lag {int(row['lag'])}: corr {number(row['corr_cex_t_dex_t_plus_lag'])}, n={int(row['n_obs'])}"
            )
        lines.append("")

    if not factor_returns.empty:
        highest_bucket = factor_returns.sort_values("dex_vol_z_bucket").tail(1).iloc[0]
        lowest_bucket = factor_returns.sort_values("dex_vol_z_bucket").head(1).iloc[0]
        lines.extend(
            [
                "## DEX_VOL_Z Buckets",
                "",
                f"- Lowest bucket 7d mean return: {pct(lowest_bucket['future_return_7d_mean'])}",
                f"- Highest bucket 7d mean return: {pct(highest_bucket['future_return_7d_mean'])}",
                "",
            ]
        )

    if not candidate_factor_returns.empty:
        lines.extend(["## Candidate Factor Buckets", ""])
        for factor_name, factor_panel in candidate_factor_returns.groupby("factor_name"):
            sorted_factor = factor_panel.sort_values("factor_bucket")
            low_bucket = sorted_factor.head(1).iloc[0]
            high_bucket = sorted_factor.tail(1).iloc[0]
            spread = high_bucket["future_return_7d_mean"] - low_bucket["future_return_7d_mean"]
            lines.append(
                f"- {factor_name}: high-minus-low 7d mean spread {pct(spread)} "
                f"(low {pct(low_bucket['future_return_7d_mean'])}, high {pct(high_bucket['future_return_7d_mean'])})"
            )
        lines.append("")

    if not robustness.empty:
        lines.extend(["## Robustness Checks", ""])
        overall = robustness[robustness["check_type"] == "overall"]
        exclude_pepe_arb = robustness[robustness["subset_name"] == "exclude_pepe_arb"]

        merged = overall.merge(
            exclude_pepe_arb,
            on="factor_name",
            suffixes=("_overall", "_exclude_pepe_arb"),
        )
        merged["spread_change"] = (
            merged["high_minus_low_return_mean_exclude_pepe_arb"]
            - merged["high_minus_low_return_mean_overall"]
        )
        merged = merged.sort_values("high_minus_low_return_mean_overall", ascending=False)

        for _, row in merged.head(6).iterrows():
            lines.append(
                f"- {row['factor_name']}: overall spread {pct(row['high_minus_low_return_mean_overall'])}, "
                f"excluding PEPE+ARB {pct(row['high_minus_low_return_mean_exclude_pepe_arb'])}, "
                f"change {pct(row['spread_change'])}"
            )

        group_rows = robustness[robustness["check_type"] == "token_group"].copy()
        if not group_rows.empty:
            strongest = group_rows.sort_values("high_minus_low_return_mean", ascending=False).head(5)
            lines.append("")
            lines.append("Strongest token-group spreads:")
            for _, row in strongest.iterrows():
                lines.append(
                    f"- {row['subset_name']} / {row['factor_name']}: {pct(row['high_minus_low_return_mean'])}, n={int(row['row_count'])}"
                )

        lines.append("")

    if not confirmation.empty:
        ordered = confirmation.sort_values("future_return_7d_mean", ascending=False)
        lines.extend(["## Volume State Comparison", ""])
        for _, row in ordered.iterrows():
            lines.append(
                f"- {row['volume_state']}: 7d mean {pct(row['future_return_7d_mean'])}, 7d win rate {pct(row['future_return_7d_win_rate'])}, n={int(row['row_count'])}"
            )
        lines.append("")

    lines.extend(
        [
            "## Figure Paths",
            "",
            f"- Lead-lag heatmap: `{figures_dir / 'lead_lag_heatmap.png'}`",
            f"- DEX share: `{figures_dir / 'dex_share_timeseries.png'}`",
            f"- Factor buckets: `{figures_dir / 'factor_forward_return_bins.png'}`",
            f"- Confirmation states: `{figures_dir / 'confirmation_forward_return_bars.png'}`",
            "",
        ]
    )

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research-dir", default="data/research")
    parser.add_argument("--figures-dir", default="figures")
    parser.add_argument("--output", default="reports/research_findings_summary.md")
    return parser.parse_args()


def main() -> None:
    """CLI entrypoint."""
    args = parse_args()
    research_dir = resolve_path(args.research_dir)
    figures_dir = resolve_path(args.figures_dir)
    output = resolve_path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_summary(research_dir, figures_dir), encoding="utf-8")
    print("Wrote", output)


if __name__ == "__main__":
    main()
