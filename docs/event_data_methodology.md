# Event Data Methodology

## Scope

The event table covers the ten tokens in `config/tokens.csv` and the daily panel period from 2026-01-09 through 2026-07-05. The first version searches for three event types:

- token unlocks
- token airdrops or claim starts
- new spot listings on the ten CEXs already collected by the project

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

All ten tokens already have CEX observations from the start of the collected CEX panel on all ten included exchanges. Therefore, the current CEX dataset does not identify a new covered-exchange listing during the study window.

## Important limitations

This is a defensible initial event set, not a claim that every announcement on the internet was captured. Without a licensed historical event API, completeness is limited by public source discoverability. The table intentionally excludes general news, product launches, governance votes, continuous emissions, rumors, and events with no defensible date.

The event table does not label an event as bullish or bearish. Later research should measure price and volume before and after the event rather than selecting events based on their observed market reaction.
