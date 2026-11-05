import sys, os, json, tempfile, datetime as dt, unittest
import numpy as np, pandas as pd
R = os.path.join(os.path.dirname(__file__), '..', 'skills')
for sub in ('funnel-kpi-report', 'weekly-marketing-update', 'newsletter-qa'):
    sys.path.insert(0, os.path.join(R, sub, 'scripts'))
import funnel_report as fr, tracker as tr, newsletter_lint as nl

class T(unittest.TestCase):
    def test_wilson_known_value(self):
        lo, hi = fr.wilson(50, 100)
        self.assertAlmostEqual(lo, 0.4038, places=3); self.assertAlmostEqual(hi, 0.5962, places=3)
        self.assertTrue(all(np.isnan(x) for x in fr.wilson(0, 0)))

    def test_funnel_rates_on_synthetic_data(self):
        rng = np.random.default_rng(0)
        df = pd.DataFrame({'src': ['a'] * 400 + ['b'] * 400 + ['c'] * 10, 'time': rng.integers(0, 1500, 810)})
        df['conv'] = np.r_[[1] * 360 + [0] * 40, [1] * 80 + [0] * 320, [1] * 10]
        cfg = {'converted_col': 'conv', 'dimensions': {'Source': 'src'}, 'chart_dimension': 'Source',
               'engagement': {'col': 'time', 'edges': [0, 600], 'label': 't'}, 'min_group_size': 100, 'caveats': []}
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'x.csv'); df.to_csv(p, index=False)
            res = fr.run(p, cfg, d)
            rows = {r['group']: r for r in res['dimensions']['Source']}
            self.assertAlmostEqual(rows['a']['rate'], 0.9); self.assertAlmostEqual(rows['b']['rate'], 0.2)
            self.assertIn('other (small groups)', rows)          # group c (n=10) is merged, not interpreted
            self.assertNotIn('c', rows)
            self.assertTrue(any('a' in s and '90%' in s for s in res['insights']))
            self.assertTrue(os.path.exists(os.path.join(d, 'report.md')))

    def test_tracker_overdue(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 't.csv')
            rows = [dict(id='1', action='x', owner='o', due='2026-10-01', status='open'),
                    dict(id='2', action='y', owner='o', due='2026-10-01', status='done'),
                    dict(id='3', action='z', owner='o', due='2026-12-01', status='open')]
            tr.save(p, rows)
            late = tr.overdue(tr.load(p), dt.date(2026, 10, 30))
            self.assertEqual([r['id'] for r in late], ['1'])

    def test_lint_flags_bad_and_passes_good(self):
        bad = 'Subject: ' + 'x' * 70 + '\nThis is a game-changer ' + 'word ' * 20 + '\n[a](https://a.com) [b](https://b.com)'
        r = nl.lint(bad); self.assertFalse(r['passed'])
        names = {c['name']: c['ok'] for c in r['checks']}
        self.assertFalse(names['No buzzwords']); self.assertFalse(names['Exactly one call-to-action link'])
        good = open(os.path.join(os.path.dirname(__file__), '..', 'outputs', 'newsletter_draft_v2.md')).read()
        self.assertTrue(nl.lint(good)['passed'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
