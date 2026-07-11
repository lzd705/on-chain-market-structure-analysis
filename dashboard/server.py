"""Serve the local market-structure dashboard and persist workspace state."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_ROOT = Path(__file__).resolve().parent
STATIC_ROOT = DASHBOARD_ROOT / "static"
STATE_DIR = DASHBOARD_ROOT / "state"
STATE_PATH = STATE_DIR / "work_status.local.json"
STATE_TEMPLATE_PATH = STATE_DIR / "work_status.example.json"

DATA_CANDIDATES = [
    PROJECT_ROOT / "data/a_review/research/factor_panel.csv",
    PROJECT_ROOT / "data/research/factor_panel.csv",
    PROJECT_ROOT / "data/processed/research_panel.csv",
    PROJECT_ROOT / "data/processed/merged_volume_panel.csv",
]

FACTOR_RESULT_CANDIDATES = [
    PROJECT_ROOT / "data/a_review/research/candidate_factor_forward_returns.csv",
    PROJECT_ROOT / "data/research/candidate_factor_forward_returns.csv",
]

COVERAGE_CANDIDATES = [
    PROJECT_ROOT / "data/a_review/research/coverage_summary.csv",
    PROJECT_ROOT / "data/research/coverage_summary.csv",
]

SCOPE_SENSITIVITY_PATH = DASHBOARD_ROOT / "data/cex_scope_sensitivity.csv"
VENDOR_FILES = {
    "/vendor/chart.umd.js": DASHBOARD_ROOT / "node_modules/chart.js/dist/chart.umd.min.js",
    "/vendor/chartjs-adapter-date-fns.js": DASHBOARD_ROOT
    / "node_modules/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js",
    "/vendor/lucide.js": DASHBOARD_ROOT / "node_modules/lucide/dist/umd/lucide.min.js",
}

METRICS = {
    "price_usd": {"label": "价格", "unit": "USD", "format": "currency"},
    "cex_volume_usd": {"label": "CEX 成交额", "unit": "USD / day", "format": "currency"},
    "dex_volume_usd": {"label": "DEX 成交额", "unit": "USD / day", "format": "currency"},
    "dex_share": {"label": "Observed DEX Share", "unit": "%", "format": "percent"},
    "cex_to_dex_ratio": {"label": "CEX / DEX", "unit": "x", "format": "ratio"},
    "return_1d": {"label": "1 日收益", "unit": "%", "format": "percent"},
    "future_return_7d": {"label": "未来 7 日收益", "unit": "%", "format": "percent"},
    "cex_vol_z": {"label": "CEX Volume Z", "unit": "z-score", "format": "number"},
    "dex_vol_z": {"label": "DEX Volume Z", "unit": "z-score", "format": "number"},
    "volume_divergence": {"label": "Volume Divergence", "unit": "z-score", "format": "number"},
    "volume_growth_divergence_7d": {"label": "7 日量增速背离", "unit": "log ratio", "format": "number"},
    "dex_volume_to_tvl": {"label": "DEX Volume / TVL", "unit": "x", "format": "ratio"},
    "top_pool_volume_share": {"label": "Top Pool Share", "unit": "%", "format": "percent"},
    "dex_pool_herfindahl": {"label": "DEX Pool HHI", "unit": "index", "format": "number"},
    "active_pool_count": {"label": "活跃池数量", "unit": "pools", "format": "integer"},
    "mom_7d": {"label": "7 日动量", "unit": "%", "format": "percent"},
    "joint_volume_confirmed_mom_7d": {"label": "CEX+DEX 确认动量", "unit": "score", "format": "number"},
    "pool_diversified_dex_mom_7d": {"label": "池分散度确认动量", "unit": "score", "format": "number"},
}

BASE_COLUMNS = [
    "date",
    "token_symbol",
    "price_usd",
    "cex_volume_usd",
    "dex_volume_usd",
    "dex_share",
    "cex_to_dex_ratio",
    "exchange_count",
    "pool_count",
    "selected_chains",
    "included_exchanges",
    "included_dexes",
]


def find_first_existing(paths: list[Path]) -> Path | None:
    """Return the first existing file from a priority-ordered list."""
    return next((path for path in paths if path.exists()), None)


def resolve_panel_path() -> Path:
    """Resolve the richest available research panel, with an env override."""
    override = os.environ.get("DASHBOARD_DATA")
    if override:
        path = Path(override).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"DASHBOARD_DATA does not exist: {path}")
        return path

    path = find_first_existing(DATA_CANDIDATES)
    if path is None:
        candidates = ", ".join(str(item.relative_to(PROJECT_ROOT)) for item in DATA_CANDIDATES)
        raise FileNotFoundError(f"No dashboard panel found. Checked: {candidates}")
    return path


def parse_value(value: str | None) -> Any:
    """Convert CSV scalars to JSON-safe values without inventing missing data."""
    if value is None or value.strip() == "":
        return None
    try:
        number = float(value)
    except ValueError:
        return value
    if not math.isfinite(number):
        return None
    if number.is_integer() and abs(number) < 9_007_199_254_740_991:
        return int(number)
    return number


def read_csv(path: Path, columns: list[str] | None = None) -> tuple[list[dict[str, Any]], list[str]]:
    """Read a CSV into JSON-safe dictionaries, optionally selecting columns."""
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        source_columns = reader.fieldnames or []
        selected = source_columns if columns is None else [column for column in columns if column in source_columns]
        rows = [{column: parse_value(row.get(column)) for column in selected} for row in reader]
    return rows, source_columns


def relative_path(path: Path) -> str:
    """Render project paths without exposing unrelated local directories."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def build_dashboard_payload() -> dict[str, Any]:
    """Build the compact source-backed payload consumed by the browser app."""
    panel_path = resolve_panel_path()
    _, source_columns = read_csv(panel_path, [])
    available_metrics = [name for name in METRICS if name in source_columns]
    selected_columns = list(dict.fromkeys(BASE_COLUMNS + available_metrics))
    rows, _ = read_csv(panel_path, selected_columns)

    tokens = sorted({str(row["token_symbol"]) for row in rows if row.get("token_symbol")})
    dates = sorted(str(row["date"]) for row in rows if row.get("date"))
    non_null_cex = sum(row.get("cex_volume_usd") is not None for row in rows)
    non_null_dex = sum(row.get("dex_volume_usd") is not None for row in rows)

    panel_factor_path = panel_path.parent / "candidate_factor_forward_returns.csv"
    panel_coverage_path = panel_path.parent / "coverage_summary.csv"
    factor_path = panel_factor_path if panel_factor_path.exists() else find_first_existing(FACTOR_RESULT_CANDIDATES)
    factor_rows = read_csv(factor_path)[0] if factor_path else []
    coverage_path = panel_coverage_path if panel_coverage_path.exists() else find_first_existing(COVERAGE_CANDIDATES)
    coverage_rows = read_csv(coverage_path)[0] if coverage_path else []
    scope_rows = read_csv(SCOPE_SENSITIVITY_PATH)[0] if SCOPE_SENSITIVITY_PATH.exists() else []

    stat = panel_path.stat()
    return {
        "metadata": {
            "source_path": relative_path(panel_path),
            "source_modified_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            "row_count": len(rows),
            "token_count": len(tokens),
            "start_date": dates[0] if dates else None,
            "end_date": dates[-1] if dates else None,
            "cex_completeness": non_null_cex / len(rows) if rows else 0,
            "dex_completeness": non_null_dex / len(rows) if rows else 0,
            "grain": "token-day",
            "scope_note": "Observed DEX Share compares captured sources; it is not a global market-share estimate.",
        },
        "tokens": tokens,
        "metrics": {name: METRICS[name] for name in available_metrics},
        "rows": rows,
        "coverage": coverage_rows,
        "factor_results": factor_rows,
        "scope_sensitivity": scope_rows,
    }


def default_state() -> dict[str, Any]:
    """Load the committed initial workspace state."""
    if STATE_TEMPLATE_PATH.exists():
        with STATE_TEMPLATE_PATH.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    return {"selected_tokens": [], "metric": "dex_share", "notes": "", "checklist": []}


def load_state() -> dict[str, Any]:
    """Load local state, creating it from the template when needed."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_PATH.exists():
        save_state(default_state())
    with STATE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sanitize_state(payload: dict[str, Any]) -> dict[str, Any]:
    """Accept only bounded dashboard workspace fields."""
    selected_tokens = payload.get("selected_tokens", [])
    if not isinstance(selected_tokens, list):
        selected_tokens = []
    selected_tokens = [str(value)[:20] for value in selected_tokens[:20]]

    checklist = payload.get("checklist", [])
    if not isinstance(checklist, list):
        checklist = []
    clean_checklist = []
    for item in checklist[:30]:
        if not isinstance(item, dict):
            continue
        clean_checklist.append(
            {
                "id": str(item.get("id", ""))[:50],
                "label": str(item.get("label", ""))[:160],
                "done": bool(item.get("done", False)),
            }
        )

    metric = str(payload.get("metric", "dex_share"))
    if metric not in METRICS:
        metric = "dex_share"

    return {
        "selected_tokens": selected_tokens,
        "metric": metric,
        "date_start": str(payload.get("date_start", ""))[:10],
        "date_end": str(payload.get("date_end", ""))[:10],
        "normalize": bool(payload.get("normalize", False)),
        "notes": str(payload.get("notes", ""))[:10_000],
        "checklist": clean_checklist,
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }


def save_state(payload: dict[str, Any]) -> dict[str, Any]:
    """Persist state atomically so an interrupted save cannot corrupt it."""
    clean = sanitize_state(payload)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    temporary_path = STATE_PATH.with_suffix(".tmp")
    with temporary_path.open("w", encoding="utf-8") as handle:
        json.dump(clean, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    temporary_path.replace(STATE_PATH)
    return clean


class DashboardHandler(SimpleHTTPRequestHandler):
    """Static file and JSON API handler."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(STATIC_ROOT), **kwargs)

    def send_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def translate_path(self, path: str) -> str:
        """Expose only the pinned browser dependencies needed by the app."""
        request_path = urlparse(path).path
        if request_path in VENDOR_FILES:
            return str(VENDOR_FILES[request_path])
        return super().translate_path(path)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/dashboard":
            try:
                self.send_json(build_dashboard_payload())
            except Exception as error:
                self.send_json({"error": str(error)}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        if path == "/api/state":
            self.send_json(load_state())
            return
        if path == "/health":
            self.send_json({"status": "ok"})
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/api/state":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length > 128_000:
                raise ValueError("State payload is too large")
            payload = json.loads(self.rfile.read(content_length) or b"{}")
            if not isinstance(payload, dict):
                raise ValueError("State payload must be an object")
            self.send_json(save_state(payload))
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)

    def log_message(self, format: str, *args: Any) -> None:
        if self.path != "/health":
            super().log_message(format, *args)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local market-structure dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--data", help="Research panel path; overrides automatic discovery")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.data:
        data_path = Path(args.data).expanduser()
        if not data_path.is_absolute() and not data_path.exists():
            data_path = PROJECT_ROOT / data_path
        os.environ["DASHBOARD_DATA"] = str(data_path.resolve())
    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    print(f"Dashboard running at http://{args.host}:{args.port}")
    print(f"Data source: {relative_path(resolve_panel_path())}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
