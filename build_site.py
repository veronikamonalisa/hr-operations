#!/usr/bin/env python3
"""Build unified HR Operations index.html from emp_dashboard_data.json"""

import json

with open('emp_dashboard_data.json') as f:
    D = json.load(f)

g       = D['global']
pts     = D['pt_list']
PT_S    = D['pt_short']
months  = D['months']
ps      = D['pt_stats']
emps    = D['employees']

# Month labels
month_labels = [m[5:] + '/' + m[2:4] for m in months]  # "01/25"

def js(v):
    return json.dumps(v, ensure_ascii=False)

# Join/resign arrays (sorted by month)
join_data   = [g['join_by_month'].get(m, 0)   for m in months]
resign_data = [g['resign_by_month'].get(m, 0) for m in months]

# Level distribution
level_order = ['Director', 'Head', 'Manager', 'Officer', 'Staff', 'Non-Officer', 'Other']
level_vals  = [g['level_dist'].get(l, 0) for l in level_order]

# Top orgs
top_org_labels = [o[0] for o in g['top_orgs'][:12]]
top_org_vals   = [o[1] for o in g['top_orgs'][:12]]

# PT chart data
pt_labels     = [PT_S.get(p, p[:10]) for p in pts]
pt_active     = [ps[p]['active']    for p in pts]
pt_resigned   = [ps[p]['resigned_period'] for p in pts]
pt_permanent  = [ps[p]['permanent'] for p in pts]
pt_probation  = [ps[p]['probation'] for p in pts]
pt_contract   = [ps[p]['contract']  for p in pts]

# ── Color + badge helpers ─────────────────────────────────────────────────────
def pt_color(pt):
    colors = {
        'PT Maleo Kreatif Indonesia':    '#4f46e5',
        'PT Jingga Kreasi Multiguna':    '#f97316',
        'Pusat':                         '#10b981',
        'PT Langit Bimasakti Multiguna': '#3b82f6',
        'PT Orca Performa Multiguna':    '#8b5cf6',
        'PT Sisi Karya Multiguna':       '#ec4899',
        'PT Menuju Bulan Multiguna':     '#14b8a6',
    }
    return colors.get(pt, '#6b7280')

def badge_status(s):
    if s == 'Active':
        return f'<span class="badge badge-green">{s}</span>'
    return f'<span class="badge badge-orange">{s}</span>'

def badge_emp(s):
    s = s or '-'
    cl = {'Permanent':'badge-blue','Probation':'badge-orange','Contract':'badge-purple','Internship':'badge-green'}.get(s, 'badge-gray')
    return f'<span class="badge {cl}">{s}</span>'

def initials(name):
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper()

emp_rows_html = ''
for e in emps:
    ini = initials(e['name'])
    emp_rows_html += f'''
        <tr data-pt="{e['pt']}" data-status="{e['status']}" data-emp-status="{e['emp_status']}">
          <td><div class="employee-cell">
            <div class="avatar" style="background:{pt_color(e['pt'])}">{ini}</div>
            <div><div style="font-weight:600;font-size:.85rem">{e['name']}</div>
            <div style="font-size:.75rem;color:#6b7280">{e['id']}</div></div>
          </div></td>
          <td><span class="badge badge-blue" style="font-size:.7rem">{PT_S.get(e['pt'], e['pt'][:10])}</span></td>
          <td style="font-size:.82rem">{e['org']}</td>
          <td style="font-size:.82rem">{e['position']}</td>
          <td style="font-size:.75rem">{e['level']}</td>
          <td>{badge_emp(e['emp_status'])}</td>
          <td>{badge_status(e['status'])}</td>
          <td style="font-size:.78rem">{e['join_date']}</td>
          <td style="font-size:.78rem">{e['resign_date'] if e['resign_date'] != '-' else ''}</td>
        </tr>'''

# Rebuild with color support
emp_rows_html = ''
for e in emps:
    ini = initials(e['name'])
    color = pt_color(e['pt'])
    emp_rows_html += f'''
        <tr data-pt="{e['pt']}" data-status="{e['status']}" data-emp-status="{e['emp_status']}">
          <td><div class="employee-cell">
            <div class="avatar" style="background:{color}">{ini}</div>
            <div><div style="font-weight:600;font-size:.85rem">{e['name']}</div>
            <div style="font-size:.75rem;color:#6b7280">{e['id']}</div></div>
          </div></td>
          <td><span class="badge badge-blue" style="font-size:.7rem">{PT_S.get(e['pt'], e['pt'][:10])}</span></td>
          <td style="font-size:.82rem">{e['org']}</td>
          <td style="font-size:.82rem">{e['position']}</td>
          <td style="font-size:.75rem">{e['level']}</td>
          <td>{badge_emp(e['emp_status'])}</td>
          <td>{badge_status(e['status'])}</td>
          <td style="font-size:.78rem">{e['join_date']}</td>
          <td style="font-size:.78rem">{e['resign_date'] if e['resign_date'] != '-' else ''}</td>
        </tr>'''

# PT summary cards for dashboard
pt_cards_html = ''
for pt in sorted(pts, key=lambda p: -ps[p]['total']):
    st = ps[pt]
    short = PT_S.get(pt, pt[:12])
    color = pt_color(pt)
    pct_active = round(st['active'] / st['total'] * 100) if st['total'] else 0
    pt_cards_html += f'''
      <div class="pt-card" data-pt="{pt}">
        <div style="display:flex;align-items:center;gap:.75rem;margin-bottom:.75rem">
          <div style="width:40px;height:40px;border-radius:10px;background:{color}20;display:flex;align-items:center;justify-content:center;font-size:1.1rem;font-weight:700;color:{color}">{short[0]}</div>
          <div>
            <div style="font-weight:700;font-size:.9rem">{short}</div>
            <div style="font-size:.72rem;color:#6b7280">{pt}</div>
          </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:.5rem;margin-bottom:.75rem">
          <div style="text-align:center;padding:.4rem;background:#f9fafb;border-radius:8px">
            <div style="font-size:1.1rem;font-weight:700;color:{color}">{st['total']}</div>
            <div style="font-size:.65rem;color:#6b7280">Total</div>
          </div>
          <div style="text-align:center;padding:.4rem;background:#d1fae5;border-radius:8px">
            <div style="font-size:1.1rem;font-weight:700;color:#065f46">{st['active']}</div>
            <div style="font-size:.65rem;color:#065f46">Active</div>
          </div>
          <div style="text-align:center;padding:.4rem;background:#ffedd5;border-radius:8px">
            <div style="font-size:1.1rem;font-weight:700;color:#c2410c">{st['resigned_period']}</div>
            <div style="font-size:.65rem;color:#c2410c">Resigned</div>
          </div>
        </div>
        <div style="display:flex;gap:.3rem;flex-wrap:wrap">
          <span class="badge badge-blue">{st['permanent']} Perm</span>
          <span class="badge badge-orange">{st['probation']} Prob</span>
          {'<span class="badge badge-purple">'+str(st['contract'])+' Contract</span>' if st['contract'] else ''}
          <span class="badge" style="background:#f0fdf4;color:#166534;font-size:.65rem">{st['male']}M / {st['female']}F</span>
        </div>
        <div style="margin-top:.75rem">
          <div style="font-size:.7rem;color:#6b7280;margin-bottom:.2rem">Active rate: {pct_active}%</div>
          <div style="background:#f3f4f6;border-radius:4px;height:4px">
            <div style="background:{color};width:{pct_active}%;height:4px;border-radius:4px"></div>
          </div>
        </div>
      </div>'''

html = f'''<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HR Operations – FCN Group</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    .filter-bar {{
      background:#fff;padding:.75rem 2rem;
      border-bottom:1px solid #e8ecf4;
      display:flex;align-items:center;gap:.75rem;flex-wrap:wrap;
    }}
    .filter-bar select {{
      padding:.4rem .75rem;border:1.5px solid #e8ecf4;border-radius:8px;
      font-size:.85rem;outline:none;cursor:pointer;
    }}
    .filter-bar select:focus {{ border-color:#4f46e5; }}
    .filter-bar label {{ font-size:.8rem;font-weight:600;color:#6b7280; }}
    .pt-grid {{
      display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:1.5rem;
    }}
    .pt-card {{
      background:#fff;border-radius:14px;padding:1.25rem;
      box-shadow:0 1px 4px rgba(0,0,0,.06);
      transition:box-shadow .2s;cursor:default;
    }}
    .pt-card:hover {{ box-shadow:0 4px 12px rgba(0,0,0,.1); }}
    .chart-grid {{
      display:grid;grid-template-columns:1fr 1fr;gap:1.25rem;margin-bottom:1.5rem;
    }}
    .chart-card {{
      background:#fff;border-radius:16px;padding:1.5rem;
      box-shadow:0 1px 4px rgba(0,0,0,.06);
    }}
    .chart-card h3 {{ font-size:.95rem;font-weight:600;margin-bottom:1rem; }}
    .chart-full {{
      background:#fff;border-radius:16px;padding:1.5rem;
      box-shadow:0 1px 4px rgba(0,0,0,.06);margin-bottom:1.5rem;
    }}
    .chart-full h3 {{ font-size:.95rem;font-weight:600;margin-bottom:1rem; }}
    .emp-controls {{
      display:flex;gap:.75rem;align-items:center;flex-wrap:wrap;margin-bottom:1rem;
    }}
    .emp-controls input {{
      padding:.6rem 1rem;border:1.5px solid #e8ecf4;border-radius:10px;
      font-size:.875rem;outline:none;width:260px;
    }}
    .emp-controls input:focus {{ border-color:#4f46e5; }}
    .emp-controls select {{
      padding:.6rem .75rem;border:1.5px solid #e8ecf4;border-radius:10px;
      font-size:.85rem;outline:none;cursor:pointer;
    }}
    .emp-count {{
      font-size:.8rem;color:#6b7280;margin-left:auto;
    }}
    .table-wrap {{ overflow-x:auto; }}
    #emp-tbody tr.hidden {{ display:none; }}
    .section-note {{
      font-size:.8rem;color:#6b7280;
      background:#f9fafb;border-radius:8px;padding:.5rem 1rem;
      margin-bottom:1rem;border-left:3px solid #4f46e5;
    }}
  </style>
</head>
<body>

<!-- ── Sidebar ── -->
<aside class="sidebar">
  <div class="sidebar-logo">
    <span class="logo-icon">🏢</span>
    <span>HR Operations</span>
  </div>
  <nav class="sidebar-nav">
    <a class="nav-item active" onclick="showSection('dashboard',event)">
      <span class="nav-icon">📊</span> Dashboard
    </a>
    <a class="nav-item" onclick="showSection('employees',event)">
      <span class="nav-icon">👥</span> Employees
    </a>
    <a class="nav-item" onclick="showSection('leave',event)">
      <span class="nav-icon">🏖️</span> Leave Management
    </a>
    <a class="nav-item" onclick="showSection('payroll',event)">
      <span class="nav-icon">💰</span> Payroll
    </a>
    <a class="nav-item" onclick="showSection('recruitment',event)">
      <span class="nav-icon">🔍</span> Recruitment
    </a>
    <a class="nav-item" onclick="showSection('performance',event)">
      <span class="nav-icon">⭐</span> Performance
    </a>
    <a class="nav-item" onclick="showSection('it',event)">
      <span class="nav-icon">💻</span> IT
    </a>
    <a class="nav-item" onclick="showSection('ga',event)">
      <span class="nav-icon">🏗️</span> General Affairs
    </a>
  </nav>
  <div class="sidebar-user">
    <div class="user-avatar">VR</div>
    <div>
      <div class="user-name">Vero</div>
      <div class="user-role">HR Manager</div>
    </div>
  </div>
</aside>

<!-- ── Main ── -->
<div class="main">
  <header class="header">
    <div class="header-title" id="page-title">Dashboard</div>
    <div class="header-actions">
      <span style="font-size:.8rem;color:#6b7280">Data per 29 Oct 2026 · Active Jan 2026–sekarang</span>
    </div>
  </header>

  <!-- Filter Bar (Dashboard only) -->
  <div class="filter-bar" id="filter-bar">
    <label>Filter PT/Opco:</label>
    <select id="pt-filter" onchange="filterDashboard()">
      <option value="all">Semua PT/Opco</option>
      {''.join(f'<option value="{p}">{PT_S.get(p,p)}</option>' for p in sorted(pts))}
    </select>
    <span style="font-size:.78rem;color:#6b7280" id="filter-count">419 karyawan · Jan 2026 – Oct 2026</span>
  </div>

  <!-- ══════════════════════════════════════════════════════════════
       DASHBOARD
  ══════════════════════════════════════════════════════════════ -->
  <section class="section active" id="section-dashboard">

    <!-- Stat cards -->
    <div class="stats-grid" id="stat-cards">
      <div class="stat-card">
        <div class="stat-icon blue">👥</div>
        <div>
          <div class="stat-value" id="s-total">{g['total']}</div>
          <div class="stat-label">Total Karyawan</div>
          <div class="stat-change neutral">Jan 2026 – sekarang</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">✅</div>
        <div>
          <div class="stat-value" id="s-active">{g['active']}</div>
          <div class="stat-label">Karyawan Aktif</div>
          <div class="stat-change positive">per 29 Oct 2026</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">🚪</div>
        <div>
          <div class="stat-value" id="s-resigned">{g['resigned_period']}</div>
          <div class="stat-label">Resigned (2026)</div>
          <div class="stat-change negative">dalam periode</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">📋</div>
        <div>
          <div class="stat-value" id="s-permanent">{g['permanent']}</div>
          <div class="stat-label">Permanent</div>
          <div class="stat-change neutral">{g['probation']} Probation · {g['contract']} Contract</div>
        </div>
      </div>
    </div>

    <!-- PT Cards -->
    <div style="font-size:.95rem;font-weight:700;margin-bottom:.75rem;color:#1a1a2e">Breakdown per PT / Opco</div>
    <div class="pt-grid" id="pt-cards">
      {pt_cards_html}
    </div>

    <!-- Charts row 1: Trend + Status -->
    <div class="chart-grid">
      <div class="chart-card" style="grid-column:span 2">
        <h3>📈 Tren Bergabung & Resign per Bulan</h3>
        <canvas id="trendChart" height="80"></canvas>
      </div>
    </div>

    <!-- Charts row 2: Level dist + Gender + Org -->
    <div class="chart-grid">
      <div class="chart-card">
        <h3>🏅 Distribusi Job Level</h3>
        <canvas id="levelChart" height="160"></canvas>
      </div>
      <div class="chart-card">
        <h3>⚧ Distribusi Gender</h3>
        <canvas id="genderChart" height="160"></canvas>
      </div>
    </div>

    <!-- Charts row 3: PT breakdown + Org -->
    <div class="chart-grid">
      <div class="chart-card">
        <h3>🏢 Headcount per PT (Active vs Resigned)</h3>
        <canvas id="ptChart" height="180"></canvas>
      </div>
      <div class="chart-card">
        <h3>🗂️ Top Divisi / Organisasi</h3>
        <canvas id="orgChart" height="180"></canvas>
      </div>
    </div>

    <!-- Employment status breakdown -->
    <div class="chart-full">
      <h3>📊 Status Kepegawaian per PT</h3>
      <canvas id="empStatusChart" height="70"></canvas>
    </div>

  </section>

  <!-- ══════════════════════════════════════════════════════════════
       EMPLOYEES
  ══════════════════════════════════════════════════════════════ -->
  <section class="section" id="section-employees">
    <div class="section-note">
      📋 Menampilkan <strong>{len(emps)} karyawan</strong> yang aktif pada periode 1 Jan 2026 – 29 Oct 2026 (termasuk yang sudah resign dalam periode ini).
    </div>
    <div class="card">
      <div class="emp-controls">
        <input type="text" id="emp-search" placeholder="🔍  Cari nama, ID, posisi..." oninput="filterEmployees()">
        <select id="emp-pt-filter" onchange="filterEmployees()">
          <option value="">Semua PT</option>
          {''.join(f'<option value="{p}">{PT_S.get(p,p)}</option>' for p in sorted(pts))}
        </select>
        <select id="emp-status-filter" onchange="filterEmployees()">
          <option value="">Semua Status</option>
          <option value="Active">Active</option>
          <option value="Resigned">Resigned</option>
        </select>
        <select id="emp-type-filter" onchange="filterEmployees()">
          <option value="">Semua Tipe</option>
          <option value="Permanent">Permanent</option>
          <option value="Probation">Probation</option>
          <option value="Contract">Contract</option>
          <option value="Internship">Internship</option>
        </select>
        <span class="emp-count" id="emp-count">{len(emps)} karyawan</span>
      </div>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Karyawan</th>
              <th>PT / Opco</th>
              <th>Divisi</th>
              <th>Posisi</th>
              <th>Level</th>
              <th>Tipe</th>
              <th>Status</th>
              <th>Join Date</th>
              <th>Resign Date</th>
            </tr>
          </thead>
          <tbody id="emp-tbody">
            {emp_rows_html}
          </tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- ══════════════════════════════════════════════════════════════
       LEAVE
  ══════════════════════════════════════════════════════════════ -->
  <section class="section" id="section-leave">
    <div class="card">
      <div class="card-header"><h3>🏖️ Leave Management</h3></div>
      <p style="color:#6b7280;font-size:.9rem">Modul leave management akan diintegrasikan dengan sistem HR. Data cuti per karyawan dapat dilihat setelah integrasi selesai.</p>
    </div>
  </section>

  <!-- ══════════════════════════════════════════════════════════════
       PAYROLL
  ══════════════════════════════════════════════════════════════ -->
  <section class="section" id="section-payroll">
    <div class="card">
      <div class="card-header"><h3>💰 Payroll</h3></div>
      <p style="color:#6b7280;font-size:.9rem">Modul payroll terintegrasi dengan ALVA Payroll DB. Data payroll tersedia dan akan ditampilkan setelah validasi mapping PT selesai.</p>
    </div>
  </section>

  <!-- ══════════════════════════════════════════════════════════════
       RECRUITMENT
  ══════════════════════════════════════════════════════════════ -->
  <section class="section" id="section-recruitment">
    <div class="card">
      <div class="card-header"><h3>🔍 Recruitment</h3></div>
      <p style="color:#6b7280;font-size:.9rem">Modul recruitment akan menampilkan pipeline kandidat dan progress hiring per posisi.</p>
    </div>
  </section>

  <!-- ══════════════════════════════════════════════════════════════
       PERFORMANCE
  ══════════════════════════════════════════════════════════════ -->
  <section class="section" id="section-performance">
    <div class="card">
      <div class="card-header"><h3>⭐ Performance Reviews</h3></div>
      <p style="color:#6b7280;font-size:.9rem">Modul performance review akan menampilkan hasil review karyawan dan metrik KPI per PT.</p>
    </div>
  </section>

  <!-- ══════════════════════════════════════════════════════════════
       IT
  ══════════════════════════════════════════════════════════════ -->
  <section class="section" id="section-it">
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">🖥️</div>
        <div>
          <div class="stat-value">24</div>
          <div class="stat-label">Open Tickets</div>
          <div class="stat-change negative">↑ 3 dari minggu lalu</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">✅</div>
        <div>
          <div class="stat-value">87%</div>
          <div class="stat-label">Resolution Rate</div>
          <div class="stat-change positive">↑ 5% dari bulan lalu</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">⚠️</div>
        <div>
          <div class="stat-value">3</div>
          <div class="stat-label">Critical Issues</div>
          <div class="stat-change negative">Perlu perhatian</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">🛡️</div>
        <div>
          <div class="stat-value">99.2%</div>
          <div class="stat-label">System Uptime</div>
          <div class="stat-change positive">Stabil</div>
        </div>
      </div>
    </div>
    <div class="card">
      <div class="card-header">
        <h3>🖥️ Recent IT Tickets</h3>
        <a href="#" class="card-link">View All</a>
      </div>
      <table class="table">
        <thead><tr><th>Ticket</th><th>Issue</th><th>Submitted By</th><th>Priority</th><th>Status</th></tr></thead>
        <tbody>
          <tr><td>#IT-2847</td><td>VPN Access Issue</td><td>Creative Team</td><td><span class="badge badge-red">High</span></td><td><span class="badge badge-orange">In Progress</span></td></tr>
          <tr><td>#IT-2846</td><td>Laptop Setup - New Hire</td><td>HR Dept</td><td><span class="badge badge-blue">Medium</span></td><td><span class="badge badge-green">Resolved</span></td></tr>
          <tr><td>#IT-2845</td><td>Email Configuration</td><td>Finance Team</td><td><span class="badge badge-blue">Medium</span></td><td><span class="badge badge-green">Resolved</span></td></tr>
          <tr><td>#IT-2844</td><td>Software License Renewal</td><td>IT Dept</td><td><span class="badge badge-orange">High</span></td><td><span class="badge badge-orange">Pending</span></td></tr>
          <tr><td>#IT-2843</td><td>Network Slowdown</td><td>Account Team</td><td><span class="badge badge-red">Critical</span></td><td><span class="badge badge-orange">In Progress</span></td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <!-- ══════════════════════════════════════════════════════════════
       GA
  ══════════════════════════════════════════════════════════════ -->
  <section class="section" id="section-ga">
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">🏢</div>
        <div>
          <div class="stat-value">8</div>
          <div class="stat-label">Office Locations</div>
          <div class="stat-change neutral">Aktif</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">📦</div>
        <div>
          <div class="stat-value">142</div>
          <div class="stat-label">Asset Terdaftar</div>
          <div class="stat-change positive">↑ 12 bulan ini</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">🔧</div>
        <div>
          <div class="stat-value">7</div>
          <div class="stat-label">Maintenance Requests</div>
          <div class="stat-change neutral">Dalam antrean</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">📋</div>
        <div>
          <div class="stat-value">15</div>
          <div class="stat-label">Vendor Aktif</div>
          <div class="stat-change neutral">Per Oktober 2026</div>
        </div>
      </div>
    </div>
    <div class="mid-grid">
      <div class="card">
        <div class="card-header"><h3>🏢 Office Locations</h3></div>
        <div class="event-list">
          <div class="event-item"><div class="event-date"><span class="date-day">JKT</span></div><div class="event-info"><div class="event-title">Jakarta HQ (Pusat)</div><div class="event-meta">Graha Layar Prima · 5 floors</div></div></div>
          <div class="event-item"><div class="event-date"><span class="date-day">MLO</span></div><div class="event-info"><div class="event-title">Maleo – Jakarta</div><div class="event-meta">155 karyawan · Creative hub</div></div></div>
          <div class="event-item"><div class="event-date"><span class="date-day">JNG</span></div><div class="event-info"><div class="event-title">Jingga – Jakarta</div><div class="event-meta">110 karyawan · Account hub</div></div></div>
          <div class="event-item"><div class="event-date"><span class="date-day">LGT</span></div><div class="event-info"><div class="event-title">Langit – Jakarta</div><div class="event-meta">39 karyawan</div></div></div>
        </div>
      </div>
      <div class="card">
        <div class="card-header"><h3>📋 Asset Summary</h3></div>
        <table class="table">
          <thead><tr><th>Kategori</th><th>Jumlah</th><th>Status</th></tr></thead>
          <tbody>
            <tr><td>Laptop/PC</td><td>98</td><td><span class="badge badge-green">Good</span></td></tr>
            <tr><td>Monitor</td><td>24</td><td><span class="badge badge-green">Good</span></td></tr>
            <tr><td>Furniture</td><td>12</td><td><span class="badge badge-orange">Maintenance</span></td></tr>
            <tr><td>Kendaraan Operasional</td><td>5</td><td><span class="badge badge-blue">Available</span></td></tr>
            <tr><td>AV Equipment</td><td>3</td><td><span class="badge badge-green">Good</span></td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>

</div><!-- /main -->

<script src="app.js"></script>
<script>
// ── Data ─────────────────────────────────────────────────────────────────────
const DATA = {js(D)};

const COLORS = {{
  'PT Maleo Kreatif Indonesia':    '#4f46e5',
  'PT Jingga Kreasi Multiguna':    '#f97316',
  'Pusat':                         '#10b981',
  'PT Langit Bimasakti Multiguna': '#3b82f6',
  'PT Orca Performa Multiguna':    '#8b5cf6',
  'PT Sisi Karya Multiguna':       '#ec4899',
  'PT Menuju Bulan Multiguna':     '#14b8a6',
  'Unknown':                       '#6b7280',
}};

// ── Charts ────────────────────────────────────────────────────────────────────
let trendChart, levelChart, genderChart, ptChart, orgChart, empStatusChart;

function initCharts(ptFilter='all') {{
  const g  = ptFilter === 'all' ? DATA.global : buildPTGlobal(ptFilter);
  const pts = ptFilter === 'all' ? DATA.pt_list : [ptFilter];

  const months = DATA.months;
  const mLabels = months.map(m => m.slice(5)+'/'+m.slice(2,4));

  // Trend
  if (trendChart) trendChart.destroy();
  trendChart = new Chart(document.getElementById('trendChart'), {{
    type: 'bar',
    data: {{
      labels: mLabels,
      datasets: [
        {{label:'Join', data: months.map(m => (g.join_by_month[m]||0)), backgroundColor:'rgba(79,70,229,.7)', borderRadius:4}},
        {{label:'Resign', data: months.map(m => (g.resign_by_month[m]||0)), backgroundColor:'rgba(249,115,22,.7)', borderRadius:4}},
      ]
    }},
    options: {{
      responsive:true, plugins:{{legend:{{position:'top'}}}},
      scales:{{y:{{beginAtZero:true}},x:{{ticks:{{maxRotation:45}}}}}}
    }}
  }});

  // Level
  const levelOrder = ['Director','Head','Manager','Officer','Staff','Non-Officer','Other'];
  if (levelChart) levelChart.destroy();
  levelChart = new Chart(document.getElementById('levelChart'), {{
    type: 'doughnut',
    data: {{
      labels: levelOrder,
      datasets: [{{
        data: levelOrder.map(l => g.level_dist[l]||0),
        backgroundColor: ['#4f46e5','#3b82f6','#10b981','#f97316','#8b5cf6','#ec4899','#6b7280'],
        borderWidth: 2,
      }}]
    }},
    options: {{responsive:true, plugins:{{legend:{{position:'right'}}}}}}
  }});

  // Gender
  if (genderChart) genderChart.destroy();
  genderChart = new Chart(document.getElementById('genderChart'), {{
    type: 'doughnut',
    data: {{
      labels: ['Male','Female','Unknown'],
      datasets: [{{
        data: [g.male||0, g.female||0, (g.total-(g.male||0)-(g.female||0))],
        backgroundColor: ['#3b82f6','#ec4899','#9ca3af'],
        borderWidth: 2,
      }}]
    }},
    options: {{responsive:true, plugins:{{legend:{{position:'right'}}}}}}
  }});

  // PT headcount
  const ptLabels = pts.map(p => DATA.pt_short[p] || p.slice(0,12));
  if (ptChart) ptChart.destroy();
  ptChart = new Chart(document.getElementById('ptChart'), {{
    type: 'bar',
    data: {{
      labels: ptLabels,
      datasets: [
        {{label:'Active', data: pts.map(p => DATA.pt_stats[p]?.active||0), backgroundColor:'#10b981', borderRadius:4}},
        {{label:'Resigned (2026)', data: pts.map(p => DATA.pt_stats[p]?.resigned_period||0), backgroundColor:'#f97316', borderRadius:4}},
      ]
    }},
    options: {{
      responsive:true, plugins:{{legend:{{position:'top'}}}},
      scales:{{x:{{stacked:false}},y:{{beginAtZero:true}}}}
    }}
  }});

  // Top orgs
  if (orgChart) orgChart.destroy();
  const orgLabels = g.top_orgs.map(o => o[0]);
  const orgVals   = g.top_orgs.map(o => o[1]);
  orgChart = new Chart(document.getElementById('orgChart'), {{
    type: 'bar',
    data: {{
      labels: orgLabels,
      datasets: [{{
        label:'Karyawan',
        data: orgVals,
        backgroundColor: orgLabels.map((_,i) => `hsl(${{i*27}},65%,55%)`),
        borderRadius: 4,
      }}]
    }},
    options: {{
      indexAxis:'y', responsive:true,
      plugins:{{legend:{{display:false}}}},
      scales:{{x:{{beginAtZero:true}}}}
    }}
  }});

  // Employment status per PT (stacked)
  if (empStatusChart) empStatusChart.destroy();
  empStatusChart = new Chart(document.getElementById('empStatusChart'), {{
    type: 'bar',
    data: {{
      labels: ptLabels,
      datasets: [
        {{label:'Permanent', data: pts.map(p => DATA.pt_stats[p]?.permanent||0), backgroundColor:'#4f46e5', borderRadius:3}},
        {{label:'Probation', data: pts.map(p => DATA.pt_stats[p]?.probation||0), backgroundColor:'#f97316', borderRadius:3}},
        {{label:'Contract',  data: pts.map(p => DATA.pt_stats[p]?.contract||0),  backgroundColor:'#8b5cf6', borderRadius:3}},
        {{label:'Internship',data: pts.map(p => DATA.pt_stats[p]?.intern||0),    backgroundColor:'#10b981', borderRadius:3}},
      ]
    }},
    options: {{
      responsive:true,
      plugins:{{legend:{{position:'top'}}}},
      scales:{{x:{{stacked:true}},y:{{stacked:true,beginAtZero:true}}}}
    }}
  }});
}}

function buildPTGlobal(pt) {{
  const s = DATA.pt_stats[pt] || {{}};
  const emps = DATA.employees.filter(e => e.pt === pt);
  const jbm = {{}}, rbm = {{}};
  emps.forEach(e => {{
    if (e.join_date && e.join_date >= '2025-01') {{
      const k = e.join_date.slice(0,7); jbm[k] = (jbm[k]||0)+1;
    }}
    if (e.resign_date && e.resign_date >= '2026-01-01') {{
      const k = e.resign_date.slice(0,7); rbm[k] = (rbm[k]||0)+1;
    }}
  }});
  const orgMap = {{}};
  emps.forEach(e => {{ orgMap[e.org] = (orgMap[e.org]||0)+1; }});
  const top_orgs = Object.entries(orgMap).sort((a,b)=>b[1]-a[1]).slice(0,12);
  const lvl = s.level || {{}};
  return {{
    total: s.total||0, active: s.active||0, resigned_period: s.resigned_period||0,
    permanent: s.permanent||0, probation: s.probation||0, contract: s.contract||0, intern: s.intern||0,
    male: s.male||0, female: s.female||0,
    join_by_month: jbm, resign_by_month: rbm,
    level_dist: lvl, top_orgs,
  }};
}}

// ── Filter Dashboard ──────────────────────────────────────────────────────────
function filterDashboard() {{
  const pt = document.getElementById('pt-filter').value;
  const g  = pt === 'all' ? DATA.global : buildPTGlobal(pt);

  // Update stat cards
  document.getElementById('s-total').textContent    = g.total;
  document.getElementById('s-active').textContent   = g.active;
  document.getElementById('s-resigned').textContent = g.resigned_period;
  document.getElementById('s-permanent').textContent = g.permanent;

  // Show/hide PT cards
  document.querySelectorAll('#pt-cards .pt-card').forEach(c => {{
    c.style.display = (pt === 'all' || c.dataset.pt === pt) ? '' : 'none';
  }});

  document.getElementById('filter-count').textContent =
    `${{g.total}} karyawan · Jan 2026 – Oct 2026${{pt !== 'all' ? ' · '+( DATA.pt_short[pt]||pt) : ''}}`;

  initCharts(pt);
}}

// ── Filter Employees ──────────────────────────────────────────────────────────
function filterEmployees() {{
  const q      = document.getElementById('emp-search').value.toLowerCase();
  const ptF    = document.getElementById('emp-pt-filter').value;
  const statusF= document.getElementById('emp-status-filter').value;
  const typeF  = document.getElementById('emp-type-filter').value;

  let count = 0;
  document.querySelectorAll('#emp-tbody tr').forEach(row => {{
    const cells = row.querySelectorAll('td');
    const text  = Array.from(cells).map(c=>c.textContent).join(' ').toLowerCase();
    const pt    = row.dataset.pt    || '';
    const status= row.dataset.status || '';
    const empS  = row.dataset.empStatus || '';

    const ok = (!q || text.includes(q))
            && (!ptF    || pt === ptF)
            && (!statusF || status === statusF)
            && (!typeF   || empS === typeF);
    row.classList.toggle('hidden', !ok);
    if (ok) count++;
  }});
  document.getElementById('emp-count').textContent = count + ' karyawan';
}}

// ── Section Switch ────────────────────────────────────────────────────────────
function showSection(name, event) {{
  ['dashboard','employees','leave','payroll','recruitment','performance','it','ga'].forEach(s => {{
    document.getElementById('section-'+s)?.classList.remove('active');
  }});
  document.getElementById('section-'+name)?.classList.add('active');
  const titles = {{
    dashboard:'Dashboard', employees:'Employee Directory', leave:'Leave Management',
    payroll:'Payroll', recruitment:'Recruitment', performance:'Performance Reviews',
    it:'IT', ga:'General Affairs'
  }};
  document.getElementById('page-title').textContent = titles[name] || name;
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  if (event) event.currentTarget.classList.add('active');
  document.getElementById('filter-bar').style.display = name === 'dashboard' ? 'flex' : 'none';
}}

// ── Init ──────────────────────────────────────────────────────────────────────
window.addEventListener('load', () => {{
  initCharts('all');
}});
</script>
</body>
</html>'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Built index.html ({len(html):,} chars)')
