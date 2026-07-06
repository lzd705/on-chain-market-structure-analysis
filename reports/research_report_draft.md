# CEX 与 DEX 成交量关系及动量因子研究初稿

## 1. 研究问题

本研究关注同一个 Token 在 CEX 与 DEX 两类交易场所中的成交量关系：

- CEX 成交量和 DEX 成交量是否同步放大？
- DEX 成交量是否领先或滞后 CEX 成交量？
- CEX 与 DEX 同时放量，是否比单边放量更能解释未来收益？
- DEX 成交量占比变化是否反映交易场所结构变化？

## 2. 数据来源与样本范围

第一版使用日频数据。CEX 侧预计覆盖 Binance、OKX、Bybit 的现货 OHLCV 或成交额数据；DEX 侧预计使用 GeckoTerminal、DefiLlama、Dune 或手动导出的日频成交量数据。

第一版分析所需字段：

```text
date
token_symbol
price_usd
cex_volume_usd
dex_volume_usd
```

如果 A 侧主表尚未生成，研究脚本会尝试从 CEX 与 DEX 日频中间表合并出临时研究面板。

正式写结论前需要先运行：

```bash
python3 research/check_data_inputs.py --input-dir data/processed
python3 research/run_research.py
python3 research/summarize_results.py
```

## 3. 第一版因子定义

```text
CEX_VOL_Z = rolling_z_score(log1p(cex_volume_usd), 30d)
DEX_VOL_Z = rolling_z_score(log1p(dex_volume_usd), 30d)
DEX_SHARE = dex_volume_usd / (cex_volume_usd + dex_volume_usd)
VOL_DIVERGENCE = DEX_VOL_Z - CEX_VOL_Z
CEX_DEX_CONFIRMATION = 1 if CEX_VOL_Z > 1 and DEX_VOL_Z > 1 else 0
MOM_7D = log(price_t / price_t-7)
MOM_14D = log(price_t / price_t-14)
MOM_30D = log(price_t / price_t-30)
MOM_7D_SKIP_1D = log(price_t-1 / price_t-8)
CEX_VOL_GROWTH_7D = log(CEX_volume_recent_7d / CEX_volume_previous_7d)
DEX_VOL_GROWTH_7D = log(DEX_volume_recent_7d / DEX_volume_previous_7d)
TOTAL_VOL_Z = rolling_z_score(log1p(total_volume_usd), 30d)
TOTAL_VOL_GROWTH_7D = log(total_volume_recent_7d / total_volume_previous_7d)
DEX_SHARE_Z = rolling_z_score(DEX_SHARE, 30d)
DEX_SHARE_CHANGE_7D = DEX_SHARE_t - DEX_SHARE_t-7
VOLUME_GROWTH_DIVERGENCE_7D = DEX_VOL_GROWTH_7D - CEX_VOL_GROWTH_7D
JOINT_VOL_Z_MEAN = (CEX_VOL_Z + DEX_VOL_Z) / 2
CEX_DEX_Z_PRODUCT = CEX_VOL_Z * DEX_VOL_Z
CEX_VOLUME_CONFIRMED_MOM_7D = MOM_7D * CEX_VOL_Z
DEX_VOLUME_CONFIRMED_MOM_7D = MOM_7D * DEX_VOL_Z
JOINT_VOLUME_CONFIRMED_MOM_7D = MOM_7D * JOINT_VOL_Z_MEAN
```

成交量状态分为：

```text
both_high
cex_only
dex_only
both_low_or_normal
```

## 4. 分析设计

第一步做数据覆盖检查，包括每个 Token 的起止日期、样本天数、CEX 成交量中位数、DEX 成交量中位数和 DEX_SHARE 中位数。

第二步比较 CEX 与 DEX 成交量同步性，包括同日 log volume correlation 和 z-score correlation。

第三步做 lead-lag correlation。核心统计量为：

```text
corr(CEX_VOL_Z_t, DEX_VOL_Z_t+lag)
```

其中 lag > 0 表示 CEX 今天和未来 DEX 的相关性，lag < 0 表示 DEX 今天和未来 CEX 的相关性。

第四步检验 DEX_VOL_Z 与未来 1d、3d、7d 收益的关系，并比较 CEX + DEX 同时放量、CEX 单边放量、DEX 单边放量和普通状态下的未来收益。

第五步对候选因子做分桶检验，包括价格动量、跳过最近一天动量、成交量增长、DEX_SHARE 变化、CEX/DEX 背离、共振强度和成交量确认动量。第一版只看未来 1d、3d、7d、14d 平均收益、中位数和胜率，不直接解释为可交易策略。

## 5. 初步图表清单

- `figures/time_series/*.png`: price / CEX volume / DEX volume 时间序列图
- `figures/lead_lag_heatmap.png`: lead-lag correlation heatmap
- `figures/dex_share_timeseries.png`: DEX_SHARE 时间序列图
- `figures/factor_forward_return_bins.png`: DEX_VOL_Z 分组后的未来收益图
- `figures/confirmation_forward_return_bars.png`: CEX/DEX 放量状态对应的未来收益图

## 6. 初步发现

待运行 `python3 research/run_research.py` 和 `python3 research/summarize_results.py` 后补充。第一版结论必须区分统计相关和交易信号，不能把相关性直接写成因果。

建议填充格式：

```text
Finding 1:
Evidence:
Interpretation:
Limitation:
```

当前推荐写法：

```text
Finding:
在样本期内，部分 Token 的 CEX_VOL_Z 与 DEX_VOL_Z 存在同向变化。

Evidence:
引用 cex_dex_correlation.csv 和 lead_lag_correlation.csv 中的 token-level 结果。

Interpretation:
这说明 CEX 与 DEX 成交活跃度可能受到共同市场关注度影响，也可能存在跨场所套利传导。

Limitation:
日频数据不能证明日内领先关系，也不能区分真实方向性买入和套利/做市成交。
```

## 7. 局限性

- DEX 数据第一版可能只覆盖主池，不代表全市场 DEX 成交量。
- CEX 成交量可能受到做市、刷量、交易所覆盖差异和衍生品热度影响。
- 日频数据无法观察日内 lead-lag。
- 样本期较短，初步结论只能作为研究假设。
- 最后一日数据可能不完整，研究脚本默认剔除最大日期。

## 8. 下一步

- 扩大 Token 样本。
- 加入事件变量，例如 unlock、airdrop、CEX listing、TGE。
- 拆分 DEX 买卖方向、唯一钱包数、大额 Swap 和 LP 流动性变化。
- 对 lead-lag 结果做稳健性检验。
- 对因子做更严格的横截面分组或简单回测。

## 9. 附录：输出文件

```text
data/research/data_quality_report.csv
data/research/factor_panel.csv
data/research/coverage_summary.csv
data/research/cex_dex_correlation.csv
data/research/lead_lag_correlation.csv
data/research/factor_forward_returns.csv
data/research/candidate_factor_forward_returns.csv
data/research/factor_robustness_checks.csv
data/research/confirmation_forward_returns.csv
reports/research_findings_summary.md
```
