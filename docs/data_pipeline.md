# Data Pipeline

The data pipeline is responsible for producing a clean daily panel that the research branch can use directly.

## Pipeline flow

```text
config/tokens.csv
  -> fetch CEX daily volume
  -> fetch DEX daily volume
  -> fetch daily price
  -> clean and align
  -> calculate metrics
  -> export merged_volume_panel.csv
```

## Expected final panel columns

```text
date
token_symbol
price_usd
return_1d
future_return_1d
future_return_3d
future_return_7d
cex_volume_usd
dex_volume_usd
total_volume_usd
dex_share
cex_vol_z_30d
dex_vol_z_30d
cex_volume_growth_7d
dex_volume_growth_7d
volume_divergence
```

