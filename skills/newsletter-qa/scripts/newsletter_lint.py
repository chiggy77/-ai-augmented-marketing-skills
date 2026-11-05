"""Lint a newsletter draft (markdown). Checks subject, length, readability, buzzwords, CTA, unsupported numbers.
Usage: python newsletter_lint.py draft.md [--json]
Draft format: first line 'Subject: ...', then body. Links as [text](url). Numbers should carry a source line starting with 'Source:'.
"""
import re, sys, json

BUZZ = ['game-changer', 'game changing', 'revolutionary', 'cutting-edge', 'leverage', 'synergy', 'unlock', 'next-level', 'best-in-class', 'seamless', 'supercharge', 'disrupt', 'world-class', 'robust solution']
LIMITS = dict(subject_max=60, words_min=120, words_max=350, grade_max=11.0, sentence_max_words=28)

def syllables(w):
    w = w.lower(); w = re.sub(r'[^a-z]', '', w)
    if not w: return 0
    n = len(re.findall(r'[aeiouy]+', w)); n -= w.endswith('e') and n > 1
    return max(n, 1)

def lint(text):
    lines = text.strip().splitlines()
    subject = lines[0].replace('Subject:', '').strip() if lines and lines[0].startswith('Subject:') else ''
    body = '\n'.join(lines[1:] if subject else lines)
    sources = [l for l in body.splitlines() if l.strip().lower().startswith('source')]
    prose = '\n'.join(l for l in body.splitlines() if not l.strip().lower().startswith('source'))
    plain = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', prose); plain = re.sub(r'[#*_>`-]', ' ', plain)
    words = re.findall(r"[A-Za-z0-9'%€$.,-]+", plain); words = [w for w in words if re.search(r'[A-Za-z0-9]', w)]
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', plain) if len(s.split()) > 2]
    syl = sum(syllables(w) for w in words if re.search('[A-Za-z]', w))
    grade = 0.39 * (len(words) / max(len(sents), 1)) + 11.8 * (syl / max(len(words), 1)) - 15.59
    links = re.findall(r'\[[^\]]+\]\(https?://[^)]+\)', body)
    nums = re.findall(r'\d[\d,.]*\s?%|\d{1,3}(?:,\d{3})+|\b\d+x\b', plain)
    long_s = [s for s in sents if len(s.split()) > LIMITS['sentence_max_words']]
    buzz = [b for b in BUZZ if b in text.lower()]
    checks = [
        ('Subject present and <= %d characters' % LIMITS['subject_max'], bool(subject) and len(subject) <= LIMITS['subject_max'], f'{len(subject)} characters'),
        ('Body length %d-%d words' % (LIMITS['words_min'], LIMITS['words_max']), LIMITS['words_min'] <= len(words) <= LIMITS['words_max'], f'{len(words)} words'),
        ('Reading grade <= %.0f (Flesch-Kincaid)' % LIMITS['grade_max'], grade <= LIMITS['grade_max'], f'grade {grade:.1f}'),
        ('No sentence over %d words' % LIMITS['sentence_max_words'], not long_s, f'{len(long_s)} long'),
        ('Exactly one call-to-action link', len(links) == 1, f'{len(links)} links'),
        ('No buzzwords', not buzz, ', '.join(buzz) or 'none'),
        ('Numbers have a source line', (not nums) or bool(sources), f'{len(nums)} figures, {len(sources)} source line(s)'),
    ]
    return dict(subject=subject, words=len(words), grade=round(grade, 1), checks=[dict(name=n, ok=o, detail=d) for n, o, d in checks], passed=all(o for _, o, _ in checks))

if __name__ == '__main__':
    r = lint(open(sys.argv[1]).read())
    if '--json' in sys.argv: print(json.dumps(r, indent=1))
    else:
        for c in r['checks']: print(('PASS ' if c['ok'] else 'FAIL ') + c['name'] + ' (' + c['detail'] + ')')
        print('RESULT:', 'PASS' if r['passed'] else 'FAIL')
