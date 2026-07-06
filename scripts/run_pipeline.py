"""Run the full data pipeline in order.

Default behavior:
    - Rebuild merged_volume_panel.csv from existing processed CSV files.

Optional behavior:
    - Use --fetch to refresh CEX and DEX data before rebuilding the panel.
"""

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts import build_panel as build_panel_module
from scripts import fetch_cex as fetch_cex_module
from scripts import fetch_dex as fetch_dex_module


def run_pipeline(
    fetch=False,
    fetch_cex=None,
    fetch_dex=None,
    build_panel=None,
):
    """Run the data pipeline."""
    if fetch_cex is None:
        fetch_cex = fetch_cex_module.main

    if fetch_dex is None:
        fetch_dex = fetch_dex_module.main

    if build_panel is None:
        build_panel = build_panel_module.main

    if fetch:
        print("Refreshing CEX data")
        fetch_cex()
        print("Refreshing DEX data")
        fetch_dex()

    print("Building merged panel")
    build_panel()


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="Refresh CEX and DEX API data before rebuilding the merged panel.",
    )

    return parser.parse_args()


def main() -> None:
    """Run the pipeline from the command line."""
    args = parse_args()
    run_pipeline(fetch=args.fetch)


if __name__ == "__main__":
    main()
