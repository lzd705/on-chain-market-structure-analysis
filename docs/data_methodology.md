# Data Methodology

This document should explain how the data pipeline builds the CEX / DEX daily volume panel.

## Scope

- Frequency: daily
- Initial target window: recent 3-6 months
- Initial sample size: 10-20 tokens
- CEX coverage: 10 major spot exchanges
- DEX coverage: start with top 3 pools on the configured chain for each token

Current CEX exchanges:

```text
Binance
OKX
Bybit
KuCoin
Gate
Bitget
MEXC
HTX
Coinbase
Kraken
```

## Core outputs

- `data/processed/cex_volume_daily.csv`
- `data/processed/dex_pool_volume_daily.csv`
- `data/processed/dex_volume_daily.csv`
- `data/processed/price_daily.csv`
- `data/processed/merged_volume_panel.csv`

## Known limitations

- Raw wallet-level swap attribution is out of scope for the first version.
- CEX volume is major-exchange coverage, not guaranteed total CEX market volume.
- Coinbase and Kraken candles provide base volume, so quote volume is approximated as close price times base volume.
- DEX volume is single-chain top-pool coverage, not guaranteed total cross-chain DEX market volume.
- DEX pool selection must be documented per token in `data/processed/dex_pools.csv`.
