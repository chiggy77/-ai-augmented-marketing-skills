"""Funnel KPI report: conversion by channel and engagement tier, with confidence intervals.

Usage:  python funnel_report.py --csv leads.csv --config config.json --out outputs/
Needs: pandas, numpy, matplotlib.
"""
import argparse, json, math, os
import numpy as np, pandas as pd


def wilson(k, n, z=1.96):
    """95% Wilson score interval for a proportion."""
    if n == 0:
        return (float('nan'), float('nan'))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def clean_dim(s, min_n):
    s = s.fillna('Unknown').astype(str).str.strip().str.lower()
    counts = s.value_counts()
    rare = counts[counts < min_n].index
    s = s.where(~s.isin(rare), 'other (small groups)')
    return s


def group_table(df, dim, conv, min_n):
    g = df.groupby(dim)[conv].agg(['size', 'sum']).rename(columns={'size': 'n', 'sum': 'conv'})
    g['rate'] = g.conv / g.n
    ci = [wilson(k, n) for k, n in zip(g.conv, g.n)]
    g['lo'] = [c[0] for c in ci]; g['hi'] = [c[1] for c in ci]
    return g.sort_values('n', ascending=False)


def tiers(series, edges):
    labels = []
    for i, e in enumerate(edges):
        if i == 0:
            labels.append(f'0 (no time on site)' if e == 0 else f'<= {e}')
        else:
            labels.append(f'{edges[i-1]+1}-{e}')
    labels.append(f'> {edges[-1]}')
    bins = [-1] + list(edges) + [1e12]
    return pd.cut(series, bins, labels=labels)


def run(csv, cfg, out):
    df = pd.read_csv(csv)
    for col, keep in cfg.get('filter', {}).items():
        df = df[df[col].isin(keep)]
    conv = cfg['converted_col']
    df[conv] = df[conv].astype(int)
    min_n = cfg.get('min_group_size', 100)
    overall = df[conv].mean()
    res = {'rows': int(len(df)), 'conversions': int(df[conv].sum()), 'overall_rate': round(float(overall), 4),
           'overall_ci': [round(x, 4) for x in wilson(int(df[conv].sum()), len(df))], 'min_group_size': min_n, 'dimensions': {}}
    insights = []
    for label, col in cfg['dimensions'].items():
        d = df.copy(); d['_g'] = clean_dim(d[col], min_n)
        t = group_table(d, '_g', conv, min_n)
        res['dimensions'][label] = [dict(group=i, n=int(r.n), conv=int(r.conv), rate=round(float(r.rate), 6),
                                         ci_lo=round(float(r.lo), 6), ci_hi=round(float(r.hi), 6),
                                         lift=round(float(r.rate / overall), 2)) for i, r in t.iterrows()]
        for i, r in t.iterrows():
            if r.n >= min_n and i not in ('unknown', 'other (small groups)'):
                if r.lo > overall:
                    insights.append((abs(r.rate - overall), f"**{label}: {i}** converts at {r.rate:.0%} (95% CI {r.lo:.0%}-{r.hi:.0%}, n={int(r.n)}) vs {overall:.0%} overall, which is {r.rate/overall:.1f}x the average."))
                elif r.hi < overall:
                    insights.append((abs(r.rate - overall), f"**{label}: {i}** converts at only {r.rate:.0%} (95% CI {r.lo:.0%}-{r.hi:.0%}, n={int(r.n)}) vs {overall:.0%} overall."))
    eng = cfg.get('engagement')
    if eng:
        d = df.copy(); d['_t'] = tiers(d[eng['col']].fillna(0), eng['edges'])
        t = group_table(d, '_t', conv, min_n)
        res['engagement_tiers'] = [dict(tier=str(i), n=int(r.n), conv=int(r.conv), rate=round(float(r.rate), 6),
                                        ci_lo=round(float(r.lo), 6), ci_hi=round(float(r.hi), 6)) for i, r in t.sort_index().iterrows()]
        best = None
        x = df[eng['col']].fillna(0)
        for e in eng['edges'][1:]:
            a = df[conv][x > e]; b = df[conv][(x > 0) & (x <= e)]
            if len(a) >= min_n and len(b) >= min_n:
                gap = a.mean() - b.mean()
                if best is None or gap > best[0]:
                    best = (gap, e, a.mean(), len(a), b.mean(), len(b))
        if best:
            gap, e, ra, na, rb, nb = best
            res['engagement_threshold'] = dict(edge=e, rate_above=round(float(ra), 6), n_above=int(na), rate_below=round(float(rb), 6), n_below=int(nb))
            insights.append((9, f"**Engagement ({eng['col']}):** the biggest jump is at {e}. Leads above {e} convert at {ra:.0%} (n={na:,}) vs {rb:.0%} (n={nb:,}) for leads with some activity up to {e}. Use this threshold to prioritise follow-up."))
    insights.sort(key=lambda x: -x[0])
    res['insights'] = [s for _, s in insights[:8]]
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, 'results.json'), 'w'), indent=1)
    charts(res, out, cfg)
    write_md(res, cfg, out)
    return res


def charts(res, out, cfg):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    BLUE, GREY, INK = '#2a78d6', '#9a998f', '#0b0b0b'
    plt.rcParams.update({'font.family': 'DejaVu Sans'})
    key = cfg.get('chart_dimension')
    if key:
        rows = [r for r in res['dimensions'][key] if r['n'] >= res['min_group_size'] and r['group'] not in ('unknown',)]
        rows = sorted(rows, key=lambda r: r['rate'])
        fig, ax = plt.subplots(figsize=(8, 4.6))
        y = np.arange(len(rows))
        err = [[r['rate'] - r['ci_lo'] for r in rows], [r['ci_hi'] - r['rate'] for r in rows]]
        ax.barh(y, [r['rate'] * 100 for r in rows], color=BLUE, height=.6)
        ax.errorbar([r['rate'] * 100 for r in rows], y, xerr=[[e * 100 for e in err[0]], [e * 100 for e in err[1]]], fmt='none', ecolor=INK, capsize=3, lw=1)
        ax.axvline(res['overall_rate'] * 100, color=GREY, ls='--', lw=1)
        ax.set_yticks(y); ax.set_yticklabels([f"{r['group']}  (n={r['n']:,})" for r in rows], fontsize=9)
        ax.set_xlabel('Conversion rate (%), bars show 95% confidence interval; dashed line = overall'); ax.set_xlim(0, 105)
        for s in ('top', 'right'): ax.spines[s].set_visible(False)
        ax.set_title(f'Conversion by {key.lower()}', loc='left', fontweight='bold')
        fig.tight_layout(); fig.savefig(os.path.join(out, 'chart_conversion_by_channel.png'), dpi=180); plt.close()
    if 'engagement_tiers' in res:
        t = res['engagement_tiers']; fig, ax = plt.subplots(figsize=(8, 4.2))
        ax.bar([r['tier'] for r in t], [r['rate'] * 100 for r in t], color=BLUE, width=.6)
        for i, r in enumerate(t): ax.text(i, r['rate'] * 100 + 1.5, f"{r['rate']:.0%}\nn={r['n']:,}", ha='center', fontsize=8)
        ax.set_ylim(0, 90); ax.set_ylabel('Conversion rate (%)'); ax.set_xlabel(cfg['engagement'].get('label', 'Engagement'))
        for s in ('top', 'right'): ax.spines[s].set_visible(False)
        ax.set_title('Conversion by engagement tier', loc='left', fontweight='bold')
        plt.xticks(fontsize=8); fig.tight_layout(); fig.savefig(os.path.join(out, 'chart_conversion_by_engagement.png'), dpi=180); plt.close()


def write_md(res, cfg, out):
    L = [f"# Funnel KPI report", '',
         f"Data: {res['rows']:,} leads, {res['conversions']:,} converted. Overall conversion {res['overall_rate']:.1%} (95% CI {res['overall_ci'][0]:.1%}-{res['overall_ci'][1]:.1%}).", '',
         '## What stands out', '']
    L += [f"{i+1}. {s}" for i, s in enumerate(res['insights'])]
    for label, rows in res['dimensions'].items():
        L += ['', f'## Conversion by {label}', '', '| Group | Leads | Converted | Rate | 95% CI | Lift vs overall |', '|---|---:|---:|---:|---|---:|']
        for r in rows:
            L.append(f"| {r['group']} | {r['n']:,} | {r['conv']:,} | {r['rate']:.1%} | {r['ci_lo']:.0%}-{r['ci_hi']:.0%} | {r['lift']:.2f}x |")
    if 'engagement_tiers' in res:
        L += ['', '## Conversion by engagement tier', '', '| Tier | Leads | Converted | Rate | 95% CI |', '|---|---:|---:|---:|---|']
        for r in res['engagement_tiers']:
            L.append(f"| {r['tier']} | {r['n']:,} | {r['conv']:,} | {r['rate']:.1%} | {r['ci_lo']:.0%}-{r['ci_hi']:.0%} |")
    L += ['', '## Caveats', ''] + [f'- {c}' for c in cfg.get('caveats', [])]
    L += [f"- Groups with fewer than {res['min_group_size']} leads are merged into 'other (small groups)' and not interpreted.",
          '- Associations only: a high rate does not prove the channel or activity caused the conversion.']
    open(os.path.join(out, 'report.md'), 'w').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--csv', required=True); ap.add_argument('--config', required=True); ap.add_argument('--out', required=True)
    a = ap.parse_args(); run(a.csv, json.load(open(a.config)), a.out)
    print('done ->', a.out)
