# Duplex

Competitive intelligence agent for [Beguile](https://beguile.com), the fragrance house.

It finds six competitors in each market (Nigeria, Ghana, UK, USA, Canada), studies their websites and social accounts, and writes a report per market plus a cross-market summary.

## Running it

Open this repository in Claude Code and type:

```
/competitive-intel
```

To run only some markets:

```
/competitive-intel nigeria uk
```

Reports land in `reports/<date>/`: one `<market>.md` and `<market>.json` per country, and `summary.md` across all of them. A later run compares against the previous one and notes what changed.

## How it is put together

| Path | What it is |
|---|---|
| `config/brand.md` | Beguile's profile and the definition of a competitor. Edit when the brand changes. |
| `config/markets.md` | The markets to cover. |
| `.claude/skills/competitive-intel/SKILL.md` | The coordinator: starts one researcher per market, checks their work, writes the summary. |
| `.claude/agents/market-researcher.md` | The researcher: finds six competitors in one market and profiles each. |
| `tools/fetch_page.js` | Renders pages that block plain fetches (uses the Playwright that ships with Claude Code cloud sessions). |
| `reports/` | Output of each run. |
