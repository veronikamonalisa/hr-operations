#!/usr/bin/env python3
"""Build dashboard data + index.html from Employee Information table (filtered Jan 2026 - present)."""

import json
from datetime import datetime
from collections import defaultdict

# ── Load raw data ─────────────────────────────────────────────────────────────
with open('emp_info_raw.json') as f:
    raw = json.load(f)
all_employees = raw['employees']

# ── Date helpers ─────────────────────────────────────────────────────────────
def parse_date(s):
    if not s or str(s).strip() in ('', 'None', 'null'):
        return None
    for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(str(s).strip(), fmt)
        except:
            pass
    return None

CUTOFF = datetime(2026, 1, 1)
TODAY  = datetime(2026, 10, 29)

# ── Filter: active per Jan 1 2026 to today ────────────────────────────────────
employees = []
for e in all_employees:
    name = (e.get('full_name') or '').strip()
    if not name or name == 'Dummy Employee A':
        continue
    status      = e.get('status') or ''
    resign_date = parse_date(e.get('resign_date'))
    if status == 'Active':
        employees.append(e)
    elif status == 'Resigned' and resign_date and resign_date >= CUTOFF:
        employees.append(e)

print(f'Filtered employees: {len(employees)}')

# ── PT mapping ────────────────────────────────────────────────────────────────
PT_SHORT = {
    'PT Maleo Kreatif Indonesia':    'Maleo',
    'PT Jingga Kreasi Multiguna':    'Jingga',
    'Pusat':                         'Pusat',
    'PT Langit Bimasakti Multiguna': 'Langit',
    'PT Orca Performa Multiguna':    'Orca',
    'PT Sisi Karya Multiguna':       'Sisi',
    'PT Menuju Bulan Multiguna':     'MBM',
}

def get_pt(e):
    return e.get('branch') or 'Unknown'

# ── Global stats ──────────────────────────────────────────────────────────────
total = len(employees)
active_count    = sum(1 for e in employees if e['status'] == 'Active')
resigned_period = sum(1 for e in employees if e['status'] == 'Resigned')

emp_status_count = defaultdict(int)
for e in employees:
    s = (e['employment_status'] or 'None').strip()
    emp_status_count[s] += 1

gender_count = defaultdict(int)
for e in employees:
    g = (e.get('gender') or 'Unknown').strip()
    gender_count[g] += 1

# ── Monthly join/resign trend ─────────────────────────────────────────────────
join_by_month   = defaultdict(int)
resign_by_month = defaultdict(int)
for e in employees:
    jd = parse_date(e.get('join_date'))
    if jd:
        key = jd.strftime('%Y-%m')
        if key >= '2025-01':   # only show recent 24 months
            join_by_month[key] += 1
    rd = parse_date(e.get('resign_date'))
    if rd and rd >= CUTOFF:
        key = rd.strftime('%Y-%m')
        resign_by_month[key] += 1

# ── Job level distribution ────────────────────────────────────────────────────
# Normalize job levels
LEVEL_MAP = {
    'board of director':                             'Director',
    'managing director / senior functional director':'Director',
    'functional director':                            'Director',
    'director':                                       'Director',
    'cgh / head':                                     'Head',
    'senior head / associate directors':              'Head',
    'head':                                           'Head',
    'senior manager':                                 'Manager',
    'junior manager':                                 'Manager',
    'manager':                                        'Manager',
    'supervisor':                                     'Manager',
    'senior officer':                                 'Officer',
    'middle officer':                                 'Officer',
    'officer':                                        'Officer',
    'junior officer':                                 'Officer',
    'senior staff':                                   'Staff',
    'staff':                                          'Staff',
    'junior staff':                                   'Staff',
    'non officer':                                    'Non-Officer',
}
level_count = defaultdict(int)
for e in employees:
    lvl = (e.get('job_level') or 'Unknown').strip().lower()
    level_count[LEVEL_MAP.get(lvl, 'Other')] += 1

# ── Organization distribution ─────────────────────────────────────────────────
org_count = defaultdict(int)
for e in employees:
    org = (e.get('organization_name') or 'Unknown').strip()
    # Normalize whitespace
    org = ' '.join(org.split())
    if org:
        org_count[org] += 1

top_orgs = sorted(org_count.items(), key=lambda x: -x[1])[:15]

# ── Per-PT stats ──────────────────────────────────────────────────────────────
pt_stats = defaultdict(lambda: {
    'total': 0, 'active': 0, 'resigned_period': 0,
    'permanent': 0, 'probation': 0, 'contract': 0, 'intern': 0,
    'male': 0, 'female': 0,
    'level': defaultdict(int),
    'org': defaultdict(int),
})

for e in employees:
    pt   = get_pt(e)
    stat = pt_stats[pt]
    stat['total'] += 1
    if e['status'] == 'Active':
        stat['active'] += 1
    else:
        stat['resigned_period'] += 1
    es = (e['employment_status'] or '').strip().lower()
    if 'permanent' in es:
        stat['permanent'] += 1
    elif 'probation' in es:
        stat['probation'] += 1
    elif 'contract' in es:
        stat['contract'] += 1
    elif 'intern' in es or 'internship' in es:
        stat['intern'] += 1
    g = (e.get('gender') or '').strip().lower()
    if g == 'male':
        stat['male'] += 1
    elif g == 'female':
        stat['female'] += 1
    lvl = (e.get('job_level') or '').strip().lower()
    stat['level'][LEVEL_MAP.get(lvl, 'Other')] += 1
    org = ' '.join((e.get('organization_name') or 'Unknown').strip().split())
    stat['org'][org] += 1

# ── Employee table (for website display) ─────────────────────────────────────
emp_table = []
for e in employees:
    rd = parse_date(e.get('resign_date'))
    emp_table.append({
        'id':         e.get('employee_id') or '-',
        'name':       e.get('full_name') or '-',
        'pt':         get_pt(e),
        'pt_short':   PT_SHORT.get(get_pt(e), get_pt(e)[:8]),
        'org':        ' '.join((e.get('organization_name') or '-').strip().split()),
        'position':   e.get('job_position') or '-',
        'level':      e.get('job_level') or '-',
        'emp_status': e.get('employment_status') or '-',
        'status':     e.get('status') or '-',
        'join_date':  e.get('join_date') or '-',
        'resign_date': rd.strftime('%Y-%m-%d') if rd else '-',
        'gender':     e.get('gender') or '-',
        'email':      e.get('email') or '-',
    })

# Sort by PT then name
emp_table.sort(key=lambda x: (x['pt'], x['name']))

# ── Build JSON ────────────────────────────────────────────────────────────────
# Build sorted month list for charts (Jan 2025 – Oct 2026)
months_range = []
d = datetime(2025, 1, 1)
while d <= TODAY:
    months_range.append(d.strftime('%Y-%m'))
    if d.month == 12:
        d = d.replace(year=d.year+1, month=1)
    else:
        d = d.replace(month=d.month+1)

# Serialize pt_stats (convert defaultdicts)
pt_stats_out = {}
for pt, s in pt_stats.items():
    pt_stats_out[pt] = {
        'total':          s['total'],
        'active':         s['active'],
        'resigned_period': s['resigned_period'],
        'permanent':      s['permanent'],
        'probation':      s['probation'],
        'contract':       s['contract'],
        'intern':         s['intern'],
        'male':           s['male'],
        'female':         s['female'],
        'level':          dict(s['level']),
        'top_orgs':       sorted(s['org'].items(), key=lambda x: -x[1])[:8],
    }

dashboard = {
    'generated': TODAY.strftime('%Y-%m-%d'),
    'filter_note': 'Active employees from 2026-01-01 to 2026-10-29',
    'pt_list':  sorted(pt_stats.keys()),
    'pt_short': PT_SHORT,
    'months':   months_range,
    'global': {
        'total':            total,
        'active':           active_count,
        'resigned_period':  resigned_period,
        'permanent':        emp_status_count.get('Permanent', 0),
        'probation':        emp_status_count.get('Probation', 0),
        'contract':         emp_status_count.get('Contract', 0),
        'intern':           emp_status_count.get('Internship', 0),
        'male':             gender_count.get('Male', 0),
        'female':           gender_count.get('Female', 0),
        'join_by_month':    dict(join_by_month),
        'resign_by_month':  dict(resign_by_month),
        'level_dist':       dict(level_count),
        'top_orgs':         top_orgs,
    },
    'pt_stats': pt_stats_out,
    'employees': emp_table,
}

with open('emp_dashboard_data.json', 'w') as f:
    json.dump(dashboard, f, ensure_ascii=False, default=str)

print(f'Saved emp_dashboard_data.json')
print(f'  Total: {total}')
print(f'  Active: {active_count}  |  Resigned-in-period: {resigned_period}')
print(f'  Permanent: {emp_status_count["Permanent"]}  Probation: {emp_status_count["Probation"]}  Contract: {emp_status_count["Contract"]}')
print(f'  PTs: {list(pt_stats.keys())}')
print(f'  Employee table rows: {len(emp_table)}')
