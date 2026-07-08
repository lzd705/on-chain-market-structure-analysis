"""Run first-pass CEX / DEX volume factor research.

The script is intentionally data-source agnostic. It prefers the final A-side
panel, but can also merge the intermediate CEX and DEX daily CSV files.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = PROJECT_ROOT / "data" / "processed"
RESEARCH_DIR = PROJECT_ROOT / "data" / "research"
FIGURES_DIR = PROJECT_ROOT / "figures"
TIME_SERIES_DIR = FIGURES_DIR / "time_series"

MERGED_PANEL_PATH = INPUT_DIR / "merged_volume_panel.csv"
RESEARCH_PANEL_INPUT_PATH = INPUT_DIR / "research_panel.csv"
CEX_DAILY_PATH = INPUT_DIR / "cex_volume_daily.csv"
DEX_DAILY_PATH = INPUT_DIR / "dex_volume_daily.csv"
DEX_POOL_DAILY_PATH = INPUT_DIR / "dex_pool_volume_daily.csv"

FACTOR_PANEL_PATH = RESEARCH_DIR / "factor_panel.csv"
COVERAGE_SUMMARY_PATH = RESEARCH_DIR / "coverage_summary.csv"
CEX_DEX_CORRELATION_PATH = RESEARCH_DIR / "cex_dex_correlation.csv"
LEAD_LAG_CORRELATION_PATH = RESEARCH_DIR / "lead_lag_correlation.csv"
FACTOR_FORWARD_RETURNS_PATH = RESEARCH_DIR / "factor_forward_returns.csv"
CONFIRMATION_FORWARD_RETURNS_PATH = RESEARCH_DIR / "confirmation_forward_returns.csv"
DATA_QUALITY_REPORT_PATH = RESEARCH_DIR / "data_quality_report.csv"
CANDIDATE_FACTOR_RETURNS_PATH = RESEARCH_DIR / "candidate_factor_forward_returns.csv"
FACTOR_ROBUSTNESS_PATH = RESEARCH_DIR / "factor_robustness_checks.csv"
DEX_STRUCTURE_DAILY_PATH = RESEARCH_DIR / "dex_structure_daily.csv"

np = None
pd = None
plt = None


PRICE_ALIASES = ["price_usd", "close", "close_cex", "close_x", "cex_close", "price", "close_price"]
CEX_VOLUME_ALIASES = ["cex_volume_usd", "quote_volume_usd", "volume_usd_cex", "cex_volume"]
DEX_VOLUME_ALIASES = ["dex_volume_usd", "volume_usd_dex", "dex_volume", "volume_usd"]
DATE_ALIASES = ["date", "day", "timestamp"]
TOKEN_ALIASES = ["token_symbol", "symbol", "token"]
TOKEN_GROUPS = {
    "AAVE": "defi",
    "ARB": "layer2",
    "CRV": "defi",
    "ENA": "defi",
    "LDO": "defi",
    "LINK": "infra",
    "OP": "layer2",
    "PENDLE": "defi",
    "PEPE": "meme",
    "UNI": "defi",
}
CANDIDATE_FACTOR_NAMES = [
    "mom_7d",
    "mom_14d",
    "mom_30d",
    "mom_7d_skip_1d",
    "reversal_1d",
    "realized_vol_14d",
    "momentum_vol_adj_7d",
    "total_vol_z",
    "cex_vol_growth_7d",
    "dex_vol_growth_7d",
    "total_vol_growth_7d",
    "dex_share_z",
    "dex_share_change_7d",
    "cex_dex_ratio_z",
    "volume_growth_divergence_7d",
    "joint_vol_z_mean",
    "cex_dex_z_product",
    "dex_share_x_dex_vol_z",
    "cex_volume_confirmed_mom_7d",
    "dex_volume_confirmed_mom_7d",
    "joint_volume_confirmed_mom_7d",
    "dex_share_confirmed_mom_7d",
    "dex_net_buy_ratio_proxy",
    "dex_buy_pressure_proxy_z",
    "dex_net_buy_confirmed_mom_7d",
    "top_pool_volume_share",
    "dex_pool_herfindahl",
    "dex_pool_diversification",
    "dex_pool_concentration_change_7d",
    "dex_volume_to_tvl",
    "dex_volume_to_tvl_z",
    "dex_pool_tvl_growth_7d",
    "pool_diversified_dex_mom_7d",
]
ROBUSTNESS_FACTOR_NAMES = [
    "cex_volume_confirmed_mom_7d",
    "dex_volume_confirmed_mom_7d",
    "joint_volume_confirmed_mom_7d",
    "dex_share_x_dex_vol_z",
    "volume_growth_divergence_7d",
    "mom_14d",
    "mom_30d",
    "total_vol_z",
    "dex_net_buy_confirmed_mom_7d",
    "pool_diversified_dex_mom_7d",
    "dex_volume_to_tvl_z",
]


def resolve_path(path_text: str) -> Path:
    """Resolve a CLI path relative to the project root."""
    path = Path(path_text)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def configure_paths(input_dir: Path, research_dir: Path, figures_dir: Path) -> None:
    """Configure input and output paths for one research run."""
    global INPUT_DIR, RESEARCH_DIR, FIGURES_DIR, TIME_SERIES_DIR
    global MERGED_PANEL_PATH, RESEARCH_PANEL_INPUT_PATH, CEX_DAILY_PATH, DEX_DAILY_PATH, DEX_POOL_DAILY_PATH
    global FACTOR_PANEL_PATH, COVERAGE_SUMMARY_PATH, CEX_DEX_CORRELATION_PATH
    global LEAD_LAG_CORRELATION_PATH, FACTOR_FORWARD_RETURNS_PATH
    global CONFIRMATION_FORWARD_RETURNS_PATH, DATA_QUALITY_REPORT_PATH
    global CANDIDATE_FACTOR_RETURNS_PATH, FACTOR_ROBUSTNESS_PATH, DEX_STRUCTURE_DAILY_PATH

    INPUT_DIR = input_dir
    RESEARCH_DIR = research_dir
    FIGURES_DIR = figures_dir
    TIME_SERIES_DIR = FIGURES_DIR / "time_series"

    MERGED_PANEL_PATH = INPUT_DIR / "merged_volume_panel.csv"
    RESEARCH_PANEL_INPUT_PATH = INPUT_DIR / "research_panel.csv"
    CEX_DAILY_PATH = INPUT_DIR / "cex_volume_daily.csv"
    DEX_DAILY_PATH = INPUT_DIR / "dex_volume_daily.csv"
    DEX_POOL_DAILY_PATH = INPUT_DIR / "dex_pool_volume_daily.csv"

    FACTOR_PANEL_PATH = RESEARCH_DIR / "factor_panel.csv"
    COVERAGE_SUMMARY_PATH = RESEARCH_DIR / "coverage_summary.csv"
    CEX_DEX_CORRELATION_PATH = RESEARCH_DIR / "cex_dex_correlation.csv"
    LEAD_LAG_CORRELATION_PATH = RESEARCH_DIR / "lead_lag_correlation.csv"
    FACTOR_FORWARD_RETURNS_PATH = RESEARCH_DIR / "factor_forward_returns.csv"
    CONFIRMATION_FORWARD_RETURNS_PATH = RESEARCH_DIR / "confirmation_forward_returns.csv"
    DATA_QUALITY_REPORT_PATH = RESEARCH_DIR / "data_quality_report.csv"
    CANDIDATE_FACTOR_RETURNS_PATH = RESEARCH_DIR / "candidate_factor_forward_returns.csv"
    FACTOR_ROBUSTNESS_PATH = RESEARCH_DIR / "factor_robustness_checks.csv"
    DEX_STRUCTURE_DAILY_PATH = RESEARCH_DIR / "dex_structure_daily.csv"


def ensure_output_dirs() -> None:
    """Create output directories used by the research layer."""
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    TIME_SERIES_DIR.mkdir(parents=True, exist_ok=True)


def has_research_input() -> bool:
    """Return whether any usable A-side input data is present."""
    if RESEARCH_PANEL_INPUT_PATH.exists():
        return True

    if MERGED_PANEL_PATH.exists():
        return True

    return CEX_DAILY_PATH.exists() and DEX_DAILY_PATH.exists()


def load_analysis_dependencies() -> None:
    """Import optional analysis dependencies only when data is available."""
    global np, pd, plt

    if pd is not None:
        return

    os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".matplotlib-cache"))

    try:
        import matplotlib.pyplot as imported_plt
        import numpy as imported_np
        import pandas as imported_pd
    except ModuleNotFoundError as error:
        raise ModuleNotFoundError(
            "Missing research dependency. Install with: "
            "python3 -m pip install -r requirements-research.txt"
        ) from error

    np = imported_np
    pd = imported_pd
    plt = imported_plt


def pick_column(panel: pd.DataFrame, aliases: list[str], target: str) -> pd.DataFrame:
    """Rename the first available alias to a canonical column name."""
    if target in panel.columns:
        return panel

    for alias in aliases:
        if alias in panel.columns:
            return panel.rename(columns={alias: target})

    raise ValueError("Panel must include one of these columns for %s: %s" % (target, ", ".join(aliases)))


def standardize_core_columns(panel: pd.DataFrame) -> pd.DataFrame:
    """Normalize flexible input column names to the research contract."""
    panel = panel.copy()
    panel = pick_column(panel, DATE_ALIASES, "date")
    panel = pick_column(panel, TOKEN_ALIASES, "token_symbol")
    panel = pick_column(panel, PRICE_ALIASES, "price_usd")
    panel = pick_column(panel, CEX_VOLUME_ALIASES, "cex_volume_usd")
    panel = pick_column(panel, DEX_VOLUME_ALIASES, "dex_volume_usd")
    return panel


def load_panel() -> pd.DataFrame:
    """Load the final panel or build one from intermediate CEX and DEX files."""
    if RESEARCH_PANEL_INPUT_PATH.exists():
        panel = pd.read_csv(RESEARCH_PANEL_INPUT_PATH)
        return merge_dex_pool_features(panel)

    if MERGED_PANEL_PATH.exists():
        panel = pd.read_csv(MERGED_PANEL_PATH)
        return merge_dex_pool_features(panel)

    if not CEX_DAILY_PATH.exists() or not DEX_DAILY_PATH.exists():
        missing_paths = [
            str(path.relative_to(PROJECT_ROOT))
            for path in [RESEARCH_PANEL_INPUT_PATH, MERGED_PANEL_PATH, CEX_DAILY_PATH, DEX_DAILY_PATH]
            if not path.exists()
        ]
        raise FileNotFoundError(
            "No research input data found. Missing: " + ", ".join(missing_paths)
        )

    cex = pd.read_csv(CEX_DAILY_PATH)
    dex = pd.read_csv(DEX_DAILY_PATH)

    cex = pick_column(cex, DATE_ALIASES, "date")
    cex = pick_column(cex, TOKEN_ALIASES, "token_symbol")
    cex = pick_column(cex, PRICE_ALIASES, "price_usd")
    cex = pick_column(cex, CEX_VOLUME_ALIASES, "cex_volume_usd")

    dex = pick_column(dex, DATE_ALIASES, "date")
    dex = pick_column(dex, TOKEN_ALIASES, "token_symbol")
    dex = pick_column(dex, DEX_VOLUME_ALIASES, "dex_volume_usd")

    dex_agg_kwargs = {"dex_volume_usd": ("dex_volume_usd", "sum")}
    if "pool_address" in dex.columns:
        dex_agg_kwargs["dex_pool_count"] = ("pool_address", "nunique")
    if "dex" in dex.columns:
        dex_agg_kwargs["dex_list"] = ("dex", lambda values: ";".join(sorted(set(values.dropna()))))

    dex_agg = (
        dex.groupby(["date", "token_symbol"], as_index=False)
        .agg(**dex_agg_kwargs)
    )

    cex = (
        cex.groupby(["date", "token_symbol"], as_index=False)
        .agg(
            price_usd=("price_usd", "last"),
            cex_volume_usd=("cex_volume_usd", "sum"),
        )
    )

    panel = cex.merge(dex_agg, on=["date", "token_symbol"], how="inner")
    return merge_dex_pool_features(panel)


def calculate_dex_pool_features(pool_daily: pd.DataFrame) -> pd.DataFrame:
    """Build daily DEX direction proxies and pool concentration metrics.

    The input is daily pool OHLCV, not swap-level data. Directional buy/sell
    columns are therefore OHLCV-based pressure proxies, not true trade signs.
    """
    required = {"date", "token_symbol", "pool_address", "open", "high", "low", "close", "dex_volume_usd"}
    missing = sorted(required - set(pool_daily.columns))
    if missing:
        raise ValueError("DEX pool daily file is missing required columns: " + ", ".join(missing))

    pool_daily = pool_daily.copy()
    pool_daily["date"] = pd.to_datetime(pool_daily["date"])
    pool_daily["token_symbol"] = pool_daily["token_symbol"].astype(str).str.upper()

    numeric_columns = ["open", "high", "low", "close", "dex_volume_usd"]
    if "pool_tvl_usd" in pool_daily.columns:
        numeric_columns.append("pool_tvl_usd")

    for column in numeric_columns:
        pool_daily[column] = pd.to_numeric(pool_daily[column], errors="coerce")

    if "pool_tvl_usd" not in pool_daily.columns:
        pool_daily["pool_tvl_usd"] = pd.NA

    pool_daily["dex_volume_usd"] = pool_daily["dex_volume_usd"].fillna(0.0).clip(lower=0)
    price_range = pool_daily["high"] - pool_daily["low"]
    close_location = (pool_daily["close"] - pool_daily["low"]) / price_range.replace(0, pd.NA)
    pool_daily["buy_pressure_proxy"] = close_location.fillna(0.5).clip(lower=0.0, upper=1.0)
    pool_daily["dex_buy_volume_proxy_usd"] = pool_daily["dex_volume_usd"] * pool_daily["buy_pressure_proxy"]
    pool_daily["dex_sell_volume_proxy_usd"] = pool_daily["dex_volume_usd"] * (1.0 - pool_daily["buy_pressure_proxy"])

    group_keys = ["date", "token_symbol"]
    pool_daily["pool_volume_total"] = pool_daily.groupby(group_keys)["dex_volume_usd"].transform("sum")
    pool_daily["pool_volume_share"] = pool_daily["dex_volume_usd"] / pool_daily["pool_volume_total"].replace(0, pd.NA)
    pool_daily["pool_tvl_total"] = pool_daily.groupby(group_keys)["pool_tvl_usd"].transform("sum")
    pool_daily["pool_tvl_share"] = pool_daily["pool_tvl_usd"] / pool_daily["pool_tvl_total"].replace(0, pd.NA)

    features = (
        pool_daily.groupby(group_keys, as_index=False)
        .agg(
            dex_pool_volume_sum=("dex_volume_usd", "sum"),
            dex_buy_volume_proxy_usd=("dex_buy_volume_proxy_usd", "sum"),
            dex_sell_volume_proxy_usd=("dex_sell_volume_proxy_usd", "sum"),
            active_pool_count=("pool_address", "nunique"),
            top_pool_volume_usd=("dex_volume_usd", "max"),
            top_pool_volume_share=("pool_volume_share", "max"),
            dex_pool_herfindahl=("pool_volume_share", lambda values: (values.dropna() ** 2).sum()),
            dex_pool_tvl_usd=("pool_tvl_usd", "sum"),
            top_pool_tvl_share=("pool_tvl_share", "max"),
        )
    )

    features["dex_net_buy_volume_proxy_usd"] = (
        features["dex_buy_volume_proxy_usd"] - features["dex_sell_volume_proxy_usd"]
    )
    features["dex_net_buy_ratio_proxy"] = (
        features["dex_net_buy_volume_proxy_usd"]
        / features["dex_pool_volume_sum"].replace(0, pd.NA)
    )
    features["dex_volume_to_tvl"] = (
        features["dex_pool_volume_sum"]
        / features["dex_pool_tvl_usd"].replace(0, pd.NA)
    )
    features["dex_pool_diversification"] = 1.0 - features["dex_pool_herfindahl"]
    features["dex_direction_proxy_method"] = "ohlcv_close_location"

    return features


def merge_dex_pool_features(panel: pd.DataFrame) -> pd.DataFrame:
    """Merge optional DEX pool microstructure proxies into the research panel."""
    if not DEX_POOL_DAILY_PATH.exists():
        return panel

    pool_daily = pd.read_csv(DEX_POOL_DAILY_PATH)
    if pool_daily.empty:
        return panel

    features = calculate_dex_pool_features(pool_daily)
    panel = panel.copy()
    panel["date"] = pd.to_datetime(panel["date"])
    panel["token_symbol"] = panel["token_symbol"].astype(str).str.upper()
    return panel.merge(features, on=["date", "token_symbol"], how="left")


def normalize_columns(panel: pd.DataFrame) -> pd.DataFrame:
    """Normalize expected column names and types."""
    panel = standardize_core_columns(panel)
    panel["date"] = pd.to_datetime(panel["date"])
    panel["token_symbol"] = panel["token_symbol"].astype(str).str.upper()

    required = ["price_usd", "cex_volume_usd", "dex_volume_usd"]
    for column in required:
        panel[column] = pd.to_numeric(panel[column], errors="coerce")

    panel = panel.dropna(subset=["date", "token_symbol", "price_usd"])
    panel = panel.sort_values(["token_symbol", "date"])
    return panel


def build_data_quality_report(panel: pd.DataFrame, min_token_days: int) -> pd.DataFrame:
    """Build token-level input checks before factor calculation."""
    duplicate_counts = panel.groupby(["date", "token_symbol"]).size().reset_index(name="duplicate_count")
    duplicate_counts = duplicate_counts[duplicate_counts["duplicate_count"] > 1]
    duplicate_by_token = duplicate_counts.groupby("token_symbol")["duplicate_count"].sum()

    rows = []
    for token_symbol, token_panel in panel.groupby("token_symbol"):
        token_panel = token_panel.sort_values("date")
        date_span = pd.date_range(token_panel["date"].min(), token_panel["date"].max(), freq="D")
        present_dates = set(token_panel["date"].dt.normalize())
        missing_dates = sum(1 for value in date_span if value not in present_dates)
        row_count = len(token_panel)
        rows.append(
            {
                "token_symbol": token_symbol,
                "start_date": token_panel["date"].min(),
                "end_date": token_panel["date"].max(),
                "row_count": row_count,
                "status": "ok" if row_count >= min_token_days else "too_short",
                "missing_dates": missing_dates,
                "duplicate_rows": int(duplicate_by_token.get(token_symbol, 0)),
                "missing_price": int(token_panel["price_usd"].isna().sum()),
                "missing_cex_volume": int(token_panel["cex_volume_usd"].isna().sum()),
                "missing_dex_volume": int(token_panel["dex_volume_usd"].isna().sum()),
                "zero_cex_volume": int((token_panel["cex_volume_usd"].fillna(0) == 0).sum()),
                "zero_dex_volume": int((token_panel["dex_volume_usd"].fillna(0) == 0).sum()),
            }
        )

    return pd.DataFrame(rows)


def write_data_quality_report(panel: pd.DataFrame, min_token_days: int) -> pd.DataFrame:
    """Write input quality report and return the same dataframe."""
    report = build_data_quality_report(panel, min_token_days)
    report.to_csv(DATA_QUALITY_REPORT_PATH, index=False)
    return report


def filter_short_tokens(panel: pd.DataFrame, min_token_days: int) -> pd.DataFrame:
    """Drop token histories that are too short for rolling factors."""
    counts = panel.groupby("token_symbol")["date"].count()
    valid_tokens = counts[counts >= min_token_days].index
    return panel[panel["token_symbol"].isin(valid_tokens)].copy()


def rolling_z_score(series: pd.Series, window: int = 30, min_periods: int = 10) -> pd.Series:
    """Compute a rolling z-score that is stable for short initial histories."""
    rolling_mean = series.rolling(window=window, min_periods=min_periods).mean()
    rolling_std = series.rolling(window=window, min_periods=min_periods).std()
    return (series - rolling_mean) / rolling_std.replace(0, pd.NA)


def rolling_volume_growth(series: pd.Series, window: int = 7) -> pd.Series:
    """Compare recent rolling volume with the previous rolling window."""
    recent = series.rolling(window=window, min_periods=window).sum()
    previous = recent.shift(window)
    return np.log(recent / previous.replace(0, pd.NA))


def assign_token_group(token_symbol: str) -> str:
    """Assign a coarse token group for robustness checks."""
    return TOKEN_GROUPS.get(str(token_symbol).upper(), "other")


def add_factors(panel: pd.DataFrame, drop_last_date: bool = True) -> pd.DataFrame:
    """Add returns, volume factors, and confirmation labels."""
    panel = panel.copy()

    if drop_last_date and not panel.empty:
        panel = panel[panel["date"] < panel["date"].max()].copy()

    panel["token_group"] = panel["token_symbol"].map(assign_token_group)
    panel["cex_volume_usd"] = panel["cex_volume_usd"].fillna(0.0)
    panel["dex_volume_usd"] = panel["dex_volume_usd"].fillna(0.0)
    optional_numeric_columns = [
        "dex_buy_volume_proxy_usd",
        "dex_sell_volume_proxy_usd",
        "dex_net_buy_volume_proxy_usd",
        "dex_net_buy_ratio_proxy",
        "active_pool_count",
        "top_pool_volume_usd",
        "top_pool_volume_share",
        "dex_pool_herfindahl",
        "dex_pool_tvl_usd",
        "top_pool_tvl_share",
        "dex_volume_to_tvl",
        "dex_pool_diversification",
    ]
    for column in optional_numeric_columns:
        if column not in panel.columns:
            panel[column] = pd.NA
        panel[column] = pd.to_numeric(panel[column], errors="coerce")

    panel["total_volume_usd"] = panel["cex_volume_usd"] + panel["dex_volume_usd"]
    panel["dex_share"] = panel["dex_volume_usd"] / panel["total_volume_usd"].replace(0, pd.NA)

    grouped = panel.groupby("token_symbol", group_keys=False)
    panel["return_1d"] = grouped["price_usd"].pct_change()

    for horizon in [1, 3, 7, 14]:
        panel[f"future_return_{horizon}d"] = grouped["price_usd"].shift(-horizon) / panel["price_usd"] - 1

    for lookback in [7, 14, 30]:
        panel[f"mom_{lookback}d"] = np.log(panel["price_usd"] / grouped["price_usd"].shift(lookback))
    panel["mom_7d_skip_1d"] = np.log(grouped["price_usd"].shift(1) / grouped["price_usd"].shift(8))
    panel["reversal_1d"] = -panel["return_1d"]
    panel["realized_vol_14d"] = grouped["return_1d"].transform(
        lambda values: values.rolling(window=14, min_periods=7).std()
    )
    panel["momentum_vol_adj_7d"] = panel["mom_7d"] / panel["realized_vol_14d"].replace(0, pd.NA)

    panel["log_cex_volume"] = np.log1p(panel["cex_volume_usd"].clip(lower=0))
    panel["log_dex_volume"] = np.log1p(panel["dex_volume_usd"].clip(lower=0))
    panel["log_total_volume"] = np.log1p(panel["total_volume_usd"].clip(lower=0))
    panel["log_cex_dex_ratio"] = np.log((panel["cex_volume_usd"] + 1.0) / (panel["dex_volume_usd"] + 1.0))
    panel["log_dex_volume_to_tvl"] = np.log1p(panel["dex_volume_to_tvl"].clip(lower=0))

    panel["cex_vol_z"] = grouped["log_cex_volume"].transform(rolling_z_score)
    panel["dex_vol_z"] = grouped["log_dex_volume"].transform(rolling_z_score)
    panel["total_vol_z"] = grouped["log_total_volume"].transform(rolling_z_score)
    panel["cex_dex_ratio_z"] = grouped["log_cex_dex_ratio"].transform(rolling_z_score)
    panel["dex_share_z"] = grouped["dex_share"].transform(rolling_z_score)
    panel["dex_buy_pressure_proxy_z"] = grouped["dex_net_buy_ratio_proxy"].transform(rolling_z_score)
    panel["dex_volume_to_tvl_z"] = grouped["log_dex_volume_to_tvl"].transform(rolling_z_score)
    panel["cex_vol_growth_7d"] = grouped["cex_volume_usd"].transform(rolling_volume_growth)
    panel["dex_vol_growth_7d"] = grouped["dex_volume_usd"].transform(rolling_volume_growth)
    panel["total_vol_growth_7d"] = grouped["total_volume_usd"].transform(rolling_volume_growth)
    panel["dex_pool_tvl_growth_7d"] = grouped["dex_pool_tvl_usd"].transform(rolling_volume_growth)
    panel["dex_share_change_7d"] = panel["dex_share"] - grouped["dex_share"].shift(7)
    panel["dex_pool_concentration_change_7d"] = (
        panel["top_pool_volume_share"] - grouped["top_pool_volume_share"].shift(7)
    )
    panel["volume_divergence"] = panel["dex_vol_z"] - panel["cex_vol_z"]
    panel["volume_growth_divergence_7d"] = panel["dex_vol_growth_7d"] - panel["cex_vol_growth_7d"]
    panel["joint_vol_z_mean"] = (panel["cex_vol_z"] + panel["dex_vol_z"]) / 2.0
    panel["cex_dex_z_product"] = panel["cex_vol_z"] * panel["dex_vol_z"]
    panel["dex_share_x_dex_vol_z"] = panel["dex_share"] * panel["dex_vol_z"]
    panel["cex_volume_confirmed_mom_7d"] = panel["mom_7d"] * panel["cex_vol_z"]
    panel["dex_volume_confirmed_mom_7d"] = panel["mom_7d"] * panel["dex_vol_z"]
    panel["joint_volume_confirmed_mom_7d"] = panel["mom_7d"] * panel["joint_vol_z_mean"]
    panel["dex_share_confirmed_mom_7d"] = panel["mom_7d"] * panel["dex_share_z"]
    panel["dex_net_buy_confirmed_mom_7d"] = panel["mom_7d"] * panel["dex_buy_pressure_proxy_z"]
    panel["pool_diversified_dex_mom_7d"] = (
        panel["dex_volume_confirmed_mom_7d"] * panel["dex_pool_diversification"]
    )
    panel["cex_dex_confirmation"] = (
        (panel["cex_vol_z"] > 1.0) & (panel["dex_vol_z"] > 1.0)
    ).astype(int)

    panel["volume_state"] = "both_low_or_normal"
    panel.loc[(panel["cex_vol_z"] > 1.0) & (panel["dex_vol_z"] <= 1.0), "volume_state"] = "cex_only"
    panel.loc[(panel["dex_vol_z"] > 1.0) & (panel["cex_vol_z"] <= 1.0), "volume_state"] = "dex_only"
    panel.loc[(panel["cex_vol_z"] > 1.0) & (panel["dex_vol_z"] > 1.0), "volume_state"] = "both_high"

    return panel


def format_percent_axis(ax) -> None:
    """Format the y-axis as percentages."""
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value:.1%}"))


def format_million_axis(ax) -> None:
    """Format the y-axis in USD millions."""
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value / 1_000_000:.1f}M"))


def apply_chart_style(ax) -> None:
    """Apply consistent chart styling for report-ready figures."""
    ax.grid(True, axis="y", color="#e6e8eb", linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def write_coverage_summary(panel: pd.DataFrame) -> None:
    """Write token-level data coverage and volume summary."""
    agg_kwargs = {
        "start_date": ("date", "min"),
        "end_date": ("date", "max"),
        "row_count": ("date", "count"),
        "cex_volume_median": ("cex_volume_usd", "median"),
        "dex_volume_median": ("dex_volume_usd", "median"),
        "dex_share_median": ("dex_share", "median"),
        "missing_price": ("price_usd", lambda values: values.isna().sum()),
    }
    optional_summary_columns = {
        "dex_net_buy_ratio_proxy_median": "dex_net_buy_ratio_proxy",
        "top_pool_volume_share_median": "top_pool_volume_share",
        "dex_pool_herfindahl_median": "dex_pool_herfindahl",
        "dex_volume_to_tvl_median": "dex_volume_to_tvl",
        "active_pool_count_median": "active_pool_count",
    }
    for output_column, source_column in optional_summary_columns.items():
        if source_column in panel.columns:
            agg_kwargs[output_column] = (source_column, "median")

    summary = panel.groupby("token_symbol").agg(**agg_kwargs).reset_index()
    summary.to_csv(COVERAGE_SUMMARY_PATH, index=False)


def write_dex_structure_daily(panel: pd.DataFrame) -> None:
    """Write DEX direction proxy, pool concentration, and liquidity proxy columns."""
    columns = [
        "date",
        "token_symbol",
        "dex_volume_usd",
        "dex_buy_volume_proxy_usd",
        "dex_sell_volume_proxy_usd",
        "dex_net_buy_volume_proxy_usd",
        "dex_net_buy_ratio_proxy",
        "active_pool_count",
        "top_pool_volume_usd",
        "top_pool_volume_share",
        "dex_pool_herfindahl",
        "dex_pool_diversification",
        "dex_pool_tvl_usd",
        "top_pool_tvl_share",
        "dex_volume_to_tvl",
        "dex_direction_proxy_method",
    ]
    available_columns = [column for column in columns if column in panel.columns]
    if not {"date", "token_symbol"}.issubset(available_columns):
        pd.DataFrame().to_csv(DEX_STRUCTURE_DAILY_PATH, index=False)
        return

    panel[available_columns].to_csv(DEX_STRUCTURE_DAILY_PATH, index=False)


def write_cex_dex_correlation(panel: pd.DataFrame) -> None:
    """Write per-token same-day CEX/DEX volume correlations."""
    rows = []
    for token_symbol, token_panel in panel.groupby("token_symbol"):
        rows.append(
            {
                "token_symbol": token_symbol,
                "row_count": len(token_panel),
                "log_volume_corr": token_panel["log_cex_volume"].corr(token_panel["log_dex_volume"]),
                "z_score_corr": token_panel["cex_vol_z"].corr(token_panel["dex_vol_z"]),
            }
        )

    pd.DataFrame(rows).to_csv(CEX_DEX_CORRELATION_PATH, index=False)


def calculate_lead_lag(panel: pd.DataFrame, max_lag: int = 7) -> pd.DataFrame:
    """Calculate corr(CEX_VOL_Z_t, DEX_VOL_Z_{t+lag}) by token."""
    rows = []

    for token_symbol, token_panel in panel.groupby("token_symbol"):
        token_panel = token_panel.sort_values("date")

        for lag in range(-max_lag, max_lag + 1):
            shifted_dex = token_panel["dex_vol_z"].shift(-lag)
            rows.append(
                {
                    "token_symbol": token_symbol,
                    "lag": lag,
                    "corr_cex_t_dex_t_plus_lag": token_panel["cex_vol_z"].corr(shifted_dex),
                    "n_obs": token_panel[["cex_vol_z"]].join(shifted_dex.rename("shifted_dex")).dropna().shape[0],
                }
            )

    result = pd.DataFrame(rows)
    result.to_csv(LEAD_LAG_CORRELATION_PATH, index=False)
    return result


def write_factor_forward_returns(panel: pd.DataFrame) -> None:
    """Write forward returns grouped by DEX volume z-score quantiles."""
    analysis_panel = panel.dropna(subset=["dex_vol_z"]).copy()
    unique_values = analysis_panel["dex_vol_z"].nunique()

    if unique_values < 3:
        pd.DataFrame().to_csv(FACTOR_FORWARD_RETURNS_PATH, index=False)
        return

    quantile_count = min(5, unique_values)
    analysis_panel["dex_vol_z_bucket"] = pd.qcut(
        analysis_panel["dex_vol_z"],
        q=quantile_count,
        labels=False,
        duplicates="drop",
    )

    grouped = analysis_panel.groupby("dex_vol_z_bucket", observed=True)
    summary = grouped.agg(
        row_count=("date", "count"),
        dex_vol_z_mean=("dex_vol_z", "mean"),
        future_return_1d_mean=("future_return_1d", "mean"),
        future_return_3d_mean=("future_return_3d", "mean"),
        future_return_7d_mean=("future_return_7d", "mean"),
        future_return_1d_median=("future_return_1d", "median"),
        future_return_3d_median=("future_return_3d", "median"),
        future_return_7d_median=("future_return_7d", "median"),
    )
    summary.reset_index().to_csv(FACTOR_FORWARD_RETURNS_PATH, index=False)


def write_candidate_factor_forward_returns(panel: pd.DataFrame) -> None:
    """Write forward-return buckets for a small set of candidate factors."""
    rows = []

    for factor_name in CANDIDATE_FACTOR_NAMES:
        if factor_name not in panel.columns:
            continue

        analysis_panel = panel.dropna(
            subset=[
                factor_name,
                "future_return_1d",
                "future_return_3d",
                "future_return_7d",
                "future_return_14d",
            ]
        ).copy()

        unique_values = analysis_panel[factor_name].nunique()
        if unique_values < 3:
            continue

        quantile_count = min(5, unique_values)
        analysis_panel["factor_bucket"] = pd.qcut(
            analysis_panel[factor_name],
            q=quantile_count,
            labels=False,
            duplicates="drop",
        )

        for bucket, bucket_panel in analysis_panel.groupby("factor_bucket", observed=True):
            rows.append(
                {
                    "factor_name": factor_name,
                    "factor_bucket": int(bucket),
                    "row_count": len(bucket_panel),
                    "factor_mean": bucket_panel[factor_name].mean(),
                    "future_return_1d_mean": bucket_panel["future_return_1d"].mean(),
                    "future_return_3d_mean": bucket_panel["future_return_3d"].mean(),
                    "future_return_7d_mean": bucket_panel["future_return_7d"].mean(),
                    "future_return_14d_mean": bucket_panel["future_return_14d"].mean(),
                    "future_return_1d_median": bucket_panel["future_return_1d"].median(),
                    "future_return_3d_median": bucket_panel["future_return_3d"].median(),
                    "future_return_7d_median": bucket_panel["future_return_7d"].median(),
                    "future_return_14d_median": bucket_panel["future_return_14d"].median(),
                    "future_return_1d_win_rate": (bucket_panel["future_return_1d"] > 0).mean(),
                    "future_return_3d_win_rate": (bucket_panel["future_return_3d"] > 0).mean(),
                    "future_return_7d_win_rate": (bucket_panel["future_return_7d"] > 0).mean(),
                    "future_return_14d_win_rate": (bucket_panel["future_return_14d"] > 0).mean(),
                }
            )

    pd.DataFrame(rows).to_csv(CANDIDATE_FACTOR_RETURNS_PATH, index=False)


def calculate_factor_spread(
    panel: pd.DataFrame,
    factor_name: str,
    return_column: str = "future_return_7d",
    max_buckets: int = 5,
):
    """Calculate high-minus-low forward return spread for one factor subset."""
    if factor_name not in panel.columns:
        return None

    analysis_panel = panel.dropna(subset=[factor_name, return_column]).copy()
    unique_values = analysis_panel[factor_name].nunique()

    if len(analysis_panel) < 30 or unique_values < 3:
        return None

    bucket_count = min(max_buckets, unique_values)

    try:
        analysis_panel["factor_bucket"] = pd.qcut(
            analysis_panel[factor_name],
            q=bucket_count,
            labels=False,
            duplicates="drop",
        )
    except ValueError:
        return None

    if analysis_panel["factor_bucket"].nunique() < 2:
        return None

    grouped = analysis_panel.groupby("factor_bucket", observed=True)
    bucket_summary = grouped.agg(
        row_count=(return_column, "count"),
        factor_mean=(factor_name, "mean"),
        return_mean=(return_column, "mean"),
        return_median=(return_column, "median"),
        win_rate=(return_column, lambda values: (values > 0).mean()),
    ).reset_index()

    low_bucket = bucket_summary.sort_values("factor_bucket").head(1).iloc[0]
    high_bucket = bucket_summary.sort_values("factor_bucket").tail(1).iloc[0]

    return {
        "row_count": int(len(analysis_panel)),
        "bucket_count": int(analysis_panel["factor_bucket"].nunique()),
        "low_bucket_n": int(low_bucket["row_count"]),
        "high_bucket_n": int(high_bucket["row_count"]),
        "low_factor_mean": low_bucket["factor_mean"],
        "high_factor_mean": high_bucket["factor_mean"],
        "low_return_mean": low_bucket["return_mean"],
        "high_return_mean": high_bucket["return_mean"],
        "high_minus_low_return_mean": high_bucket["return_mean"] - low_bucket["return_mean"],
        "low_return_median": low_bucket["return_median"],
        "high_return_median": high_bucket["return_median"],
        "low_win_rate": low_bucket["win_rate"],
        "high_win_rate": high_bucket["win_rate"],
    }


def build_factor_robustness_rows(panel: pd.DataFrame) -> list[dict]:
    """Build robustness rows by overall sample, exclusions, groups, and tokens."""
    rows = []

    def append_row(check_type: str, subset_name: str, subset_panel: pd.DataFrame, factor_name: str) -> None:
        spread = calculate_factor_spread(subset_panel, factor_name)
        if spread is None:
            return

        row = {
            "check_type": check_type,
            "subset_name": subset_name,
            "factor_name": factor_name,
        }
        row.update(spread)
        rows.append(row)

    tokens = sorted(panel["token_symbol"].dropna().unique())

    for factor_name in ROBUSTNESS_FACTOR_NAMES:
        append_row("overall", "all_tokens", panel, factor_name)

        for token_symbol in tokens:
            append_row(
                "leave_one_token_out",
                "exclude_" + token_symbol.lower(),
                panel[panel["token_symbol"] != token_symbol],
                factor_name,
            )

        append_row(
            "named_exclusion",
            "exclude_pepe_arb",
            panel[~panel["token_symbol"].isin(["PEPE", "ARB"])],
            factor_name,
        )
        append_row(
            "named_exclusion",
            "exclude_meme_layer2",
            panel[~panel["token_group"].isin(["meme", "layer2"])],
            factor_name,
        )

        for token_group, group_panel in panel.groupby("token_group"):
            append_row("token_group", str(token_group), group_panel, factor_name)

        for token_symbol, token_panel in panel.groupby("token_symbol"):
            append_row("single_token", str(token_symbol), token_panel, factor_name)

    return rows


def write_factor_robustness_checks(panel: pd.DataFrame) -> None:
    """Write robustness checks for the most relevant candidate factors."""
    pd.DataFrame(build_factor_robustness_rows(panel)).to_csv(FACTOR_ROBUSTNESS_PATH, index=False)


def write_confirmation_forward_returns(panel: pd.DataFrame) -> None:
    """Write forward returns by CEX/DEX volume confirmation state."""
    summary = (
        panel.groupby("volume_state")
        .agg(
            row_count=("date", "count"),
            cex_vol_z_mean=("cex_vol_z", "mean"),
            dex_vol_z_mean=("dex_vol_z", "mean"),
            future_return_1d_mean=("future_return_1d", "mean"),
            future_return_3d_mean=("future_return_3d", "mean"),
            future_return_7d_mean=("future_return_7d", "mean"),
            future_return_1d_win_rate=("future_return_1d", lambda values: (values > 0).mean()),
            future_return_3d_win_rate=("future_return_3d", lambda values: (values > 0).mean()),
            future_return_7d_win_rate=("future_return_7d", lambda values: (values > 0).mean()),
        )
        .reset_index()
    )
    summary.to_csv(CONFIRMATION_FORWARD_RETURNS_PATH, index=False)


def plot_token_time_series(panel: pd.DataFrame, max_tokens: int = 20) -> None:
    """Plot price, CEX volume, and DEX volume for selected tokens."""
    tokens = sorted(panel["token_symbol"].dropna().unique())[:max_tokens]

    for token_symbol in tokens:
        token_panel = panel[panel["token_symbol"] == token_symbol].sort_values("date")
        if token_panel.empty:
            continue

        fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
        axes[0].plot(token_panel["date"], token_panel["price_usd"], color="#2563eb", linewidth=1.6)
        axes[0].set_title(f"{token_symbol} price, {token_panel['date'].min().date()} to {token_panel['date'].max().date()}")
        axes[0].set_ylabel("USD")
        apply_chart_style(axes[0])

        axes[1].plot(token_panel["date"], token_panel["cex_volume_usd"], label="CEX", color="#16a34a", linewidth=1.3)
        axes[1].plot(token_panel["date"], token_panel["dex_volume_usd"], label="DEX", color="#dc2626", linewidth=1.3)
        axes[1].set_title(f"{token_symbol} daily volume")
        axes[1].set_ylabel("USD")
        format_million_axis(axes[1])
        apply_chart_style(axes[1])
        axes[1].legend()

        fig.autofmt_xdate()
        fig.tight_layout()
        fig.savefig(TIME_SERIES_DIR / f"{token_symbol.lower()}_price_cex_dex_volume.png", dpi=160)
        plt.close(fig)


def plot_lead_lag_heatmap(lead_lag: pd.DataFrame) -> None:
    """Plot a lead-lag correlation heatmap."""
    if lead_lag.empty:
        return

    pivot = lead_lag.pivot(
        index="token_symbol",
        columns="lag",
        values="corr_cex_t_dex_t_plus_lag",
    ).sort_index()

    fig, ax = plt.subplots(figsize=(12, 5))
    image = ax.imshow(pivot, aspect="auto", cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_title("Lead-lag correlation: CEX_VOL_Z_t vs DEX_VOL_Z_t+lag")
    ax.set_xlabel("Lag")
    ax.set_ylabel("Token")
    fig.colorbar(image, ax=ax, label="Correlation")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "lead_lag_heatmap.png", dpi=160)
    plt.close(fig)


def plot_dex_share(panel: pd.DataFrame, max_tokens: int = 20) -> None:
    """Plot DEX share over time for selected tokens."""
    tokens = sorted(panel["token_symbol"].dropna().unique())[:max_tokens]
    fig, ax = plt.subplots(figsize=(12, 6))

    for token_symbol in tokens:
        token_panel = panel[panel["token_symbol"] == token_symbol].sort_values("date")
        ax.plot(token_panel["date"], token_panel["dex_share"], linewidth=1.2, label=token_symbol)

    ax.set_title(f"DEX share over time, {panel['date'].min().date()} to {panel['date'].max().date()}")
    ax.set_ylabel("DEX volume / total volume")
    ax.set_ylim(bottom=0)
    format_percent_axis(ax)
    apply_chart_style(ax)
    ax.legend(ncol=4, fontsize=8)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "dex_share_timeseries.png", dpi=160)
    plt.close(fig)


def plot_factor_forward_returns() -> None:
    """Plot forward returns by DEX volume z-score bucket."""
    if not FACTOR_FORWARD_RETURNS_PATH.exists():
        return

    summary = pd.read_csv(FACTOR_FORWARD_RETURNS_PATH)
    if summary.empty:
        return

    x = summary["dex_vol_z_bucket"].astype(str)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(x, summary["future_return_1d_mean"], marker="o", label="1d")
    ax.plot(x, summary["future_return_3d_mean"], marker="o", label="3d")
    ax.plot(x, summary["future_return_7d_mean"], marker="o", label="7d")
    ax.axhline(0, color="#444444", linewidth=0.8)
    ax.set_title("Future returns by DEX_VOL_Z bucket")
    ax.set_xlabel("DEX_VOL_Z bucket, low to high")
    ax.set_ylabel("Mean future return")
    format_percent_axis(ax)
    apply_chart_style(ax)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "factor_forward_return_bins.png", dpi=160)
    plt.close(fig)


def plot_confirmation_forward_returns() -> None:
    """Plot future returns by volume confirmation state."""
    if not CONFIRMATION_FORWARD_RETURNS_PATH.exists():
        return

    summary = pd.read_csv(CONFIRMATION_FORWARD_RETURNS_PATH)
    if summary.empty:
        return

    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(summary))
    ax.bar([position - 0.25 for position in x], summary["future_return_1d_mean"], width=0.25, label="1d")
    ax.bar(x, summary["future_return_3d_mean"], width=0.25, label="3d")
    ax.bar([position + 0.25 for position in x], summary["future_return_7d_mean"], width=0.25, label="7d")
    ax.axhline(0, color="#444444", linewidth=0.8)
    ax.set_xticks(list(x))
    ax.set_xticklabels(summary["volume_state"], rotation=20, ha="right")
    ax.set_title("Future returns by CEX / DEX volume state")
    ax.set_ylabel("Mean future return")
    format_percent_axis(ax)
    apply_chart_style(ax)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "confirmation_forward_return_bars.png", dpi=160)
    plt.close(fig)


def run(
    allow_missing: bool = False,
    drop_last_date: bool = True,
    min_token_days: int = 30,
) -> None:
    """Run the full research workflow."""
    ensure_output_dirs()

    if not has_research_input() and allow_missing:
        missing_paths = [
            str(path.relative_to(PROJECT_ROOT))
            for path in [RESEARCH_PANEL_INPUT_PATH, MERGED_PANEL_PATH, CEX_DAILY_PATH, DEX_DAILY_PATH]
            if not path.exists()
        ]
        print("No research input data found. Missing: " + ", ".join(missing_paths))
        print("Research structure is ready. Add A-side data, then rerun this script.")
        return

    load_analysis_dependencies()

    try:
        panel = load_panel()
    except FileNotFoundError as error:
        if allow_missing:
            print(error)
            print("Research structure is ready. Add A-side data, then rerun this script.")
            return
        raise

    panel = normalize_columns(panel)
    quality_report = write_data_quality_report(panel, min_token_days)
    short_tokens = quality_report.loc[quality_report["status"] == "too_short", "token_symbol"].tolist()
    if short_tokens:
        print("Skipping short token histories:", ", ".join(short_tokens))
    panel = filter_short_tokens(panel, min_token_days)

    if panel.empty:
        raise ValueError("No tokens have enough history after quality checks.")

    factor_panel = add_factors(panel, drop_last_date=drop_last_date)
    factor_panel.to_csv(FACTOR_PANEL_PATH, index=False)

    write_coverage_summary(factor_panel)
    write_dex_structure_daily(factor_panel)
    write_cex_dex_correlation(factor_panel)
    lead_lag = calculate_lead_lag(factor_panel)
    write_factor_forward_returns(factor_panel)
    write_candidate_factor_forward_returns(factor_panel)
    write_factor_robustness_checks(factor_panel)
    write_confirmation_forward_returns(factor_panel)

    plot_token_time_series(factor_panel)
    plot_lead_lag_heatmap(lead_lag)
    plot_dex_share(factor_panel)
    plot_factor_forward_returns()
    plot_confirmation_forward_returns()

    print("Wrote factor panel and summaries to", RESEARCH_DIR)
    print("Wrote figures to", FIGURES_DIR)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Exit successfully when A-side data files are not available yet.",
    )
    parser.add_argument(
        "--keep-last-date",
        action="store_true",
        help="Keep the latest date even if it may be an incomplete trading day.",
    )
    parser.add_argument(
        "--input-dir",
        default="data/processed",
        help="Directory containing merged_volume_panel.csv or CEX/DEX daily CSVs.",
    )
    parser.add_argument(
        "--research-dir",
        default="data/research",
        help="Directory for research CSV outputs.",
    )
    parser.add_argument(
        "--figures-dir",
        default="figures",
        help="Directory for figure outputs.",
    )
    parser.add_argument(
        "--min-token-days",
        type=int,
        default=30,
        help="Minimum token-day observations required for analysis.",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entrypoint."""
    args = parse_args()
    configure_paths(
        input_dir=resolve_path(args.input_dir),
        research_dir=resolve_path(args.research_dir),
        figures_dir=resolve_path(args.figures_dir),
    )
    run(
        allow_missing=args.allow_missing,
        drop_last_date=not args.keep_last_date,
        min_token_days=args.min_token_days,
    )


if __name__ == "__main__":
    main()
