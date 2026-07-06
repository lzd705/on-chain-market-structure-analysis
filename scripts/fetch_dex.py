"""Fetch daily DEX volume data from GeckoTerminal.

This first version is intentionally simple:
    - Read token config from config/tokens.csv
    - Find the top DEX pools on the configured chain for each token
    - Fetch daily OHLCV for those pools
    - Write data/processed/dex_pools.csv
    - Write data/processed/dex_pool_volume_daily.csv
    - Write data/processed/dex_volume_daily.csv
"""

import csv
import json
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime
from datetime import timezone
from pathlib import Path


TOKEN_CONFIG_PATH = Path("config/tokens.csv")
DEX_POOLS_OUTPUT_PATH = Path("data/processed/dex_pools.csv")
DEX_POOL_VOLUME_OUTPUT_PATH = Path("data/processed/dex_pool_volume_daily.csv")
DEX_VOLUME_OUTPUT_PATH = Path("data/processed/dex_volume_daily.csv")

GECKOTERMINAL_BASE_URL = "https://api.geckoterminal.com/api/v2"
LIMIT_DAYS = 180
REQUEST_SLEEP_SECONDS = 15.0
MAX_RETRIES = 3
MIN_HISTORY_DAYS = 120
MAX_POOL_CANDIDATES = 8
TOP_POOL_COUNT = 3


def safe_float(value) -> float:
    """Convert API numeric strings to float."""
    if value is None:
        return 0.0
    if value == "":
        return 0.0
    return float(value)


def get_retry_wait_seconds(status_code, retry_after) -> int:
    """Return wait seconds for rate-limited requests."""
    if status_code != 429:
        return 0

    if retry_after is None:
        return 65

    try:
        return int(retry_after)
    except ValueError:
        return 65


def get_status_code(error):
    """Extract an HTTP status code from urllib errors or error text."""
    status_code = getattr(error, "code", None)

    if status_code is not None:
        return status_code

    if "HTTP Error 429" in str(error):
        return 429

    return None


def get_token_side(pool, chain: str, contract_address: str) -> str:
    """Return base or quote, depending on where the target token is in the pool."""
    target_id = (chain + "_" + contract_address).lower()

    if pool.get("base_token_id", "").lower() == target_id:
        return "base"

    if pool.get("quote_token_id", "").lower() == target_id:
        return "quote"

    return "base"


def sort_pools_by_volume(pools):
    """Sort GeckoTerminal pools by 24h volume, highest first."""
    def get_volume(pool):
        attributes = pool.get("attributes", {})
        volume_usd = attributes.get("volume_usd", {})
        return safe_float(volume_usd.get("h24"))

    return sorted(pools, key=get_volume, reverse=True)


def request_json(url: str):
    """Request JSON from GeckoTerminal."""
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    attempt = 0

    while attempt < MAX_RETRIES:
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                text = response.read().decode("utf-8")
                data = json.loads(text)
                return data
        except Exception as error:
            status_code = get_status_code(error)
            retry_after = None

            if hasattr(error, "headers"):
                retry_after = error.headers.get("Retry-After")

            wait_seconds = get_retry_wait_seconds(status_code, retry_after)

            if wait_seconds <= 0:
                raise

            attempt = attempt + 1
            print("Rate limited. Waiting %s seconds before retry." % wait_seconds)
            time.sleep(wait_seconds)

    raise RuntimeError("Failed after retries: %s" % url)


def read_token_config(path: Path):
    """Read token config rows."""
    with path.open("r", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    return rows


def build_pool_result(pool_data):
    """Convert GeckoTerminal pool data into our pool row."""
    attributes = pool_data.get("attributes", {})
    relationships = pool_data.get("relationships", {})
    dex_data = relationships.get("dex", {}).get("data", {})
    base_token_data = relationships.get("base_token", {}).get("data", {})
    quote_token_data = relationships.get("quote_token", {}).get("data", {})
    volume_usd = attributes.get("volume_usd", {})

    result = {
        "pool_address": attributes.get("address", ""),
        "dex": dex_data.get("id", ""),
        "pool_name": attributes.get("name", ""),
        "pool_tvl_usd": safe_float(attributes.get("reserve_in_usd")),
        "volume_24h_usd": safe_float(volume_usd.get("h24")),
        "base_token_id": base_token_data.get("id", ""),
        "quote_token_id": quote_token_data.get("id", ""),
    }

    return result


def choose_main_pool(pools):
    """Choose the highest-volume pool from GeckoTerminal pool data."""
    sorted_pools = sort_pools_by_volume(pools)

    if len(sorted_pools) == 0:
        return None

    return build_pool_result(sorted_pools[0])


def choose_top_pools(pools, pool_count):
    """Choose top pools by 24h volume from GeckoTerminal pool data."""
    sorted_pools = sort_pools_by_volume(pools)
    selected_pool_data = sorted_pools[:pool_count]

    selected_pools = []
    for pool_data in selected_pool_data:
        selected_pools.append(build_pool_result(pool_data))

    return selected_pools


def add_token_fields(pool, token, pool_rank):
    """Add token metadata to a selected pool row."""
    chain = token["chain"]
    contract_address = token["contract_address"]

    pool["token_symbol"] = token["token_symbol"]
    pool["chain"] = chain
    pool["contract_address"] = contract_address
    pool["pool_rank"] = pool_rank
    pool["ohlcv_token"] = get_token_side(pool, chain, contract_address)

    return pool


def find_main_pool(token):
    """Find one main pool for a token."""
    chain = token["chain"]
    contract_address = token["contract_address"]

    path = "/networks/%s/tokens/%s/pools" % (chain, contract_address)
    url = GECKOTERMINAL_BASE_URL + path

    data = request_json(url)
    pools = data.get("data", [])
    pool = choose_main_pool(pools)

    if pool is None:
        return None

    add_token_fields(pool, token, 1)

    return pool


def find_pool_with_ohlcv(token):
    """Find a pool with enough daily OHLCV history."""
    chain = token["chain"]
    contract_address = token["contract_address"]

    path = "/networks/%s/tokens/%s/pools" % (chain, contract_address)
    url = GECKOTERMINAL_BASE_URL + path

    data = request_json(url)
    pools = data.get("data", [])
    sorted_pools = sort_pools_by_volume(pools)
    candidates = sorted_pools[:MAX_POOL_CANDIDATES]

    fallback_pool = None
    fallback_ohlcv_list = []

    time.sleep(REQUEST_SLEEP_SECONDS)

    for pool_data in candidates:
        pool = build_pool_result(pool_data)
        pool["token_symbol"] = token["token_symbol"]
        pool["chain"] = chain
        pool["contract_address"] = contract_address
        pool["ohlcv_token"] = get_token_side(pool, chain, contract_address)

        try:
            ohlcv_list = fetch_pool_ohlcv(pool)
        except Exception as error:
            print("Candidate failed %s: %s" % (pool["pool_name"], error))
            time.sleep(REQUEST_SLEEP_SECONDS)
            continue

        row_count = len(ohlcv_list)

        if row_count > len(fallback_ohlcv_list):
            fallback_pool = pool
            fallback_ohlcv_list = ohlcv_list

        if row_count >= MIN_HISTORY_DAYS:
            time.sleep(REQUEST_SLEEP_SECONDS)
            return pool, ohlcv_list

        print(
            "Candidate has short history for %s: %s rows (%s)"
            % (token["token_symbol"], row_count, pool["pool_name"])
        )
        time.sleep(REQUEST_SLEEP_SECONDS)

    if fallback_pool is None:
        return None, []

    return fallback_pool, fallback_ohlcv_list


def find_top_pools_with_ohlcv(token):
    """Find top pools with enough daily OHLCV history for one token."""
    chain = token["chain"]
    contract_address = token["contract_address"]

    path = "/networks/%s/tokens/%s/pools" % (chain, contract_address)
    url = GECKOTERMINAL_BASE_URL + path

    data = request_json(url)
    pools = data.get("data", [])
    sorted_pools = sort_pools_by_volume(pools)
    candidates = sorted_pools[:MAX_POOL_CANDIDATES]

    selected = []
    fallback = []

    time.sleep(REQUEST_SLEEP_SECONDS)

    for pool_data in candidates:
        pool = build_pool_result(pool_data)
        pool_rank = len(selected) + 1
        add_token_fields(pool, token, pool_rank)

        try:
            ohlcv_list = fetch_pool_ohlcv(pool)
        except Exception as error:
            print("Candidate failed %s: %s" % (pool["pool_name"], error))
            time.sleep(REQUEST_SLEEP_SECONDS)
            continue

        row_count = len(ohlcv_list)

        if row_count > 0:
            fallback.append((pool, ohlcv_list))

        if row_count >= MIN_HISTORY_DAYS:
            selected.append((pool, ohlcv_list))
            print(
                "Selected %s pool %s: %s"
                % (token["token_symbol"], len(selected), pool["pool_name"])
            )

        if len(selected) >= TOP_POOL_COUNT:
            time.sleep(REQUEST_SLEEP_SECONDS)
            return selected

        if row_count < MIN_HISTORY_DAYS:
            print(
                "Candidate has short history for %s: %s rows (%s)"
                % (token["token_symbol"], row_count, pool["pool_name"])
            )

        time.sleep(REQUEST_SLEEP_SECONDS)

    if len(selected) > 0:
        return selected

    return fallback[:TOP_POOL_COUNT]


def convert_ohlcv_row(ohlcv, pool):
    """Convert one GeckoTerminal OHLCV list into one output CSV row."""
    timestamp = int(ohlcv[0])
    date = datetime.fromtimestamp(timestamp, timezone.utc).strftime("%Y-%m-%d")

    row = {
        "date": date,
        "token_symbol": pool["token_symbol"],
        "chain": pool["chain"],
        "dex": pool["dex"],
        "pool_address": pool["pool_address"],
        "pool_name": pool["pool_name"],
        "open": float(ohlcv[1]),
        "high": float(ohlcv[2]),
        "low": float(ohlcv[3]),
        "close": float(ohlcv[4]),
        "dex_volume_usd": float(ohlcv[5]),
        "pool_tvl_usd": pool["pool_tvl_usd"],
    }

    return row


def aggregate_dex_pool_rows(rows):
    """Aggregate pool-level DEX volume rows into token-date rows."""
    groups = {}

    for row in rows:
        key = (row["date"], row["token_symbol"], row["chain"])

        if key not in groups:
            groups[key] = {
                "date": row["date"],
                "token_symbol": row["token_symbol"],
                "chain": row["chain"],
                "dex_volume_usd": 0.0,
                "pool_addresses": set(),
                "dexes": set(),
            }

        groups[key]["dex_volume_usd"] += float(row["dex_volume_usd"])
        groups[key]["pool_addresses"].add(row["pool_address"])
        groups[key]["dexes"].add(row["dex"])

    result = []
    for item in groups.values():
        pool_addresses = sorted(item["pool_addresses"])
        dexes = sorted(item["dexes"])

        result.append(
            {
                "date": item["date"],
                "token_symbol": item["token_symbol"],
                "chain": item["chain"],
                "dex_volume_usd": item["dex_volume_usd"],
                "pool_count": len(pool_addresses),
                "included_dexes": ";".join(dexes),
                "included_pool_addresses": ";".join(pool_addresses),
            }
        )

    return sorted(result, key=lambda row: (row["token_symbol"], row["date"]))


def filter_complete_dates(rows, expected_token_count):
    """Keep only dates that have all expected tokens."""
    tokens_by_date = {}

    for row in rows:
        date = row["date"]
        token_symbol = row["token_symbol"]

        if date not in tokens_by_date:
            tokens_by_date[date] = set()

        tokens_by_date[date].add(token_symbol)

    complete_dates = set()
    for date, token_symbols in tokens_by_date.items():
        if len(token_symbols) == expected_token_count:
            complete_dates.add(date)

    result = []
    for row in rows:
        if row["date"] in complete_dates:
            result.append(row)

    return sorted(result, key=lambda row: (row["token_symbol"], row["date"]))


def fetch_pool_ohlcv(pool):
    """Fetch daily OHLCV for one pool."""
    chain = pool["chain"]
    pool_address = pool["pool_address"]

    query = {
        "aggregate": "1",
        "limit": str(LIMIT_DAYS),
        "currency": "usd",
        "token": pool.get("ohlcv_token", "base"),
    }

    encoded_query = urllib.parse.urlencode(query)
    path = "/networks/%s/pools/%s/ohlcv/day" % (chain, pool_address)
    url = GECKOTERMINAL_BASE_URL + path + "?" + encoded_query

    data = request_json(url)
    attributes = data.get("data", {}).get("attributes", {})
    ohlcv_list = attributes.get("ohlcv_list", [])

    return ohlcv_list


def write_pool_rows(pools, output_path: Path):
    """Write selected pools to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "token_symbol",
        "chain",
        "contract_address",
        "pool_rank",
        "dex",
        "pool_address",
        "pool_name",
        "pool_tvl_usd",
        "volume_24h_usd",
        "ohlcv_token",
        "base_token_id",
        "quote_token_id",
    ]

    with output_path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(pools)


def write_pool_volume_rows(rows, output_path: Path):
    """Write pool-level DEX volume rows to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "date",
        "token_symbol",
        "chain",
        "dex",
        "pool_address",
        "pool_name",
        "open",
        "high",
        "low",
        "close",
        "dex_volume_usd",
        "pool_tvl_usd",
    ]

    rows = sorted(rows, key=lambda row: (row["token_symbol"], row["date"]))

    with output_path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_volume_rows(rows, output_path: Path):
    """Write aggregated DEX volume rows to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "date",
        "token_symbol",
        "chain",
        "dex_volume_usd",
        "pool_count",
        "included_dexes",
        "included_pool_addresses",
    ]

    rows = sorted(rows, key=lambda row: (row["token_symbol"], row["date"]))

    with output_path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Fetch DEX data into processed CSV files."""
    token_rows = read_token_config(TOKEN_CONFIG_PATH)
    selected_pools = []
    pool_volume_rows = []

    for token in token_rows:
        token_symbol = token["token_symbol"]

        try:
            pool_results = find_top_pools_with_ohlcv(token)
        except Exception as error:
            print("Failed %s: %s" % (token_symbol, error))
            continue

        if len(pool_results) == 0:
            print("No usable pool found for %s" % token_symbol)
            continue

        for pool_result in pool_results:
            pool = pool_result[0]
            ohlcv_list = pool_result[1]
            selected_pools.append(pool)

            print(
                "Using %s pool: %s (%s)"
                % (token_symbol, pool["pool_name"], pool["pool_address"])
            )

            for ohlcv in ohlcv_list:
                row = convert_ohlcv_row(ohlcv, pool)
                pool_volume_rows.append(row)

        print("Fetched %s DEX pools: %s" % (token_symbol, len(pool_results)))
        time.sleep(REQUEST_SLEEP_SECONDS)

    volume_rows = aggregate_dex_pool_rows(pool_volume_rows)
    volume_rows = filter_complete_dates(volume_rows, len(token_rows))

    write_pool_rows(selected_pools, DEX_POOLS_OUTPUT_PATH)
    write_pool_volume_rows(pool_volume_rows, DEX_POOL_VOLUME_OUTPUT_PATH)
    write_volume_rows(volume_rows, DEX_VOLUME_OUTPUT_PATH)

    print("Wrote %s pools to %s" % (len(selected_pools), DEX_POOLS_OUTPUT_PATH))
    print("Wrote %s pool rows to %s" % (len(pool_volume_rows), DEX_POOL_VOLUME_OUTPUT_PATH))
    print("Wrote %s rows to %s" % (len(volume_rows), DEX_VOLUME_OUTPUT_PATH))


if __name__ == "__main__":
    main()
