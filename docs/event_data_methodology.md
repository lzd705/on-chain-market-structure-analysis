# Event Data Methodology

## Scope

The event table covers the 30 tokens in `config/tokens.csv` and the daily panel period from 2026-01-09 through 2026-07-05. It searches for three event types:

- token unlocks
- token airdrops or claim starts
- new spot listings on the configured CEXs already collected by the project

The candidate file is `data/curated/event_candidates.csv`. The standardized output is `data/processed/event_table.csv`.

## Collection method

The project does not have a paid event API. Candidate events are therefore curated from public sources and passed through a reproducible validation script. Official tokenomics, project governance posts, and official supply pages are preferred. A secondary schedule is used when an official source confirms the vesting rule but does not publish an exact daily calendar.

Unknown sizes are blank. They are not inferred from a later token price or copied from a current-value widget. `confidence=medium` means the vesting rule is supported but the exact historical day is taken from a secondary schedule. `confidence=high` means the release was observed onchain using known non-circulating supply wallets.

## Search results by token

| Token | Included events | Collection decision |
|---|---:|---|
| ARB | 6 | Official governance material confirms monthly team and investor vesting; dates are cross-checked with DefiLlama. |
| OP | 5 | Optimism publishes an estimated supply tracker; the dated schedule is retained with medium confidence. |
| ENA | 6 | Official tokenomics confirms monthly contributor and investor vesting; dates are cross-checked with Tokenomics.com. |
| LINK | 2 | Quarterly transfers from official non-circulating wallets were observed in April and June. |
| UNI | 0 | No qualifying unlock, airdrop, or new listing was verified in the panel period. |
| AAVE | 0 | No qualifying unlock, airdrop, or new listing was verified in the panel period. |
| LDO | 0 | The original contributor vesting ended before the panel; treasury usage is not treated as a scheduled unlock. |
| CRV | 0 | Ongoing protocol emissions are continuous and are not converted into arbitrary event days. |
| PENDLE | 0 | Official documentation says team and investor tokens are fully vested; weekly incentives and terminal inflation are continuous emissions. |
| PEPE | 0 | No qualifying unlock, airdrop, or new listing was verified in the panel period. |
| COMP | 0 | Governance distribution is continuous and is not converted into an arbitrary event day. |
| MORPHO | 6 | Official documentation confirms linear vesting; monthly dates are cross-checked with the team-verified Tokenomics schedule. |
| SUSHI | 0 | No qualifying discrete unlock, airdrop, or new listing was verified in the panel period. |
| 1INCH | 0 | The tracked allocation unlocks were complete before the panel period. |
| CAKE | 0 | Ongoing emissions are continuous and are not converted into arbitrary event days. |
| GMX | 0 | The tracked allocation unlocks were complete before the panel period. |
| SNX | 0 | The tracked vesting schedule ended before the panel period. |
| ONDO | 1 | The team-verified schedule identifies the annual allocation unlock on 2026-01-18. |
| EIGEN | 6 | The official announcement confirms monthly investor and early-contributor vesting; dates are cross-checked with Tokenomics. |
| ETHFI | 6 | Official allocations confirm multi-year vesting; monthly dates are cross-checked with Tokenomics. |
| GRT | 6 | Official distribution material confirms long-term vesting; monthly dates are cross-checked with Tokenomics. |
| ENS | 5 | The January date is outside the panel; February through June monthly contributor unlocks are retained. |
| WLD | 0 | Official material describes daily linear unlocks, so third-party monthly aggregation dates are not treated as discrete events. |
| STRK | 6 | Official Starknet documentation specifies an unlock on the 15th of each month. The official date is used instead of a conflicting third-party monthly aggregation date. |
| ZK | 6 | Official documentation confirms monthly investor and team vesting; dates are cross-checked with Tokenomics. |
| JUP | 1 | The 2026 Jupuary distribution was postponed; the separate Mercurial-stakeholder release tied to the net-zero proposal is retained. |
| RAY | 0 | Scheduled allocation unlocks ended before the panel; ongoing mining rewards are continuous emissions. |
| JTO | 5 | The January date is outside the panel; February through June investor and contributor unlocks are retained. |
| BONK | 0 | The tracked allocation unlocks were complete before the panel period. |
| SHIB | 0 | No qualifying unlock, airdrop, or new listing was verified in the panel period. |

The expanded collection adds 48 source-backed events for the 20 new tokens. Together with the original 19 records, the candidate and processed tables contain 67 events. Of these, 62 have a complete `[-7, +14]` event window inside the price and volume panel and are analysis-eligible.

The current CEX panel does not by itself prove that a token was newly listed. A `cex_listing` event is added only when a dated exchange announcement can be verified; ordinary first observations or missing exchange rows are not treated as listing events.

## Important limitations

This is a defensible initial event set, not a claim that every announcement on the internet was captured. Without a licensed historical event API, completeness is limited by public source discoverability. The table intentionally excludes general news, product launches, governance votes, continuous emissions, rumors, and events with no defensible date.

The event table does not label an event as bullish or bearish. Later research should measure price and volume before and after the event rather than selecting events based on their observed market reaction.
