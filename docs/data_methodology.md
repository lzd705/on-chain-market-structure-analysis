# Data Methodology

This document should explain how the data pipeline builds the CEX / DEX daily volume panel.

## Scope

- Frequency: daily
- Initial target window: recent 3-6 months
- Initial sample size: 10-20 tokens
- CEX coverage: start with 1-2 major spot exchanges
- DEX coverage: start with daily DEX volume, preferably pool-level when available

## Core outputs

- `data/processed/cex_volume_daily.csv`
- `data/processed/dex_volume_daily.csv`
- `data/processed/price_daily.csv`
- `data/processed/merged_volume_panel.csv`

## Known limitations

- Raw wallet-level swap attribution is out of scope for the first version.
- CEX coverage may be incomplete if only one exchange is available.
- DEX volume source and pool selection must be documented per token.

