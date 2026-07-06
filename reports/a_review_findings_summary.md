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

## Candidate Factor Buckets

- cex_dex_ratio_z: high-minus-low 7d mean spread 0.47% (low -2.76%, high -2.29%)
- cex_dex_z_product: high-minus-low 7d mean spread 0.46% (low -2.31%, high -1.85%)
- cex_vol_growth_7d: high-minus-low 7d mean spread 0.19% (low -2.47%, high -2.28%)
- cex_volume_confirmed_mom_7d: high-minus-low 7d mean spread 1.78% (low -4.61%, high -2.83%)
- dex_share_change_7d: high-minus-low 7d mean spread 0.46% (low -3.56%, high -3.10%)
- dex_share_confirmed_mom_7d: high-minus-low 7d mean spread -0.94% (low -2.34%, high -3.28%)
- dex_share_x_dex_vol_z: high-minus-low 7d mean spread 1.47% (low -3.47%, high -2.00%)
- dex_share_z: high-minus-low 7d mean spread -0.05% (low -2.50%, high -2.54%)
- dex_vol_growth_7d: high-minus-low 7d mean spread 0.34% (low -2.69%, high -2.34%)
- dex_volume_confirmed_mom_7d: high-minus-low 7d mean spread 1.46% (low -3.58%, high -2.12%)
- joint_vol_z_mean: high-minus-low 7d mean spread -1.02% (low -2.35%, high -3.37%)
- joint_volume_confirmed_mom_7d: high-minus-low 7d mean spread 1.70% (low -4.08%, high -2.38%)
- mom_14d: high-minus-low 7d mean spread 0.75% (low -2.87%, high -2.12%)
- mom_30d: high-minus-low 7d mean spread -2.39% (low 2.00%, high -0.39%)
- mom_7d: high-minus-low 7d mean spread 0.04% (low -3.19%, high -3.15%)
- mom_7d_skip_1d: high-minus-low 7d mean spread -0.34% (low -2.74%, high -3.08%)
- momentum_vol_adj_7d: high-minus-low 7d mean spread 0.63% (low -3.70%, high -3.06%)
- realized_vol_14d: high-minus-low 7d mean spread -0.00% (low -2.63%, high -2.63%)
- reversal_1d: high-minus-low 7d mean spread -1.21% (low -3.00%, high -4.21%)
- total_vol_growth_7d: high-minus-low 7d mean spread 0.51% (low -2.81%, high -2.30%)
- total_vol_z: high-minus-low 7d mean spread -1.58% (low -2.86%, high -4.43%)
- volume_growth_divergence_7d: high-minus-low 7d mean spread 1.04% (low -2.04%, high -1.00%)

## Robustness Checks

- cex_volume_confirmed_mom_7d: overall spread 2.41%, excluding PEPE+ARB 2.09%, change -0.32%
- joint_volume_confirmed_mom_7d: overall spread 2.03%, excluding PEPE+ARB 1.88%, change -0.15%
- dex_volume_confirmed_mom_7d: overall spread 1.69%, excluding PEPE+ARB 1.28%, change -0.40%
- dex_share_x_dex_vol_z: overall spread 1.05%, excluding PEPE+ARB 0.14%, change -0.91%
- volume_growth_divergence_7d: overall spread 0.69%, excluding PEPE+ARB 0.35%, change -0.34%
- mom_14d: overall spread 0.56%, excluding PEPE+ARB 0.41%, change -0.14%

Strongest token-group spreads:
- layer2 / joint_volume_confirmed_mom_7d: 5.48%, n=326
- layer2 / cex_volume_confirmed_mom_7d: 5.41%, n=326
- layer2 / mom_30d: 5.29%, n=284
- layer2 / dex_volume_confirmed_mom_7d: 4.39%, n=326
- layer2 / dex_share_x_dex_vol_z: 3.73%, n=326

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
