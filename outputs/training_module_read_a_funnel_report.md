# Training module: Read a funnel report and decide who to call first

**Audience:** regional marketing teams (no data background needed)  |  **Duration:** 45 minutes  |  **Language:** English  |  **Format:** live workshop, hands-on

## Learning goals
1. Explain what a conversion rate, a confidence interval and a "small group" warning mean.
2. Pick the three most reliable findings in a funnel report and say what action each suggests.
3. Run the funnel-kpi-report skill on a new CSV and read its output.

## Prerequisites and materials
- A laptop with Python 3 and the packages in `requirements.txt` (or the shared notebook).
- The example report (`outputs/funnel_digital/report.md`) and `Leads.csv`.

## Agenda
| Min | Activity | Who | Output |
|---:|---|---|---|
| 0-5 | Why we measure conversion by group, not only overall | Facilitator | Shared vocabulary |
| 5-15 | Walk through the report: overall rate, source table, confidence intervals | Facilitator | Learners can read one row |
| 15-30 | Exercise: find the three most reliable findings and write one action each | Pairs | Three actions per pair |
| 30-40 | Run the skill on a second file (changed filter or new column mapping) | Pairs | A new report |
| 40-45 | Questions, feedback form | All | Feedback |

## Hands-on exercise
Task: in the example report, list three findings that are (a) based on at least 100 leads and (b) have a confidence interval that does not touch the overall rate. Write one action for each.
Expected: the 600-second engagement threshold, the weak chat follow-up and the bounced-email group.
Common mistakes: reading a high rate on a tiny group; treating "last activity = SMS sent" as a cause when it may happen after conversion.

## Check for understanding
1. A source converts at 60% with 8 leads. Should you shift budget to it? Why not?
2. Leads above 600 seconds on site convert at 67%. Does that prove that more time on site causes conversion?
3. What does the dashed line on the channel chart show?

## Answers
1. No. With 8 leads the confidence interval is very wide, so the rate is not reliable.
2. No. It is an association; interested leads may simply stay longer. Test with a follow-up experiment.
3. The overall conversion rate, used as the benchmark for each group.

## Follow-up and feedback
Within one week, run the skill on your own region's export and share one finding in the team channel. Feedback form: What was clear? What was confusing? What will you use?
Note: this module is a draft that has not yet been delivered to learners.
