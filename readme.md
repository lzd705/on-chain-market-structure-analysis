# On-chain Market Structure Analysis

## Project Goal

This project analyzes the market structure of an ERC20 token using verifiable on-chain data. The focus is to understand whether the token's price movement is supported by healthy liquidity, diversified holders, and real trading activity, or whether the market structure shows signs of fragility, concentration, or abnormal behavior.

The project should focus on 9 core tasks:

1. Confirm token metadata and contract risk flags
2. Identify main DEX trading pools
3. Collect on-chain events
4. Analyze holder structure
5. Analyze liquidity structure
6. Estimate AMM depth and slippage
7. Analyze trade flow structure
8. Estimate Kyle Lambda market impact
9. Conduct key transaction trace analysis

The final output should be a structured market structure report based on on-chain facts, quantitative metrics, and clearly stated limitations.

## Local Research Dashboard

The interactive CEX / DEX comparison dashboard lives in `dashboard/`. It reads the latest local research panel, compares metrics and candidate factors, exports filtered data, and persists research notes and checklist status locally.

```bash
./scripts/run_dashboard.sh
```

Open `http://127.0.0.1:8765` after startup.

Use the versioned synthetic sample for a redistribution-safe public demo:

```bash
./scripts/run_dashboard.sh --data data/mock/research/factor_panel.csv
```

Project source code is MIT licensed. See `DATA_USAGE.md` before redistributing
observed or derived market data.

---

## Task 1: Confirm Token Metadata and Contract Risk Flags

The first task is to confirm the basic information of the target ERC20 token.

Collect and verify:

* token contract address
* token name
* token symbol
* decimals
* total supply
* contract creation block and timestamp
* deployer address
* owner or admin address if available
* whether the contract source code is verified
* whether the contract is proxy or upgradeable
* whether the token has mint, burn, pause, blacklist, whitelist, tax, fee, or transfer restriction mechanisms

This task is important because all later calculations depend on correct token metadata. In particular, all token amounts must be normalized using the correct decimals.

Expected outputs:

* token metadata table
* token risk flag table
* short written summary of contract-level risks

---

## Task 2: Identify Main DEX Trading Pools

The second task is to find the main decentralized exchange pools where the token is traded.

Identify pools from:

* Uniswap V2
* Uniswap V3
* SushiSwap or other major DEXs if relevant

For each pool, collect:

* pool address
* DEX name
* DEX version
* token0 address
* token1 address
* quote token, such as WETH, USDC, or USDT
* Uniswap V3 fee tier if applicable
* current liquidity or reserves
* pool creation block
* estimated trading volume share if available

The goal is to determine where price discovery mainly happens and whether the token price is controlled by one shallow pool or supported by multiple active pools.

Expected outputs:

* pool summary table
* main pool identification
* short explanation of why the selected pool is the main trading venue

---

## Task 3: Collect On-chain Events

The third task is to collect structured on-chain event data for the target token and its main trading pools.

Collect the following event types:

### ERC20 Transfer Events

Collect all Transfer events for the target token within the analysis window.

Required fields:

```text
block_number
timestamp
tx_hash
log_index
token_address
from_address
to_address
amount_raw
amount_normalized
```

### DEX Swap Events

Collect Swap events from the main DEX pools.

Required fields:

```text
block_number
timestamp
tx_hash
pool_address
dex
version
token0
token1
amount0
amount1
amount0_normalized
amount1_normalized
target_token_amount
quote_token_amount
price
swap_direction
```

### LP Events

Collect liquidity provider events, including mint, burn, increase liquidity, decrease liquidity, and collect events where applicable.

Required fields:

```text
block_number
timestamp
tx_hash
pool_address
dex
version
event_type
lp_address
amount_token
amount_quote
liquidity_delta
```

This task creates the raw data foundation for all later analysis.

Expected outputs:

* transfers dataset
* swaps dataset
* LP events dataset
* basic data quality summary

---

## Task 4: Holder Structure Analysis

The fourth task is to reconstruct holder balances from ERC20 Transfer events and analyze token ownership concentration.

Core logic:

* each Transfer decreases the sender balance
* each Transfer increases the receiver balance
* process transfers chronologically
* normalize token balances using decimals
* calculate holder balances at selected timestamps or at the end of the analysis window

Calculate:

* total holder count
* Top 1 holder share
* Top 3 holder share
* Top 10 holder share
* Top 50 holder share
* HHI concentration index
* Gini coefficient
* top holder address table

Calculate two versions:

1. Raw holder concentration
2. Adjusted holder concentration excluding DEX pools, CEX wallets, burn addresses, routers, and known infrastructure addresses

The adjusted version is more meaningful for understanding actual ownership concentration.

Expected outputs:

* holder snapshot table
* top holders table
* holder concentration metrics
* holder distribution chart
* short interpretation of concentration risk

---

## Task 5: Liquidity Structure Analysis

The fifth task is to analyze whether the token's price and market cap are supported by real DEX liquidity.

Analyze:

* main pool TVL
* target token reserve
* quote token reserve
* main pool share of total liquidity
* liquidity change over time
* net liquidity added or removed
* major liquidity provider behavior
* liquidity before and after major price movement windows

Key questions:

* Did liquidity increase together with price?
* Did price rise while liquidity stayed shallow?
* Did liquidity providers remove liquidity before large price drops?
* Is the token dependent on one main pool?
* Is market cap much larger than available exit liquidity?

Expected outputs:

* liquidity summary table
* liquidity time series
* TVL chart
* net liquidity change chart
* short interpretation of liquidity risk

---

## Task 6: AMM Depth and Slippage Analysis

The sixth task is to convert AMM liquidity into order-book-like market depth.

For the main trading pool, estimate:

* capital required to push price up by 1%
* capital required to push price up by 5%
* capital required to push price up by 10%
* token amount required to push price down by 1%
* token amount required to push price down by 5%
* token amount required to push price down by 10%

For Uniswap V2 pools, use constant product AMM logic.

For Uniswap V3 pools, use tick-level concentrated liquidity if feasible. If full V3 modeling is too complex, use a simplified method and clearly state the assumption.

The goal is to measure real exit liquidity and price fragility.

Expected outputs:

* liquidity depth table
* slippage curve
* short explanation of how much capital is needed to move the price
* limitation statement if simplified assumptions are used

---

## Task 7: Trade Flow Structure Analysis

The seventh task is to analyze trading activity and identify whether trading is broad-based or dominated by a few addresses.

Calculate:

* minute-level or hour-level price
* buy volume
* sell volume
* net buy/sell imbalance
* number of unique buyers
* number of unique sellers
* top 5 trader volume share
* top 10 trader volume share
* largest buy transactions
* largest sell transactions
* repeated trading addresses

Key questions:

* Is volume driven by many real traders or a small number of wallets?
* Did buy pressure increase before price spikes?
* Did sell pressure increase before price drops?
* Are there repeated trading patterns that may suggest wash trading or bot activity?
* Are there large trades that explain major price changes?

Expected outputs:

* trade flow time series
* top traders table
* large trades table
* price and volume chart
* buy/sell imbalance chart
* short interpretation of trading behavior

---

## Task 8: Kyle Lambda Market Impact Estimation

The eighth task is to estimate simplified Kyle Lambda as a market impact indicator.

Kyle Lambda measures how much price changes per unit of trading volume. A higher value suggests weaker liquidity and higher price impact.

Use a simplified version:

```text
lambda_t = abs(log(P_t / P_{t-1})) / volume_t
```

Also implement a regression version if feasible:

```text
return_t = alpha + lambda * signed_volume_t + error
```

Where:

```text
signed_volume_t = buy_volume_t - sell_volume_t
```

Analyze:

* Kyle Lambda by minute or hour
* rolling average Kyle Lambda
* Kyle Lambda before and after major events
* whether market impact increased before major price drops

Expected outputs:

* Kyle Lambda table
* Kyle Lambda time series chart
* short interpretation of market impact and liquidity fragility

---

## Task 9: Key Transaction Trace Analysis

The ninth task is to select several important transactions and analyze them in detail.

Select 5 to 7 key transactions, such as:

* largest buy
* largest sell
* largest LP add
* largest LP removal
* largest transfer to CEX
* first transaction before a major price drop
* suspicious MEV, sandwich, or bot-related transaction

For each transaction, analyze:

* transaction hash
* block number
* timestamp
* sender address
* receiver or called contract
* function called
* logs emitted
* token transfers
* internal calls if available
* pool reserve or liquidity impact
* price impact
* whether the transaction is an on-chain fact, reasonable inference, or uncertain

Use the following structure for each transaction:

```text
Transaction:
Type:
On-chain facts:
Asset flow:
Market impact:
Reasonable inference:
Limitations:
```

The goal is to turn quantitative metrics into a clear market structure narrative.

Expected outputs:

* key transaction table
* detailed transaction notes
* short summary of the most important transactions

---

## Final Report

After completing the 9 tasks, produce a final report with the following sections:

```text
1. Executive Summary
2. Token Metadata and Contract Risk Flags
3. Main DEX Trading Pools
4. Data Collection Methodology
5. Holder Structure Analysis
6. Liquidity Structure Analysis
7. AMM Depth and Slippage
8. Trade Flow Structure
9. Kyle Lambda Market Impact
10. Key Transaction Trace Analysis
11. Market Structure Risk Assessment
12. Limitations
13. Conclusion
```

The report should clearly separate:

* on-chain facts
* quantitative metrics
* reasonable inferences
* limitations

Do not overclaim conclusions that cannot be directly proven from on-chain data.

---

## Minimum Expected Deliverables

The project should produce:

```text
token_metadata.csv
token_risk_flags.csv
pools.csv
transfers.parquet
swaps.parquet
lp_events.parquet
holder_snapshot.csv
holder_concentration_metrics.csv
liquidity_summary.csv
liquidity_depth.csv
trade_flow_by_time.csv
top_traders.csv
kyle_lambda.csv
key_transaction_trace.csv
final_report.md
```

Optional figures:

```text
holder_distribution.png
tvl_over_time.png
slippage_curve.png
price_volume_timeseries.png
buy_sell_imbalance.png
kyle_lambda_over_time.png
```

---

## Development Instruction

Implement the project step by step.

Recommended order:

```text
1. Token metadata
2. Pool identification
3. Event collection
4. Holder analysis
5. Liquidity analysis
6. AMM depth and slippage
7. Trade flow analysis
8. Kyle Lambda
9. Key transaction trace
10. Final report
```

Prioritize correctness and reproducibility over complexity.

Use Python as the main language. Code should be modular, readable, and easy to validate.
