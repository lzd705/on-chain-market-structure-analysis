# Research Findings Summary

This summary is generated from the selected research CSV outputs. If the inputs are mock data, treat the numbers as pipeline validation only.

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

## Candidate Factor Buckets

- cex_dex_ratio_z: high-minus-low 7d mean spread -1.13% (low 4.21%, high 3.09%)
- cex_dex_z_product: high-minus-low 7d mean spread -1.22% (low 4.36%, high 3.14%)
- cex_vol_growth_7d: high-minus-low 7d mean spread 1.48% (low 2.03%, high 3.50%)
- cex_volume_confirmed_mom_7d: high-minus-low 7d mean spread 0.51% (low 4.43%, high 4.93%)
- dex_share_change_7d: high-minus-low 7d mean spread 0.31% (low 3.06%, high 3.37%)
- dex_share_confirmed_mom_7d: high-minus-low 7d mean spread 0.13% (low 3.83%, high 3.96%)
- dex_share_x_dex_vol_z: high-minus-low 7d mean spread 1.67% (low 1.92%, high 3.60%)
- dex_share_z: high-minus-low 7d mean spread 2.40% (low 2.63%, high 5.04%)
- dex_vol_growth_7d: high-minus-low 7d mean spread 2.44% (low 1.59%, high 4.03%)
- dex_volume_confirmed_mom_7d: high-minus-low 7d mean spread 1.15% (low 3.53%, high 4.68%)
- joint_vol_z_mean: high-minus-low 7d mean spread 1.04% (low 2.41%, high 3.45%)
- joint_volume_confirmed_mom_7d: high-minus-low 7d mean spread 1.27% (low 4.10%, high 5.37%)
- mom_14d: high-minus-low 7d mean spread 15.12% (low -7.43%, high 7.69%)
- mom_30d: high-minus-low 7d mean spread 13.28% (low -7.37%, high 5.91%)
- mom_7d: high-minus-low 7d mean spread 13.28% (low -6.19%, high 7.09%)
- mom_7d_skip_1d: high-minus-low 7d mean spread 13.24% (low -5.95%, high 7.29%)
- momentum_vol_adj_7d: high-minus-low 7d mean spread 13.63% (low -6.32%, high 7.31%)
- realized_vol_14d: high-minus-low 7d mean spread 3.47% (low 0.97%, high 4.44%)
- reversal_1d: high-minus-low 7d mean spread -6.40% (low 6.14%, high -0.26%)
- total_vol_growth_7d: high-minus-low 7d mean spread 1.36% (low 2.03%, high 3.39%)
- total_vol_z: high-minus-low 7d mean spread 0.97% (low 2.95%, high 3.92%)
- volume_growth_divergence_7d: high-minus-low 7d mean spread 0.99% (low 2.30%, high 3.29%)

## Robustness Checks

- mom_14d: overall spread 14.80%, excluding PEPE+ARB 14.30%, change -0.50%
- mom_30d: overall spread 12.92%, excluding PEPE+ARB 12.21%, change -0.71%
- dex_share_x_dex_vol_z: overall spread 1.79%, excluding PEPE+ARB -0.37%, change -2.16%
- volume_growth_divergence_7d: overall spread 0.96%, excluding PEPE+ARB -0.44%, change -1.40%
- joint_volume_confirmed_mom_7d: overall spread 0.68%, excluding PEPE+ARB 1.44%, change 0.76%
- total_vol_z: overall spread 0.64%, excluding PEPE+ARB 0.02%, change -0.62%

Strongest token-group spreads:
- layer2 / mom_14d: 15.55%, n=196
- defi / mom_14d: 13.90%, n=196
- layer2 / mom_30d: 13.68%, n=164
- infra / mom_14d: 13.63%, n=98
- defi / mom_30d: 12.83%, n=164

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
