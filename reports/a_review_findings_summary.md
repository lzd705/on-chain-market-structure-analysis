# Research Findings Summary

This summary is generated from the selected research CSV outputs. If the inputs are mock data, treat the numbers as pipeline validation only.

## Data Coverage

- Token count: 10
- Date range: 2026-01-09 to 2026-07-05
- Token-day rows: 1,780
- Median DEX share across token medians: 3.37%

## Data Checks

- Tokens passing minimum history check: 10
- Tokens flagged: 0
- Total missing dates across tokens: 0
- Total duplicate token-date rows: 0

## DEX Direction And Pool Structure

- DEX buy/sell metrics are OHLCV close-location proxies, not swap-level signed flow.
- Median net buy ratio proxy: -17.77%
- Median top-pool volume share: 67.15%
- Median pool Herfindahl: 0.51
- Median active pool count: 5.00
- Median DEX volume / pool TVL: 13.78%

## CEX vs DEX Same-day Correlation

- PEPE: z-score corr 0.82, log-volume corr 0.87
- ARB: z-score corr 0.82, log-volume corr 0.81
- PENDLE: z-score corr 0.77, log-volume corr 0.81

## Lead-lag Highlights

- PEPE lag 0: corr 0.82, n=169
- ARB lag 0: corr 0.82, n=169
- PENDLE lag 0: corr 0.77, n=169
- LINK lag 0: corr 0.69, n=169
- CRV lag 0: corr 0.68, n=169

## DEX_VOL_Z Buckets

- Lowest bucket 7d mean return: -1.41%
- Highest bucket 7d mean return: -1.94%

## Candidate Factor Buckets

- cex_dex_ratio_z: high-minus-low 7d mean spread -1.86% (low -1.12%, high -2.98%)
- cex_dex_z_product: high-minus-low 7d mean spread -0.44% (low -1.51%, high -1.96%)
- cex_vol_growth_7d: high-minus-low 7d mean spread 0.78% (low -2.75%, high -1.98%)
- cex_volume_confirmed_mom_7d: high-minus-low 7d mean spread 1.88% (low -4.33%, high -2.45%)
- dex_buy_pressure_proxy_z: high-minus-low 7d mean spread -1.83% (low -1.43%, high -3.26%)
- dex_net_buy_confirmed_mom_7d: high-minus-low 7d mean spread 0.95% (low -3.54%, high -2.59%)
- dex_net_buy_ratio_proxy: high-minus-low 7d mean spread -0.70% (low -2.64%, high -3.34%)
- dex_pool_concentration_change_7d: high-minus-low 7d mean spread 0.97% (low -3.22%, high -2.25%)
- dex_pool_diversification: high-minus-low 7d mean spread 0.86% (low -2.18%, high -1.32%)
- dex_pool_herfindahl: high-minus-low 7d mean spread -0.86% (low -1.32%, high -2.18%)
- dex_pool_tvl_growth_7d: high-minus-low 7d mean spread 0.89% (low -2.42%, high -1.52%)
- dex_share_change_7d: high-minus-low 7d mean spread 0.69% (low -3.45%, high -2.75%)
- dex_share_confirmed_mom_7d: high-minus-low 7d mean spread -0.21% (low -3.27%, high -3.48%)
- dex_share_x_dex_vol_z: high-minus-low 7d mean spread 0.49% (low -2.48%, high -1.99%)
- dex_share_z: high-minus-low 7d mean spread 1.88% (low -3.29%, high -1.41%)
- dex_vol_growth_7d: high-minus-low 7d mean spread 1.88% (low -3.14%, high -1.27%)
- dex_volume_confirmed_mom_7d: high-minus-low 7d mean spread 1.03% (low -3.49%, high -2.46%)
- dex_volume_to_tvl: high-minus-low 7d mean spread -2.65% (low -1.41%, high -4.06%)
- dex_volume_to_tvl_z: high-minus-low 7d mean spread 0.51% (low -2.69%, high -2.19%)
- joint_vol_z_mean: high-minus-low 7d mean spread -0.69% (low -2.38%, high -3.06%)
- joint_volume_confirmed_mom_7d: high-minus-low 7d mean spread 1.57% (low -3.81%, high -2.24%)
- mom_14d: high-minus-low 7d mean spread 0.75% (low -2.86%, high -2.11%)
- mom_30d: high-minus-low 7d mean spread -2.28% (low 1.83%, high -0.45%)
- mom_7d: high-minus-low 7d mean spread 0.10% (low -3.18%, high -3.08%)
- mom_7d_skip_1d: high-minus-low 7d mean spread -0.23% (low -2.79%, high -3.02%)
- momentum_vol_adj_7d: high-minus-low 7d mean spread 0.71% (low -3.71%, high -2.99%)
- pool_diversified_dex_mom_7d: high-minus-low 7d mean spread 0.18% (low -3.05%, high -2.87%)
- realized_vol_14d: high-minus-low 7d mean spread -0.12% (low -2.54%, high -2.66%)
- reversal_1d: high-minus-low 7d mean spread -1.15% (low -3.08%, high -4.24%)
- top_pool_volume_share: high-minus-low 7d mean spread -0.83% (low -1.26%, high -2.09%)
- total_vol_growth_7d: high-minus-low 7d mean spread 0.90% (low -2.96%, high -2.06%)
- total_vol_z: high-minus-low 7d mean spread -2.11% (low -1.96%, high -4.06%)
- volume_growth_divergence_7d: high-minus-low 7d mean spread 1.59% (low -3.22%, high -1.63%)

## Robustness Checks

- cex_volume_confirmed_mom_7d: overall spread 2.10%, excluding PEPE+ARB 1.87%, change -0.23%
- joint_volume_confirmed_mom_7d: overall spread 1.95%, excluding PEPE+ARB 1.63%, change -0.32%
- volume_growth_divergence_7d: overall spread 1.23%, excluding PEPE+ARB 1.24%, change 0.01%
- dex_volume_confirmed_mom_7d: overall spread 1.20%, excluding PEPE+ARB 0.83%, change -0.37%
- dex_net_buy_confirmed_mom_7d: overall spread 0.95%, excluding PEPE+ARB 0.46%, change -0.49%
- pool_diversified_dex_mom_7d: overall spread 0.55%, excluding PEPE+ARB 0.40%, change -0.15%

Strongest token-group spreads:
- layer2 / mom_30d: 5.31%, n=282
- layer2 / joint_volume_confirmed_mom_7d: 5.02%, n=324
- layer2 / cex_volume_confirmed_mom_7d: 4.77%, n=324
- layer2 / pool_diversified_dex_mom_7d: 4.52%, n=324
- layer2 / dex_volume_confirmed_mom_7d: 4.24%, n=324

## Volume State Comparison

- dex_only: 7d mean 1.08%, 7d win rate 42.37%, n=118
- both_high: 7d mean -1.69%, 7d win rate 42.22%, n=135
- both_low_or_normal: 7d mean -2.66%, 7d win rate 36.22%, n=1441
- cex_only: 7d mean -7.30%, 7d win rate 19.77%, n=86

## Figure Paths

- Lead-lag heatmap: `/Users/luchuanyu/on-chain-market-structure-analysis/figures/a_review/lead_lag_heatmap.png`
- DEX share: `/Users/luchuanyu/on-chain-market-structure-analysis/figures/a_review/dex_share_timeseries.png`
- Factor buckets: `/Users/luchuanyu/on-chain-market-structure-analysis/figures/a_review/factor_forward_return_bins.png`
- Confirmation states: `/Users/luchuanyu/on-chain-market-structure-analysis/figures/a_review/confirmation_forward_return_bars.png`
