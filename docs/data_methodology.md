# Data Methodology

This document should explain how the data pipeline builds the CEX / DEX daily volume panel.

## Scope

- Frequency: daily
- Initial target window: recent 3-6 months
- Current sample size: 30 tokens
- CEX coverage: 12 configured spot exchanges
- DEX coverage: global top 5 pools across configured chains for each token

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
Crypto.com
Upbit
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
- Coinbase, Kraken, and Crypto.com candles provide base volume, so quote volume is approximated as close price times base volume.
- Upbit uses the KRW market when available and converts each day through the Upbit KRW-USDT close; it falls back to the USDT market when needed.
- Each exchange contributes one preferred spot pair per token. The result is a consistent major-exchange proxy, not the sum of every pair traded on an exchange.
- DEX volume is multi-chain top-pool coverage, not guaranteed total cross-chain DEX market volume.
- DEX pool selection must be documented per token in `data/processed/dex_pools.csv`.
