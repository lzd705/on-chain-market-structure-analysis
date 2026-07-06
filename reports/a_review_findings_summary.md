# Research Findings Summary

This summary is generated from the selected research CSV outputs. If the inputs are mock data, treat the numbers as pipeline validation only.

## Data Coverage

- Token count: 10
- Date range: 2026-01-08 to 2026-07-05
- Token-day rows: 1,790
- Median DEX share across token medians: 3.69%

## Data Checks

- Tokens passing minimum history check: 10
- Tokens flagged: 0
- Total missing dates across tokens: 0
- Total duplicate token-date rows: 0

## CEX vs DEX Same-day Correlation

- PEPE: z-score corr 0.83, log-volume corr 0.87
- ARB: z-score corr 0.80, log-volume corr 0.77
- UNI: z-score corr 0.73, log-volume corr 0.66

## Lead-lag Highlights

- PEPE lag 0: corr 0.83, n=170
- ARB lag 0: corr 0.80, n=170
- UNI lag 0: corr 0.73, n=170
- LINK lag 0: corr 0.66, n=170
- ENA lag 0: corr 0.63, n=170

## DEX_VOL_Z Buckets

- Lowest bucket 7d mean return: -0.95%
- Highest bucket 7d mean return: -2.76%

## Volume State Comparison

- both_high: 7d mean -1.16%, 7d win rate 42.22%, n=135
- dex_only: 7d mean -2.27%, 7d win rate 36.36%, n=132
- both_low_or_normal: 7d mean -2.35%, 7d win rate 36.75%, n=1426
- cex_only: 7d mean -7.62%, 7d win rate 23.71%, n=97

## Figure Paths

- Lead-lag heatmap: `/Users/luchuanyu/on-chain-market-structure-analysis/figures/a_review/lead_lag_heatmap.png`
- DEX share: `/Users/luchuanyu/on-chain-market-structure-analysis/figures/a_review/dex_share_timeseries.png`
- Factor buckets: `/Users/luchuanyu/on-chain-market-structure-analysis/figures/a_review/factor_forward_return_bins.png`
- Confirmation states: `/Users/luchuanyu/on-chain-market-structure-analysis/figures/a_review/confirmation_forward_return_bars.png`
