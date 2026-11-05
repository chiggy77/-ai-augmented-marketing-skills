---
name: weekly-marketing-update
description: Produce a one-page weekly marketing update (headline, signal to act on, decisions, actions, risks) from the funnel results.json and a CSV action tracker. Use when asked for a weekly report, status update or action tracking for a marketing team.
---

# Weekly marketing update

## Steps
1. Make sure `results.json` exists (run `funnel-kpi-report` first).
2. Keep actions in a CSV tracker: `python scripts/tracker.py tracker.csv add "action" owner YYYY-MM-DD`. Mark finished rows `done` in the file.
3. Render: `python scripts/render_update.py results.json tracker.csv "Week of ..." YYYY-MM-DD update.md`
4. Read the update. Check that every number matches `results.json` and every action has an owner and a due date.
5. Check overdue items with `python scripts/tracker.py tracker.csv overdue`.

## Rules
- Lead with one headline and one decision, not a list of metrics.
- Keep it to one page.
- Name risks plainly, including data limits.
