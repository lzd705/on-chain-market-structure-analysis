可验证的问题：

> 链下 CEX 成交量和链上 DEX 成交量是否存在领先、滞后、共振或背离关系？
> 这些关系是否能转化成动量类多因子策略中的有效因子？
> 解锁、空投、分发、上所等事件是否会改变这些成交量因子的含义？

# 实训任务文档：CEX 与 DEX 成交量关系及动量因子研究

## 1. 研究背景

在传统量化交易中，成交量和成交额是常用的动量、关注度、流动性和反转类因子。例如：

```text
价格上涨 + 成交量放大
```

通常会被解释为趋势增强。

但在加密市场里，成交量不是单一来源。一个 Token 的交易可能同时发生在：

```text
CEX：Binance、OKX、Bybit、Gate 等中心化交易所
DEX：Uniswap、PancakeSwap、Curve、Aerodrome 等链上交易所
```

CEX 和 DEX 的成交量含义可能不同：

```text
CEX 成交量：更多反映交易所内部的买卖活跃度、做市深度、散户和合约交易热度
DEX 成交量：更多反映链上真实 Swap、钱包行为、套利、MEV、LP 流动性和链上资金流
```

所以，本次实训的核心问题是：

> 传统链下成交量因子，能不能和链上 DEX 成交量结合，形成更适合加密资产的动量类因子？

数据源方面，CEX 侧可以使用交易所 API 或 CCXT 这类统一接口；例如 Binance 官方现货 API 提供 order book、recent trades、aggregate trades 和 kline/candlestick 数据，K 线返回字段中包含成交量、成交额和 taker buy volume 等字段。([币安开发者中心](https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints "Market Data endpoints | Binance Open Platform")) CCXT 也提供覆盖多家交易所的统一 API 接口。([CCXT](https://docs.ccxt.com/ "CCXT — Unified Crypto Trading API for 100+ Exchanges")) DEX 侧可以使用 DefiLlama 的 DEX volume endpoints，或者用 Dune / 自建索引从链上 Swap Logs 中计算。DefiLlama 文档列出了 DEX Volumes、Open Interest、Token Unlocks 等相关接口；Dune API 支持执行 SQL 查询并程序化获取链上查询结果。([DeFi Llama](https://defillama.com/docs/api "api-docs.defillama.com")) ([Dune Docs](https://docs.dune.com/api-reference/overview/introduction "Overview - Dune Docs"))

---

## 2. 总体目标

本项目要求围绕 **CEX 成交量、DEX 成交量、链上事件和动量因子** 做一个可复现的小型研究。

最终目标不是直接证明“某个策略一定有效”，而是完成以下任务：

```text
1. 建立 CEX / DEX 成交量数据集
2. **比较不同来源成交量的特征差异**
3. **分析 CEX 与 DEX 成交量之间的领先滞后关系**
4. 研究链上事件对成交量和价格趋势的影响
5. 构建一组候选多因子
6. 用简单回测或因子检验评估这些因子的有效性
7. 输出可复现的分析过程的完整pipeline代码、图表、报告和汇报 PPT
```

---

## 3. 核心研究问题

学员需要围绕下面 6 个问题展开。

### 问题 1：CEX 成交量和 DEX 成交量是否同步？

需要回答：

```text
当某个 Token 在 CEX 上成交量放大时，DEX 成交量是否也同步放大？
DEX 成交量是否会领先 CEX 成交量？
CEX 成交量是否会领先 DEX 成交量？
不同类型 Token 是否表现不同？
```

可做分析：

```text
CEX_volume_t 与 DEX_volume_t 的相关系数
CEX_volume_t 与 DEX_volume_{t-1, t-2, ...} 的滞后相关
DEX_volume_t 与 CEX_volume_{t-1, t-2, ...} 的滞后相关
Lead-Lag heatmap
Granger causality，可选
```

---

### 问题 2：不同交易所的成交量有什么差异？

需要比较：

```text
Binance / OKX / Bybit 等 CEX 成交量差异
Uniswap / PancakeSwap / Curve / Aerodrome 等 DEX 成交量差异
不同链上的 DEX 成交量差异
同一个 Token 在多个池子里的成交量差异
```

重点不是只算总量，而是看结构：

```text
成交量是否集中在一个 CEX？
成交量是否集中在一个 DEX 池子？
DEX 成交量是否由套利或 MEV 驱动？
某个交易所成交量是否先于其他交易所放大？
CEX 和 DEX 的成交量波动是否具有不同噪声特征？
```

---

### 问题 3：DEX 成交量因子和传统 CEX 成交量因子有什么不同？

传统成交量因子通常包括：

```text
成交量放大
成交额放大
换手率上升
价格上涨伴随放量
价格下跌伴随放量
异常成交量
```

链上 DEX 成交量可以进一步拆成：

```text
买入方向 Swap
卖出方向 Swap
大额 Swap
唯一交易钱包数
新钱包买入数
Top trader 占比
DEX / CEX 成交量比例
LP 流动性变化
CEX 充值 / 提现
```

需要研究的问题：

```text
DEX 成交量放大更像是趋势信号，还是出货信号？
CEX 成交量放大是否更容易受到合约交易、刷量、做市影响？
DEX 买入量放大是否比总成交量更有解释力？
DEX 成交量集中在少数地址时，动量因子是否失效？
```

---

### 问题 4：解锁、空投、分发事件会如何影响成交量？

事件类型包括：

```text
Token Unlock
Airdrop Claim
CEX Listing
TGE
Vesting Release
Team / Investor Unlock
Bridge Launch
Major Incentive Campaign
```

需要研究：

```text
事件前后 CEX 成交量是否放大？
事件前后 DEX 成交量是否放大？
空投后是否出现大量 claim → transfer → swap → CEX deposit？
解锁后是否出现大户转账或 DEX 卖出？
这些事件带来的成交量是趋势确认，还是潜在卖压？
```

核心提醒：

> 事件带来的成交量不一定是正向动量。
> 空投、解锁、分发导致的成交量放大，可能代表新增关注，也可能代表集中卖出。

---

### 问题 5：CEX / DEX 成交量关系能否用于动量类多因子策略？

需要构建候选因子，例如：

```text
价格动量因子
CEX 成交量动量因子
DEX 成交量动量因子
DEX / CEX 成交量占比因子
CEX-DEX 成交量背离因子
DEX 买入净流因子
链上钱包活跃度因子
事件调整因子
流动性惩罚因子
```

然后检验它们对未来收益的解释力：

```text
未来 1 天收益
未来 3 天收益
未来 7 天收益
未来 14 天收益
未来 30 天收益
```

---

### 问题 6：哪些结论只能作为研究假设，不能直接用于交易？

学员必须区分：

```text
链上事实
统计关系
合理推断
策略假设
无法证明的猜测
```

例如：

```text
事实：某地址向 Binance 地址充值 100 万枚 Token
推断：这可能形成潜在卖压
不能直接断言：该地址已经在 Binance 卖出
```

这部分是报告评分重点。

---

# 4. 研究对象范围

## 4.1 Token 样本池

建议选择 30–80 个 Token，分成几类：

```text
1. 同时有 CEX 和 DEX 交易的主流 Token
2. 新上线 CEX 的 Token
3. 有较大 DEX 交易量的链上原生 Token
4. 有明显空投或解锁事件的 Token
5. 高波动、叙事驱动型 Token
```

可以排除：

```text
稳定币
流动性极差的 Token
只有 CEX 没有 DEX 的 Token
只有 DEX 没有可靠价格数据的 Token
严重缺失数据的 Token
```

## 4.2 时间粒度

建议先做三个粒度：

```text
1h
4h
1d
```

MVP 阶段可以只做日频，进阶阶段再做小时级。

## 4.3 时间窗口

建议至少覆盖：

```text
过去 6–12 个月
```

如果研究事件，比如空投、解锁、上所，可以使用事件窗口：

```text
T-30 天 到 T+30 天
T-7 天 到 T+7 天
T-24 小时 到 T+72 小时
```

---

# 5. 数据要求

## 5.1 CEX 数据

需要采集：

```text
timestamp
exchange
symbol
base_asset
quote_asset
open
high
low
close
base_volume
quote_volume
number_of_trades
taker_buy_base_volume
taker_buy_quote_volume
```

最小要求：

```text
CEX 日频 OHLCV
CEX 成交额 quote_volume
```

进阶要求：

```text
小时级 OHLCV
taker buy volume
订单簿深度
不同交易所成交量拆分
现货和永续合约分别统计
```

---

## 5.2 DEX 数据

需要采集：

```text
timestamp
chain
dex
pool_address
token_address
token_symbol
token_in
token_out
amount_in
amount_out
amount_usd
price
side
tx_hash
trader
router
```

最小要求：

```text
DEX 日频成交量
DEX 日频成交额
主池价格
```

进阶要求：

```text
每笔 Swap
买入 / 卖出方向
唯一交易钱包数
Top trader 占比
大额 Swap
MEV / arbitrage 初步识别
LP 添加和移除
池子 TVL 和滑点
```

---

## 5.3 事件数据

需要建立事件表：

```text
token
event_type
event_time
event_name
amount
amount_usd
percent_of_supply
source
related_address
related_tx_hash
notes
```

事件类型包括：

```text
unlock
airdrop
claim_start
cex_listing
major_lp_add
major_lp_remove
team_transfer
treasury_transfer
large_cex_deposit
large_cex_withdrawal
```

---

# 6. 标准数据表设计

要求学员最终至少产出以下表。

## 6.1 `token_master.csv`

```text
token_id
symbol
name
chain
contract_address
decimals
coingecko_id
cex_symbols
main_dex_pools
launch_date
first_cex_listing_date
notes
```

## 6.2 `cex_ohlcv.parquet`

```text
timestamp
token_id
exchange
symbol
market_type
open
high
low
close
base_volume
quote_volume
number_of_trades
taker_buy_base_volume
taker_buy_quote_volume
```

## 6.3 `dex_swaps.parquet`

```text
timestamp
block_number
chain
token_id
dex
pool_address
tx_hash
trader
side
amount_token
amount_usd
price_usd
router
is_large_trade
```

## 6.4 `dex_daily_metrics.parquet`

```text
date
token_id
dex_volume_usd
dex_buy_volume_usd
dex_sell_volume_usd
dex_net_buy_volume_usd
unique_traders
unique_buyers
unique_sellers
large_trade_count
top5_trader_volume_share
pool_tvl_usd
price_impact_10k
```

## 6.5 `event_table.csv`

```text
token_id
event_type
event_time
event_window_start
event_window_end
event_size_token
event_size_usd
event_size_supply_pct
source
confidence
```

## 6.6 `factor_table.parquet`

```text
timestamp
token_id
factor_name
factor_value
lookback_window
data_source
```

---

# 7. 候选因子设计

下面这些因子可以作为学员的研究方向。

## 7.1 基础动量因子

### 价格动量

```text
MOM_7D = log(P_t / P_{t-7})
MOM_14D = log(P_t / P_{t-14})
MOM_30D = log(P_t / P_{t-30})
```

可以设置反转过滤：

```text
MOM_7D_SKIP_1D = log(P_{t-1} / P_{t-8})
```

避免使用最近 1 天的过度噪声。

---

## 7.2 CEX 成交量因子

### CEX 异常成交量

```text
CEX_VOL_Z = zscore(log(1 + CEX_volume_usd), lookback=30d)
```

### CEX 成交量增长

```text
CEX_VOL_GROWTH_7D = log(CEX_volume_7d / CEX_volume_prev_7d)
```

### CEX 成交量确认动量

```text
CEX_VOLUME_CONFIRMED_MOM = MOM_7D * CEX_VOL_Z
```

解释：

```text
价格上涨，同时 CEX 成交量放大，可能说明趋势在中心化市场被确认。
```

---

## 7.3 DEX 成交量因子

### DEX 异常成交量

```text
DEX_VOL_Z = zscore(log(1 + DEX_volume_usd), lookback=30d)
```

### DEX 买入净流

```text
DEX_NET_BUY_RATIO = (DEX_buy_volume - DEX_sell_volume) / DEX_total_volume
```

### DEX 钱包活跃度

```text
DEX_TRADER_Z = zscore(log(1 + unique_traders), lookback=30d)
```

### DEX 大户交易集中度

```text
TOP5_TRADER_SHARE = top5_trader_volume / total_dex_volume
```

解释：

```text
DEX 成交量放大如果伴随大量独立钱包参与，可能更像真实扩散。
DEX 成交量放大如果集中在少数钱包，可能更像操纵、套利或大户出货。
```

---

## 7.4 CEX / DEX 关系因子

### DEX 成交量占比

```text
DEX_SHARE = DEX_volume_usd / (DEX_volume_usd + CEX_spot_volume_usd)
```

解释：

```text
DEX_SHARE 上升，说明链上交易活跃度相对于中心化交易所提高。
```

### DEX-CEX 成交量背离

```text
VOL_DIVERGENCE = zscore(DEX_volume_growth) - zscore(CEX_volume_growth)
```

解释：

```text
VOL_DIVERGENCE > 0：
链上成交量增长快于 CEX

VOL_DIVERGENCE < 0：
CEX 成交量增长快于链上
```

研究问题：

```text
DEX 先放量，后续 CEX 是否跟随？
CEX 先放量，后续链上是否跟随？
DEX 放量但 CEX 不跟，是否容易反转？
```

### 跨市场共振因子

```text
CROSS_MARKET_VOLUME_CONFIRMATION =
rank(CEX_VOL_Z) + rank(DEX_VOL_Z)
```

解释：

```text
如果 CEX 和 DEX 同时放量，可能比单一市场放量更有趋势确认意义。
```

---

## 7.5 流动性调整因子

### DEX 流动性惩罚

```text
LIQUIDITY_RISK = price_impact_10k 或 slippage_50k
```

### 流动性调整动量

```text
LIQ_ADJ_MOM = MOM_7D - liquidity_risk_penalty
```

解释：

```text
价格上涨但池子很浅，动量可能不可靠。
价格上涨且 DEX 深度同步增加，趋势质量更高。
```

---

## 7.6 事件调整因子

### 解锁压力因子

```text
UNLOCK_PRESSURE = unlock_amount / circulating_supply
```

### 空投卖压因子

```text
AIRDROP_SELL_PRESSURE =
claimed_amount_sold_or_transferred / claimed_amount
```

### 事件后成交量异常

```text
POST_EVENT_VOLUME_Z =
zscore(volume_after_event, baseline=event前30天)
```

研究问题：

```text
空投后的成交量放大，是新需求还是 claim 后卖出？
解锁前后成交量放大，是趋势扩散还是卖压释放？
```

---

# 8. 重点研究假设

让学员按“假设 → 数据 → 方法 → 图表 → 结论 → 限制”的格式完成。

## H1：DEX 成交量可能领先 CEX 成交量

适用场景：

```text
新 Token
链上原生项目
刚空投的 Token
DEX 先交易，CEX 后上所
```

验证方法：

```text
计算 DEX_volume_growth 对未来 CEX_volume_growth 的滞后相关
做 DEX lead CEX 的 cross-correlation heatmap
观察事件前后 DEX 是否先放量
```

---

## H2：CEX 成交量可能领先 DEX 成交量

适用场景：

```text
大市值 Token
CEX 主导定价的 Token
合约交易活跃的 Token
CEX 上所后带动链上转账和 DEX 交易
```

验证方法：

```text
计算 CEX_volume_growth 对未来 DEX_volume_growth 的滞后相关
比较 CEX 主导 Token 与 DEX 主导 Token 的差异
```

---

## H3：CEX 和 DEX 同时放量时，动量质量更高

验证方法：

```text
构建 CROSS_MARKET_VOLUME_CONFIRMATION 因子
把样本分成：
1. CEX 放量 + DEX 放量
2. 只有 CEX 放量
3. 只有 DEX 放量
4. 都不放量

比较未来 1d / 3d / 7d 收益
```

重点：

```text
不是只看平均收益，还要看回撤、胜率和分位数组合表现。
```

---

## H4：空投和解锁带来的 DEX 放量可能不是正向动量

验证方法：

```text
建立 airdrop / unlock 事件样本
计算事件后 DEX_volume_z
计算事件后 CEX_volume_z
计算事件后 1d / 3d / 7d / 14d 收益
观察 claim 地址是否卖出或转入 CEX
```

可能结论：

```text
空投后 DEX 放量可能代表新增关注
也可能代表领取者集中卖出
需要结合链上卖出方向、CEX 入金和持仓变化判断
```

---

## H5：DEX 放量但流动性没有增加，可能是脆弱动量

验证方法：

```text
比较 DEX_volume_growth 和 pool_tvl_growth
计算 price_impact_10k / price_impact_50k
观察上涨阶段是否伴随 LP 添加
观察崩盘前是否伴随 LP 移除
```

可能解释：

```text
成交量很大，但池子很浅，价格容易被少量资金推高或砸下。
```

---

# 9. 学员任务拆分

任务目标可以分成 4 个小组，每组目标明确。

## A 组：CEX 数据组

任务：

```text
1. 拉取 Binance / OKX / Bybit 等 CEX 的 OHLCV
2. 统一 symbol、quote asset、时间戳
3. 计算 CEX 成交量、成交额、成交量增长、异常成交量
4. 区分不同交易所的成交量贡献
```

交付：

```text
cex_ohlcv.parquet
cex_volume_metrics.parquet
CEX 成交量分析图表
```

核心图表：

```text
不同 CEX 成交额占比
CEX 成交量时间序列
CEX volume z-score
CEX volume vs price
```

---

## B 组：DEX 数据组

任务：

```text
1. 找到每个 Token 的主要 DEX 池子
2. 拉取 Swap 数据或 DEX 汇总成交量
3. 区分买入、卖出、大额交易
4. 计算 DEX 成交量、成交额、钱包数、Top trader 占比
5. 计算池子 TVL 和滑点
```

交付：

```text
dex_swaps.parquet
dex_daily_metrics.parquet
pool_liquidity_metrics.parquet
```

核心图表：

```text
DEX 成交量时间序列
DEX buy / sell volume
unique traders
Top trader volume share
pool TVL vs price
```

---

## C 组：事件研究组

任务：

```text
1. 收集 unlock、airdrop、CEX listing 等事件
2. 建立事件窗口
3. 分析事件前后 CEX / DEX 成交量变化
4. 分析事件前后价格趋势和回撤
5. 对空投事件研究 claim → sell / transfer / CEX deposit 路径
```

交付：

```text
event_table.csv
event_study_results.parquet
event_case_report.md
```

核心图表：

```text
事件前后异常成交量
事件前后累计收益
事件前后 DEX_SHARE
事件前后 CEX deposit 变化
```

---

## D 组：因子与回测组

任务：

```text
1. 基于 A/B/C 组数据构建候选因子
2. 计算未来收益标签
3. 做 IC / Rank IC / 分组收益检验
4. 构建简单多因子组合
5. 做基础回测和稳健性分析
```

交付：

```text
factor_table.parquet
factor_performance.csv
backtest_report.ipynb
```

核心图表：

```text
因子 IC 时间序列
分位数组合收益
多因子组合净值曲线
因子相关性热力图
```

---

# 10. 最小可行版本 MVP

考虑学员还不太熟，第一阶段不要铺太大。可以给他们一个 MVP。

## MVP 目标

```text
选择 10 个 Token
覆盖 3 个月数据
使用日频数据
只做 CEX spot volume、DEX volume、price return
先不做复杂钱包聚类和 Trace
```

## MVP 必须完成

```text
1. 每个 Token 的 CEX 日成交额
2. 每个 Token 的 DEX 日成交额
3. 每个 Token 的日收益率
4. DEX_SHARE
5. CEX_VOL_Z
6. DEX_VOL_Z
7. CEX-DEX volume divergence
8. 未来 1d / 3d / 7d 收益检验
```

## MVP 最低交付

```text
一个 notebook
三张核心图
一个 5 页小报告
一个 5 分钟汇报
```

三张核心图：

```text
1. 某个 Token 的 price、CEX volume、DEX volume 三轴图
2. DEX_VOLUME_Z 与未来收益分组图
3. CEX/DEX 成交量 lead-lag heatmap
```

---

# 11. 进阶版本

MVP 做完后再扩展。

## 进阶 1：小时级数据

```text
1h / 4h 粒度
研究短周期领先滞后
研究事件发生后 24–72 小时的成交量扩散
```

## 进阶 2：买卖方向

```text
DEX buy volume
DEX sell volume
DEX net buy
CEX taker buy volume
CEX taker sell approximation
```

## 进阶 3：流动性和滑点

```text
pool TVL
reserve
price impact
slippage
LP add/remove
liquidity-adjusted momentum
```

## 进阶 4：链上钱包行为

```text
unique traders
new buyers
top holder selling
large CEX deposits
whale netflow
airdrop claim-to-sell ratio
```

## 进阶 5：多因子模型

```text
price momentum
CEX volume momentum
DEX volume momentum
DEX/CEX divergence
wallet activity
liquidity risk
event pressure
```

---

# 12. 因子检验标准

不要只看一条净值曲线。每个因子至少要给出以下结果。

## 12.1 单因子有效性

```text
IC
Rank IC
ICIR
分位数组合收益
Top - Bottom spread
未来 1d / 3d / 7d 收益
样本覆盖率
```

## 12.2 稳健性

```text
不同时间窗口是否稳定？
不同 Token 类型是否稳定？
不同交易所是否稳定？
牛市 / 熊市 / 震荡市是否稳定？
去掉极端样本后是否还有效？
交易成本和滑点后是否还有效？
```

## 12.3 因子解释

每个因子必须能回答：

```text
这个因子捕捉的是什么市场行为？
它为什么可能有效？
它在哪些情况下可能失效？
它是否可能只是事件、上所或极端行情导致的偶然结果？
```

---

# 13. 报告结构要求

最终报告建议 15–25 页，结构如下。

## 1. Executive Summary

用一页说清楚：

```text
研究对象
数据范围
核心发现
最有效的因子
最明显的风险
结论置信度
```

## 2. 数据说明

包括：

```text
Token 样本
时间范围
CEX 数据来源
DEX 数据来源
事件数据来源
清洗规则
缺失数据处理
```

## 3. CEX 与 DEX 成交量结构

回答：

```text
哪些 Token 主要由 CEX 定价？
哪些 Token 链上交易更活跃？
CEX 和 DEX 成交量是否同步？
不同交易所是否存在领先关系？
```

## 4. Lead-Lag 分析

必须包含：

```text
CEX volume lead DEX volume 的结果
DEX volume lead CEX volume 的结果
volume lead price return 的结果
price return lead volume 的结果
```

## 5. 事件研究

至少选 3–5 个事件：

```text
airdrop
unlock
cex listing
large treasury transfer
large CEX deposit
```

分析事件前后：

```text
price
CEX volume
DEX volume
DEX_SHARE
wallet activity
future return
```

## 6. 因子设计

列出候选因子：

```text
定义
公式
数据来源
经济含义
可能失效场景
```

## 7. 因子表现

展示：

```text
IC 表
分组收益图
多因子组合表现
因子相关性
稳健性检验
```

## 8. 结论与限制

必须写清楚：

```text
哪些结论比较可靠
哪些结论只是样本内现象
哪些数据存在偏差
哪些地方可能有幸存者偏差
哪些地方需要更高频或更完整数据
```

---

# 14. 汇报 PPT 结构

要求每组做 10 分钟汇报，建议 10 页。

```text
第 1 页：研究问题和样本范围
第 2 页：数据来源和清洗方法
第 3 页：CEX vs DEX 成交量结构
第 4 页：Lead-Lag 核心发现
第 5 页：事件研究案例
第 6 页：候选因子设计
第 7 页：单因子表现
第 8 页：多因子组合表现
第 9 页：失败案例和限制
第 10 页：结论与下一步
```

---

# 15. 评分标准

总分 100 分。

| 模块               | 分值 | 评分重点                                           |
| ------------------ | ---: | -------------------------------------------------- |
| 数据采集与清洗     |   20 | 时间戳、交易所、Token 映射、成交额口径是否正确     |
| CEX / DEX 对比分析 |   15 | 是否解释不同市场成交量的差异                       |
| Lead-Lag 分析      |   15 | 是否检验领先滞后关系，而不是只画图                 |
| 事件研究           |   15 | 是否分析 unlock / airdrop / listing 对成交量的影响 |
| 因子设计           |   15 | 因子是否有清晰定义和合理解释                       |
| 因子检验           |   10 | 是否做 IC、分组收益、稳健性分析                    |
| 报告质量           |    5 | 结论是否清晰、图表是否可读                         |
| 可复现性           |    5 | 代码、数据、参数是否能复现                         |

---

# 16. 常见错误提醒

需要提前告诉学员避免这些问题。

## 1. 把 CEX 成交量和 DEX 成交量直接相加

错误原因：

```text
两者市场结构不同，参与者不同，噪声不同。
```

正确做法：

```text
分别计算，再构造 DEX_SHARE、volume divergence、cross-market confirmation。
```

## 2. 忽略 Token 映射问题

同一个 Symbol 可能对应不同 Token：

```text
ETH on Ethereum
WETH on Arbitrum
WETH on Base
同名 Meme Token
跨链包装资产
```

必须建立 `token_master.csv`。

## 3. 忽略时间戳对齐

CEX 通常按毫秒时间戳。
DEX 需要用 block timestamp。
所有数据必须统一到 UTC。

## 4. 把空投后放量直接当成正向信号

空投后放量可能是：

```text
新增买盘
领取后卖出
套利
CEX 充值
流动性迁移
```

必须结合链上方向和地址行为判断。

## 5. 使用未来信息

例如：

```text
用事件之后才知道的 Token 列表回测过去
用未来成交量计算当前因子
用未来是否上所筛选样本
```

这些都会造成 look-ahead bias。

## 6. 忽略交易成本和滑点

小市值 Token 的回测很容易虚高。
必须至少估算：

```text
CEX taker fee
DEX gas
DEX slippage
价格冲击
可交易容量
```

---

# 17. 给学员的最终任务描述

可以直接复制这段发给他们：

```text
本次实训要求你们研究 CEX 与 DEX 成交量之间的关系，并评估这些关系是否能用于加密资产动量类多因子策略。

你们需要选择一组同时存在 CEX 和 DEX 交易的 Token，采集其 CEX 成交量、DEX 成交量、价格、链上事件和必要的流动性数据。

你们要回答以下问题：

1. CEX 成交量和 DEX 成交量是否同步？
2. 是否存在 DEX 领先 CEX，或 CEX 领先 DEX 的现象？
3. 不同交易所、不同 DEX、不同 Token 类型之间是否有差异？
4. DEX 成交量因子和传统 CEX 成交量因子有什么不同？
5. Unlock、Airdrop、CEX Listing 等事件是否会改变成交量因子的含义？
6. CEX / DEX 成交量关系能否构造成动量类因子？
7. 这些因子在未来 1d、3d、7d 收益上是否有解释力？
8. 哪些结论只是样本内现象，哪些结论有较强经济解释？

最终提交内容包括：

1. 数据采集和清洗脚本
2. CEX / DEX 成交量指标表
3. 事件研究结果表
4. 因子定义和因子值
5. 因子检验 notebook
6. 15–25 页研究报告
7. 10 分钟汇报 PPT

注意：本任务是研究训练，不构成投资建议。你们的结论必须基于数据和证据，必须区分事实、推断和假设。
```

---

# 18. 我建议你给他们的第一版题目

为了避免他们发散，可以直接指定成这个题目：

## 题目

**《CEX 与 DEX 成交量关系研究：链上成交量能否增强加密资产动量因子？》**

## 第一阶段目标

```text
样本：10–20 个 Token
时间：最近 6 个月
频率：日频
CEX：至少 2 个交易所
DEX：至少覆盖每个 Token 的主 DEX 池子
事件：至少 5 个 unlock / airdrop / listing 事件
```

## 第一阶段必须回答

```text
1. DEX volume 和 CEX volume 谁更领先？
2. DEX volume 放大后，未来收益是上涨还是反转？
3. CEX 和 DEX 同时放量时，动量是否更强？
4. 空投 / 解锁后的 DEX 放量是否具有不同含义？
5. DEX/CEX volume divergence 是否是一个可用因子？
```

这个范围清晰，难度适中，比较适合刚开始做链上交易分析的实习生。

---

之前上传的文件在当前环境里已经过期；后续还需要我基于那份《智能合约入门》或其他文件继续改写培训材料时，需要重新上传。
