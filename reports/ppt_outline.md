# PPT Outline

## Slide 1: Title

CEX 与 DEX 成交量关系及动量因子研究

## Slide 2: Research Question

- CEX 与 DEX 成交量是否同步、领先滞后或背离？
- CEX + DEX 同时放量是否比单边放量更有信息量？
- DEX_SHARE 是否反映交易场所结构变化？

## Slide 3: Data

- Frequency: daily
- Sample: 10-20 tokens
- CEX: Binance / OKX / Bybit
- DEX: GeckoTerminal / DefiLlama / Dune / manual export
- Core panel: date, token, price, CEX volume, DEX volume

## Slide 4: Factors

- CEX_VOL_Z
- DEX_VOL_Z
- DEX_SHARE
- VOL_DIVERGENCE
- CEX_DEX_CONFIRMATION

## Slide 5: Data Coverage

Use `data/research/coverage_summary.csv`.

Key points to fill:

- token count
- sample date range
- median DEX share
- missing date / duplicate row check

## Slide 6: CEX vs DEX Synchronization

Use `data/research/cex_dex_correlation.csv`.

Message:

- Same-day correlation measures whether CEX and DEX activity move together.
- Correlation is not causality and may reflect common market attention.

## Slide 7: Lead-lag Result

Insert `figures/lead_lag_heatmap.png`.

Message:

- Positive lag means CEX today is compared with future DEX.
- Negative lag means DEX today is compared with future CEX.

## Slide 8: DEX Share

Insert `figures/dex_share_timeseries.png`.

Message:

- DEX_SHARE shows how much trading activity happens on-chain relative to CEX.
- Changes may reflect venue migration, pool activity, or temporary event-driven flow.

## Slide 9: Factor vs Future Return

Insert `figures/factor_forward_return_bins.png`.

Message:

- Compare future 1d / 3d / 7d returns across DEX_VOL_Z buckets.
- Treat monotonicity as a hypothesis, not a proven strategy.

## Slide 10: Confirmation vs Single-sided Volume

Insert `figures/confirmation_forward_return_bars.png`.

Message:

- Compare both_high, cex_only, dex_only, and normal states.
- Main question: does cross-venue confirmation contain more information than single-venue activity?

## Slide 11: Preliminary Findings

- Finding 1: fill from `reports/research_findings_summary.md`.
- Finding 2: fill from `reports/research_findings_summary.md`.
- Finding 3: fill from `reports/research_findings_summary.md`.

## Slide 12: Limitations and Next Steps

- Short sample and limited DEX/CEX coverage.
- Daily frequency cannot prove intraday causality.
- Add events, wallet-level DEX behavior, and robustness tests next.

## Speaker Notes

- Use careful wording: "associated with", "consistent with", "suggests", not "proves".
- Separate chain facts, statistical relationships, and strategy hypotheses.
- If using mock outputs, explicitly label them as pipeline validation only.
