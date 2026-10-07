# Meta Ads audit pipeline

Scripts for the four-stage Meta Ads audit: export, clean and structure, categorise and analyse, report.
The deliverable is a workbook with the tabs Read Me, Data, Lookup, Monthly, Weekly, Zingers, Tracking,
Findings, plus a Live Ad Sets action tab.

Account data is never committed. `raw/` and `out/` are git-ignored.

## Run order

```bash
# 1. Export: Windsor.ai get_data pulls (facebook connector, ad level, daily) saved as JSON
python scripts/windsor_to_csv.py raw/raw.csv raw/q1.json raw/q2.json raw/q3.json raw/q4.json

# 2. Clean and structure (raw export -> fact, lookup, monthly, weekly, dq_report)
python scripts/clean_and_structure.py raw/raw.csv out/stage2/

# 3. Categorise. Names first; Meta metadata where names cannot be parsed
python scripts/derive_from_metadata.py raw/meta.json raw/status.json out/ad_meta.csv raw/carousel.json
python scripts/categorize_data.py out/stage2/fact.csv out/fact_categorized.csv --meta out/ad_meta.csv [--prefer-meta]
python scripts/clean_and_structure.py out/fact_categorized.csv out/final/      # rebuild Lookup + rollups with categories
# keep the stage-2 data-quality report as the reported one (it ran on the raw export)
#   cp out/stage2/dq_report.txt out/final/dq_report.txt

# 4. Zingers and analysis, per scope (live ads, other ads, whole account)
python scripts/detect_zingers.py out/final/fact.csv out/final/lookup.csv out/zingers_live.csv --scope out/live_ad_ids.txt --scope-name "Live ads"
python scripts/detect_zingers.py out/final/fact.csv out/final/lookup.csv out/zingers_all.csv --scope-name "All ads (12 months)"
python scripts/analyse.py out/final/fact.csv out/ad_meta.csv out/an_all.json --zingers out/zingers_all.csv
python scripts/live_actions.py out/final/fact.csv out/ad_meta.csv out/live_ad_ids.txt out/zingers_live.csv out/live_adsets.csv

# 5. Workbook (.xlsx, every tab) and Google Sheets payloads (reader-facing tabs)
python scripts/build_workbook.py out/final out/findings.md --out out/audit.xlsx \
    --zingers out/zingers_live.csv,out/zingers_nonlive.csv,out/zingers_all.csv \
    --live out/live_adsets.csv --meta-json out/account.json
python scripts/gsheet_payload.py out/final out/findings.md out/account.json out/live_adsets.csv \
    out/zingers_live.csv out/zingers_nonlive.csv out/zingers_all.csv out/gsheet
```

Each script prints a summary and exits non-zero on a data failure (exit 2 = completed with
findings to report, such as an Uncategorized share above 15%). Read the summary.

## Changes from the operating-prompt versions of the scripts

Each change fixes something that would otherwise put a wrong number in an audit.

| Script | Change | Why |
|---|---|---|
| `clean_and_structure.py` | Weekly rollup keyed by ISO week (Monday) | The original keyed "weekly" by the raw date, so it was a daily rollup |
| | Category columns (and Market) carried through when present; run a second time after categorisation | Stage 2 runs before stage 3, so Lookup and the rollups had empty categories |
| | CTR and CVR kept to 4 decimals | At 2 decimals a 1.3% CTR rounds to 0.01 |
| | Nulls counted per metric; date gaps listed; labels trimmed and internal spaces collapsed; Days active counts days with delivery | Required by the cleaning checklist in Part 2 |
| `categorize_data.py` | Token boundaries use `(?<![A-Za-z0-9])…(?![A-Za-z0-9])` instead of `\b` | `\b` treats `_` as a word character, so `PRSP_LAL` never matched `PRSP` |
| | Sample is the top 50 values by spend, not the first 50 seen | Part 3 asks for highest-spend first |
| | `V` and `S` added to the extended Video and Static sets (bounded, so they match only standalone) | Listed in the Part 3 synonym table, missing from the script |
| | `--meta` fallback tier and `--prefer-meta`; tier recorded per row; Uncategorized threshold checked by spend | For accounts whose names cannot be parsed, using Meta's own creative and targeting metadata |
| `detect_zingers.py` | Last-7-days window is exactly 7 days; active ad set = spend in that window | The original window was 8 days and counted zero-spend rows |
| | Z5 counts all active ad sets below 50, not only those spending more than one CPA | Matches the Part 5 definition |
| | Z7 precomputes rows per ad | The original scanned the whole fact table once per ad |
| | Z10 tested within each market | Audiences in different countries cannot overlap |
| | Entities labelled with campaign name and ID; `--scope` for live-only runs, with account averages still account-wide | Ad set names such as "New Sales Ad Set" repeat across hundreds of campaigns |
| `build_workbook.py` | IDs written as text; dates as dates; currency, ratio and percent formats; autofilter; Read Me leads with the summary and actions; Findings rendered as real tables; Zingers summary before detail | The original coerced 18-digit Meta IDs to numbers (Excel keeps 15 digits) and pasted the findings markdown into one column |

## Added scripts

- `windsor_to_csv.py`: converts Windsor.ai JSON pulls to a raw CSV with Meta's column names.
- `derive_from_metadata.py`: Funnel Stage, Audience, Ad Format and Market from targeting and creative metadata, plus delivery status (live or not).
- `analyse.py`: the Part 4 tables per scope.
- `live_actions.py`: one row per live ad set with a rule-based verdict.
- `gsheet_payload.py`: values and formatting requests for the Google Sheets connector.
