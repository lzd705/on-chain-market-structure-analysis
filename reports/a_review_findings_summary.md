# Research Findings Summary

This summary is generated from the selected research CSV outputs. If the inputs are mock data, treat the numbers as pipeline validation only.

## Data Coverage

- Token count: 10
- Date range: 2026-01-08 to 2026-07-05
- Token-day rows: 1,790
- Median DEX share across token medians: 3.92%

## Data Checks

- Tokens passing minimum history check: 10
- Tokens flagged: 0
- Total missing dates across tokens: 0
- Total duplicate token-date rows: 0

## CEX vs DEX Same-day Correlation

- PEPE: z-score corr 0.83, log-volume corr 0.87
- ARB: z-score corr 0.80, log-volume corr 0.77
- UNI: z-score corr 0.71, log-volume corr 0.69

## Lead-lag Highlights

- PEPE lag 0: corr 0.83, n=170
- ARB lag 0: corr 0.80, n=170
- UNI lag 0: corr 0.71, n=170
- LINK lag 0: corr 0.66, n=170
- ENA lag 0: corr 0.63, n=170

## DEX_VOL_Z Buckets

- Lowest bucket 7d mean return: -1.08%
- Highest bucket 7d mean return: -2.69%

## Candidate Factor Buckets

- cex_dex_ratio_z: high-minus-low 7d mean spread 0.24% (low -2.79%, high -2.54%)
- cex_dex_z_product: high-minus-low 7d mean spread 0.07% (low -1.98%, high -1.91%)
- cex_vol_growth_7d: high-minus-low 7d mean spread 0.19% (low -2.47%, high -2.28%)
- cex_volume_confirmed_mom_7d: high-minus-low 7d mean spread 1.78% (low -4.61%, high -2.83%)
- dex_share_change_7d: high-minus-low 7d mean spread 0.41% (low -3.45%, high -3.04%)
- dex_share_confirmed_mom_7d: high-minus-low 7d mean spread -1.41% (low -2.31%, high -3.71%)
- dex_share_x_dex_vol_z: high-minus-low 7d mean spread 0.90% (low -3.32%, high -2.42%)
- dex_share_z: high-minus-low 7d mean spread 0.18% (low -2.79%, high -2.61%)
- dex_vol_growth_7d: high-minus-low 7d mean spread 0.27% (low -2.80%, high -2.53%)
- dex_volume_confirmed_mom_7d: high-minus-low 7d mean spread 1.01% (low -3.48%, high -2.46%)
- joint_vol_z_mean: high-minus-low 7d mean spread -0.96% (low -2.43%, high -3.39%)
- joint_volume_confirmed_mom_7d: high-minus-low 7d mean spread 1.69% (low -4.11%, high -2.42%)
- mom_14d: high-minus-low 7d mean spread 0.75% (low -2.87%, high -2.12%)
- mom_30d: high-minus-low 7d mean spread -2.39% (low 2.00%, high -0.39%)
- mom_7d: high-minus-low 7d mean spread 0.04% (low -3.19%, high -3.15%)
- mom_7d_skip_1d: high-minus-low 7d mean spread -0.34% (low -2.74%, high -3.08%)
- momentum_vol_adj_7d: high-minus-low 7d mean spread 0.63% (low -3.70%, high -3.06%)
- realized_vol_14d: high-minus-low 7d mean spread -0.00% (low -2.63%, high -2.63%)
- reversal_1d: high-minus-low 7d mean spread -1.21% (low -3.00%, high -4.21%)
- total_vol_growth_7d: high-minus-low 7d mean spread 0.46% (low -2.76%, high -2.30%)
- total_vol_z: high-minus-low 7d mean spread -1.60% (low -2.79%, high -4.39%)
- volume_growth_divergence_7d: high-minus-low 7d mean spread 0.65% (low -2.49%, high -1.84%)

## Robustness Checks

- cex_volume_confirmed_mom_7d: overall spread 2.41%, excluding PEPE+ARB 2.09%, change -0.32%
- joint_volume_confirmed_mom_7d: overall spread 2.02%, excluding PEPE+ARB 1.85%, change -0.17%
- dex_volume_confirmed_mom_7d: overall spread 1.24%, excluding PEPE+ARB 1.04%, change -0.20%
- dex_share_x_dex_vol_z: overall spread 0.59%, excluding PEPE+ARB -0.43%, change -1.02%
- mom_14d: overall spread 0.56%, excluding PEPE+ARB 0.41%, change -0.14%
- volume_growth_divergence_7d: overall spread 0.52%, excluding PEPE+ARB 0.74%, change 0.22%

Strongest token-group spreads:
- layer2 / cex_volume_confirmed_mom_7d: 5.41%, n=326
- layer2 / joint_volume_confirmed_mom_7d: 5.37%, n=326
- layer2 / mom_30d: 5.29%, n=284
- layer2 / dex_volume_confirmed_mom_7d: 5.21%, n=326
- layer2 / dex_share_x_dex_vol_z: 3.75%, n=326

## Volume State Comparison

- both_high: 7d mean -0.86%, 7d win rate 43.85%, n=130
- both_low_or_normal: 7d mean -2.33%, 7d win rate 36.71%, n=1422
- dex_only: 7d mean -2.47%, 7d win rate 36.76%, n=136
- cex_only: 7d mean -7.67%, 7d win rate 22.55%, n=102

## Figure Paths

- Lead-lag heatmap: `/Users/luchuanyu/on-chain-market-structure-analysis/figures/a_review/lead_lag_heatmap.png`
- DEX share: `/Users/luchuanyu/on-chain-market-structure-analysis/figures/a_review/dex_share_timeseries.png`
- Factor buckets: `/Users/luchuanyu/on-chain-market-structure-analysis/figures/a_review/factor_forward_return_bins.png`
- Confirmation states: `/Users/luchuanyu/on-chain-market-structure-analysis/figures/a_review/confirmation_forward_return_bars.png`
