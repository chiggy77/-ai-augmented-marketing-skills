"""Tiny action tracker kept in a CSV: add, list, overdue.
Usage: python tracker.py tracker.csv add "action" owner YYYY-MM-DD
       python tracker.py tracker.csv list
       python tracker.py tracker.csv overdue [YYYY-MM-DD]
"""
import csv, os, sys, datetime as dt
FIELDS = ['id', 'action', 'owner', 'due', 'status']

def load(path):
    if not os.path.exists(path): return []
    with open(path, newline='') as f: return list(csv.DictReader(f))

def save(path, rows):
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)

def overdue(rows, today):
    return [r for r in rows if r['status'] != 'done' and dt.date.fromisoformat(r['due']) < today]

if __name__ == '__main__':
    path, cmd = sys.argv[1], sys.argv[2]; rows = load(path)
    if cmd == 'add':
        rows.append(dict(id=str(len(rows) + 1), action=sys.argv[3], owner=sys.argv[4], due=sys.argv[5], status='open')); save(path, rows)
    elif cmd == 'list':
        for r in rows: print(r['id'], r['status'], r['due'], r['owner'], '-', r['action'])
    elif cmd == 'overdue':
        today = dt.date.fromisoformat(sys.argv[3]) if len(sys.argv) > 3 else dt.date.today()
        for r in overdue(rows, today): print(r['id'], r['due'], r['owner'], '-', r['action'])
