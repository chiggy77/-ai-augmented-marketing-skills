---
name: funnel-kpi-report
description: Turn a lead or customer CSV into a funnel KPI report with conversion by channel and engagement tier, 95% confidence intervals, auto-written insights and charts. Use when asked to analyse lead conversion, channel performance or marketing funnel data.
---

# Funnel KPI report

## When to use
A CSV with one row per lead and a 0/1 conversion column, plus any of: source/channel, origin, last activity, an engagement number (time on site, visits).

## Steps
1. Ask which column is the conversion flag and which columns describe channel and engagement. Copy `config.example.json` and edit the column names.
2. Run: `python scripts/funnel_report.py --csv <file> --config <config.json> --out <folder>`
3. Read `report.md` and `results.json`. Check the caveats section and edit it so it describes the real dataset.
4. Report 3 to 5 findings in plain English. For each: the number, the group size, the confidence interval and one suggested action.

## Rules
- Never interpret groups under `min_group_size` leads; they are merged into "other".
- State that results are associations, not causes.
- If a column can be recorded after conversion (for example "last activity"), say so.
- If manual or offline leads convert far above digital ones, run a second report with the `filter` option so digital channels are judged on their own.
- Do not invent a trend: if the data has no dates, say a trend cannot be shown.
