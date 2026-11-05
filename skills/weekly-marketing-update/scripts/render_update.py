"""Render a one-page weekly marketing update from funnel results.json and the action tracker.
Usage: python render_update.py results.json tracker.csv "Week label" YYYY-MM-DD out.md
"""
import json, sys, datetime as dt
sys.path.insert(0, __import__('os').path.dirname(__file__))
from tracker import load, overdue

res = json.load(open(sys.argv[1])); rows = load(sys.argv[2]); label = sys.argv[3]; today = dt.date.fromisoformat(sys.argv[4])
src = max((r for r in res['dimensions'].get('Lead source', []) if r['n'] >= res['min_group_size'] and r['group'] not in ('unknown',)), key=lambda r: r['rate'])
low = min((r for r in res['dimensions'].get('Lead source', []) if r['n'] >= 500 and r['group'] not in ('unknown',)), key=lambda r: r['rate'])
th = res.get('engagement_threshold')
open_rows = [r for r in rows if r['status'] != 'done']; late = overdue(rows, today)
L = [f'# Marketing update: {label}', '',
     '## Headline', f"{res['rows']:,} leads in the dataset, overall conversion {res['overall_rate']:.1%}. "
     f"Best source: {src['group']} ({src['rate']:.0%}, n={src['n']:,}). Weakest high-volume source (500+ leads): {low['group']} ({low['rate']:.0%}, n={low['n']:,}).", '']
if th:
    L += ['## Signal to act on', f"Leads with more than {th['edge']} seconds on site convert at {th['rate_above']:.0%} vs {th['rate_below']:.0%} below that line. Route them to sales first.", '']
L += ['## Decisions needed'] + [f"- {i}" for i in res['insights'][:2]] + ['', '## Actions']
L += [f"- [{r['status']}] {r['action']} (owner: {r['owner']}, due {r['due']})" for r in open_rows] or ['- none']
L += ['', '## Risks', f"- {len(late)} action(s) overdue." if late else '- No overdue actions.', '- Results are associations from one public dataset without dates; confirm on live data before changing budget.']
open(sys.argv[5], 'w').write('\n'.join(L) + '\n')
