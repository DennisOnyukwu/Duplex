---
name: competitive-intel
description: Run the competitive intelligence agent for Beguile. Finds six competitors in each market (Nigeria, Ghana, UK, USA, Canada), studies their websites and social accounts, and writes per-market reports plus a cross-market summary. Use when asked for a competitor report, a competitor refresh, or what competitors are doing in a market.
argument-hint: "[market ...]  e.g. nigeria uk — leave empty for all markets"
---

# Competitive intelligence run

You coordinate a competitor research run for the brand in `config/brand.md` across the markets in `config/markets.md`.

## Steps

1. Read `config/brand.md` and `config/markets.md`. If the user named markets, run only those; otherwise run every row.
2. Create the output directory `reports/<YYYY-MM-DD>/` using today's date.
3. Start one `market-researcher` agent per market, all in the same message so they run in parallel. Give each its market name, slug, currency and the output directory. If an earlier run exists in `reports/`, tell each researcher the path of its market's previous report so it can re-check the same brands and note what changed. If the `market-researcher` agent type is not available, use a general-purpose agent and tell it to follow `.claude/agents/market-researcher.md`.
4. When they finish, read every `<slug>.md` and `<slug>.json` they wrote. Spot-check a few figures against their sources (at least one price and one follower count per market); fix or flag anything that does not hold.
5. Write `reports/<date>/summary.md`:
   - **Headline findings** across all markets, most important first.
   - **Market by market:** a table with the six competitors per market and the single biggest takeaway for each market.
   - **Brands that show up in several markets** and how their offer differs by country.
   - **Price position:** the brand's hero perfume against competitors in each market, converted to price per ml in local currency.
   - **Social benchmark:** the brand's following against competitors.
   - **What changed since the last run**, when there is one.
   - **Recommended moves**, ranked, each tied to the evidence behind it.
   - **Gaps:** what could not be verified.
6. Tell the user where the reports are, give the headline findings in a few sentences, and say what could not be verified.

Report only what the researchers found with a source. Do not fill gaps from memory.
