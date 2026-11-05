# AI-Augmented Marketing: reusable skill library

Four small reusable skills (SKILL.md format) for marketing operations, built by Chirag Arora and tested on a real public lead dataset. Written summary: `Chirag_Arora_AI_Augmented_Marketing_Skill_Library.pdf`.

| Skill | Folder | Entry point |
|---|---|---|
| Funnel KPI report | skills/funnel-kpi-report | scripts/funnel_report.py |
| Weekly marketing update | skills/weekly-marketing-update | scripts/render_update.py, scripts/tracker.py |
| Newsletter QA | skills/newsletter-qa | scripts/newsletter_lint.py |
| Training module builder | skills/training-module-builder | templates/module.md |

## Data
Data: data/Leads.csv (9,240 leads) is the public X Education lead-scoring dataset. It is not included here. Download Leads.csv from github.com/saptarshim7/Lead_Scoring_Case_Study and save it in a folder named data. Check the source’s terms before republishing the raw data.

## Reproduce
```
pip install -r requirements.txt
python skills/funnel-kpi-report/scripts/funnel_report.py --csv data/Leads.csv --config skills/funnel-kpi-report/config.example.json --out outputs/funnel_all
python skills/funnel-kpi-report/scripts/funnel_report.py --csv data/Leads.csv --config skills/funnel-kpi-report/config.digital.json --out outputs/funnel_digital
python skills/weekly-marketing-update/scripts/render_update.py outputs/funnel_digital/results.json outputs/tracker.csv "Week of 26 October 2026" 2026-10-30 outputs/weekly_update.md
python skills/newsletter-qa/scripts/newsletter_lint.py outputs/newsletter_draft_v2.md
python tests/test_skills.py
```

## Limits
- The scripts are small prototypes, not production tools. Every output was checked against the data by the author.
- The data is B2C (online courses) with no dates: associations only, no weekly trends.
- Tracker owners are placeholders; the training module has not been delivered; the newsletter link is a placeholder.

## Design notes: why these choices
- Why a Wilson interval? It stays valid for small groups and rates near 0% or 100%, unlike the simple normal approximation.
- Why analyse digital leads separately? Manually added referral leads convert at 92-99% and would hide how digital channels perform.
- Why 600 seconds? It is the boundary with the biggest conversion jump among the tiers (15% below, 67% above). It is a hypothesis to test, not a proven rule.
- Why is "last activity = SMS sent" not a cause? It can happen after conversion.
