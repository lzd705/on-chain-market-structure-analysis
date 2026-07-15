# Data Pipeline

The data pipeline is responsible for producing a clean daily panel that the research branch can use directly.

## Pipeline flow

```text
config/tokens.csv
  -> fetch CEX daily volume
  -> fetch DEX pool-level daily volume
  -> aggregate multi-chain DEX top 5 pools by token/date
  -> merge CEX and DEX rows by date/token
  -> calculate basic volume metrics
  -> export merged_volume_panel.csv
  -> calculate realized and future returns
  -> export research_panel.csv
  -> validate curated event candidates
  -> export event_table.csv
```

## CEX outputs

`data/processed/cex_exchange_volume_daily.csv` stores all successfully fetched
exchange-level observations.

`data/processed/cex_exchange_coverage.csv` stores the available history for
each token and exchange. An exchange enters a token's fixed aggregation set
when it has at least 120 daily observations. A token needs at least three
stable exchanges and Binance, which supplies the reference close price.

If all configured exchanges are stable, all are used. Otherwise, all available
stable exchanges are used. A token-date is written only when every exchange
in that token's fixed set is present, so a temporary API failure is not
mistaken for a drop in trading volume.

`data/processed/cex_volume_daily.csv` stores the resulting token-date totals.

## DEX outputs

```text
dex_pools.csv
  selected global top 5 pools per token across configured chains

dex_pool_volume_daily.csv
  pool-level daily DEX volume

dex_volume_daily.csv
  token-date daily DEX volume aggregated from selected pools
```

## Current merged panel columns

```text
date
token_symbol
price_usd
cex_volume_usd
dex_volume_usd
total_volume_usd
dex_share
cex_to_dex_ratio
exchange_count
included_exchanges
chain
selected_chains
pool_count
included_dexes
included_pool_addresses
```

## Research panel

`research_panel.csv` keeps the merged panel columns and adds return columns used
for factor research.

```text
return_1d
future_return_1d
future_return_3d
future_return_7d
```

Calculation:

```text
return_1d = price_t / price_{t-1} - 1
future_return_1d = price_{t+1} / price_t - 1
future_return_3d = price_{t+3} / price_t - 1
future_return_7d = price_{t+7} / price_t - 1
```

`future_return_*` columns use future prices, so they are labels for factor
testing only. They should not be used as same-day factor inputs.

## Event table

`data/curated/event_candidates.csv` stores source-backed unlock, airdrop, and
CEX listing candidates. Event discovery is curated because the project does
not use a paid historical event API.

`scripts/build_event_table.py` makes the transformation reproducible. It
validates tokens, event types, UTC dates, numeric fields, and sources; removes
duplicates; calculates the `-7/+14` event window; and writes
`data/processed/event_table.csv`.

Unknown event sizes remain blank. The pipeline does not estimate them or label
events as bullish or bearish.

## Next factor columns

```text
cex_vol_z_30d
dex_vol_z_30d
cex_volume_growth_7d
dex_volume_growth_7d
volume_divergence
```
