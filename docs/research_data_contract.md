# Research Data Contract

This is the interface B-side research expects from the A-side data pipeline.

## Preferred File

```text
data/processed/merged_volume_panel.csv
```

Required columns:

```text
date
token_symbol
price_usd
cex_volume_usd
dex_volume_usd
```

Optional but useful columns:

```text
return_1d
future_return_1d
future_return_3d
future_return_7d
exchange_count
included_exchanges
dex_pool_count
dex_list
pool_tvl_usd
```

## Accepted Fallback Files

If the merged panel is not ready, B-side scripts can merge:

```text
data/processed/cex_volume_daily.csv
data/processed/dex_volume_daily.csv
```

CEX fallback file must contain:

```text
date
token_symbol
close or price_usd
cex_volume_usd
```

DEX fallback file must contain:

```text
date
token_symbol
dex_volume_usd
```

## Formatting Rules

- `date` should be UTC daily date in `YYYY-MM-DD`.
- `token_symbol` should be uppercase and stable, for example `UNI`.
- Volumes should be in USD not token units.
- CEX and DEX rows should have one row per `date, token_symbol` after aggregation.
- If the latest date is partial, either exclude it or document it. B-side scripts drop the latest date by default.
- Missing DEX volume should be blank only when unknown; use `0` only when verified no volume.

## Before Handoff

Run:

```bash
python3 research/check_data_inputs.py --input-dir data/processed
```

Then inspect:

```text
data/research/data_input_check.csv
data/research/data_input_check.md
```

