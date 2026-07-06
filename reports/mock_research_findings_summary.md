# Research Findings Summary

This summary is generated from the current research CSV outputs. Treat mock-run conclusions as pipeline tests, not market findings.

## Data Coverage

- Token count: 5
- Date range: 2026-01-01 to 2026-04-29
- Token-day rows: 595
- Median DEX share across token medians: 1.52%

## Data Checks

- Tokens passing minimum history check: 5
- Tokens flagged: 0
- Total missing dates across tokens: 0
- Total duplicate token-date rows: 0

## CEX vs DEX Same-day Correlation

- ARB: z-score corr 0.54, log-volume corr 0.51
- LINK: z-score corr 0.49, log-volume corr 0.41
- OP: z-score corr 0.45, log-volume corr 0.40

## Lead-lag Highlights

- ARB lag -3: corr 0.79, n=107
- ARB lag -6: corr 0.77, n=104
- LINK lag -3: corr 0.77, n=107
- AAVE lag -3: corr 0.75, n=107
- ARB lag -7: corr 0.74, n=103

## DEX_VOL_Z Buckets

- Lowest bucket 7d mean return: 2.08%
- Highest bucket 7d mean return: 3.29%

## Volume State Comparison

- both_high: 7d mean 3.31%, 7d win rate 60.00%, n=30
- cex_only: 7d mean 2.91%, 7d win rate 58.23%, n=79
- both_low_or_normal: 7d mean 2.61%, 7d win rate 58.99%, n=417
- dex_only: 7d mean 2.55%, 7d win rate 52.17%, n=69

## Figure Paths

- Lead-lag heatmap: `/Users/luchuanyu/on-chain-market-structure-analysis/figures/mock/lead_lag_heatmap.png`
- DEX share: `/Users/luchuanyu/on-chain-market-structure-analysis/figures/mock/dex_share_timeseries.png`
- Factor buckets: `/Users/luchuanyu/on-chain-market-structure-analysis/figures/mock/factor_forward_return_bins.png`
- Confirmation states: `/Users/luchuanyu/on-chain-market-structure-analysis/figures/mock/confirmation_forward_return_bars.png`
