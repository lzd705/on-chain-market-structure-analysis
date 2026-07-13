# Variable CEX Coverage Design

## Goal

Expand the CEX sample from 10 to 30 tokens without requiring every token to
trade on all ten configured exchanges.

## Rules

- Attempt all ten configured exchanges for every token.
- An exchange is stable for a token when it has at least 120 daily observations
  in the fetched 180-day window.
- Use all stable exchanges for that token. If ten are stable, use all ten.
- A token needs at least three stable exchanges and Binance must be one of them,
  because Binance supplies the current reference close price.
- The stable exchange set is fixed for the token across the sample window.
- A token-date is included only when every exchange in that fixed set has data.
  This prevents an API failure from appearing as a volume decline.
- Preserve `exchange_count` and `included_exchanges` in the daily aggregate.

## Outputs

- `data/processed/cex_exchange_volume_daily.csv`: every successfully fetched
  exchange-level observation.
- `data/processed/cex_exchange_coverage.csv`: observation days, date bounds,
  and stable-set status for every token-exchange pair.
- `data/processed/cex_volume_daily.csv`: token-date totals based on each
  token's fixed stable exchange set.

## Scope

This change collects CEX data only. DEX chain configuration and DEX fetching
for the new tokens remain a separate next step.
