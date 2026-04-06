import json
from pathlib import Path


def _deduplicate(data: list) -> list:
    seen = set()
    result = []
    for e in data:
        key = (e["url"], e["page"])
        if key not in seen:
            seen.add(key)
            result.append(e)
    return result


def _screenshot_section(screenshots_dir: Path) -> str:
    if not screenshots_dir.exists():
        return ""

    book_shots = sorted(screenshots_dir.glob("*.png"))
    if not book_shots:
        return ""

    items = ""
    for shot in book_shots:
        title = shot.stem.replace("_", " ").replace("  ", " ").strip()
        src = f"screenshots/{shot.name}"
        items += f"""
        <div class="gallery-item" onclick="openLightbox('{src}', '{title}')">
          <img src="{src}" alt="{title}" loading="lazy">
          <div class="gallery-label">{title}</div>
        </div>"""

    return f"""
  <section>
    <h2>Book Page Screenshots ({len(book_shots)})</h2>
    <div class="gallery-grid">
      {items}
    </div>
  </section>

  <!-- Lightbox -->
  <div id="lightbox" onclick="closeLightbox()">
    <div class="lb-inner" onclick="event.stopPropagation()">
      <button class="lb-close" onclick="closeLightbox()">&#x2715;</button>
      <img id="lb-img" src="" alt="">
      <div id="lb-caption"></div>
    </div>
  </div>"""


def generate_report(results_path: Path) -> None:
    report_json = results_path / "performance_report.json"
    if not report_json.exists():
        return

    with open(report_json) as f:
        raw = json.load(f)

    if not raw:
        return

    data = _deduplicate(raw)
    duplicates_removed = len(raw) - len(data)

    total = len(data)
    passed = sum(1 for e in data if e["is_within_threshold"])
    failed = total - passed
    pass_rate = round(passed / total * 100) if total else 0
    avg_load = round(sum(e["load_time_ms"] for e in data) / total) if total else 0
    avg_fp = round(sum(e["first_paint_ms"] for e in data) / total) if total else 0
    avg_dcl = round(sum(e["dom_content_loaded_ms"] for e in data) / total) if total else 0

    page_types: dict[str, list] = {}
    for e in data:
        page_types.setdefault(e["page"], []).append(e)

    timestamp = results_path.name

    bar_labels = json.dumps([f"{e['page'].replace('_page', '')} #{i + 1}" for i, e in enumerate(data)])
    bar_load = json.dumps([e["load_time_ms"] for e in data])
    bar_fp = json.dumps([e["first_paint_ms"] for e in data])
    bar_dcl = json.dumps([e["dom_content_loaded_ms"] for e in data])
    bar_colors = json.dumps(["rgba(34,197,94,0.85)" if e["is_within_threshold"] else "rgba(239,68,68,0.85)" for e in data])
    bar_border = json.dumps(["#22c55e" if e["is_within_threshold"] else "#ef4444" for e in data])

    table_rows = ""
    for i, e in enumerate(data):
        status = "pass" if e["is_within_threshold"] else "fail"
        label = "PASS" if e["is_within_threshold"] else "FAIL"
        short_url = e["url"].replace("https://openlibrary.org", "...")
        table_rows += f"""
        <tr class="{status}-row" data-load="{e['load_time_ms']}" data-fp="{e['first_paint_ms']}" data-dcl="{e['dom_content_loaded_ms']}">
            <td class="num">{i + 1}</td>
            <td><span class="page-tag">{e['page'].replace('_', ' ')}</span></td>
            <td class="url-cell"><a href="{e['url']}" target="_blank" title="{e['url']}">{short_url}</a></td>
            <td class="num">{e['first_paint_ms']}</td>
            <td class="num">{e['dom_content_loaded_ms']}</td>
            <td class="num">{e['load_time_ms']}</td>
            <td><span class="badge {status}">{label}</span></td>
        </tr>"""

    page_type_cards = ""
    for pt, entries in page_types.items():
        pt_total = len(entries)
        pt_passed = sum(1 for e in entries if e["is_within_threshold"])
        pt_avg_load = round(sum(e["load_time_ms"] for e in entries) / pt_total)
        pt_avg_fp = round(sum(e["first_paint_ms"] for e in entries) / pt_total)
        pt_rate = round(pt_passed / pt_total * 100)
        rate_class = "good" if pt_rate >= 50 else "bad"
        page_type_cards += f"""
        <div class="pt-card">
            <div class="pt-name">{pt.replace('_', ' ').title()}</div>
            <div class="pt-rate {rate_class}">{pt_rate}%</div>
            <div class="pt-meta">
                <span>{pt_passed}/{pt_total} passed</span>
                <span>Avg load <strong>{pt_avg_load}ms</strong></span>
                <span>Avg FP <strong>{pt_avg_fp}ms</strong></span>
            </div>
        </div>"""

    dedup_notice = f'<span class="dedup-note">{duplicates_removed} duplicate entries removed</span>' if duplicates_removed else ""
    screenshot_html = _screenshot_section(results_path / "screenshots")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Performance Report -- {timestamp}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --bg: #0f1117;
    --surface: #1a1d27;
    --surface2: #22263a;
    --border: #2e3349;
    --text: #e2e8f0;
    --muted: #94a3b8;
    --accent: #6366f1;
    --green: #22c55e;
    --red: #ef4444;
    --yellow: #f59e0b;
  }}
  body {{ background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; min-height: 100vh; }}

  /* ── Header ── */
  .header {{
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #1e1b4b 100%);
    padding: 2.5rem 3rem 2rem;
    border-bottom: 1px solid var(--border);
    display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 1rem;
  }}
  .header-left h1 {{ font-size: 1.75rem; font-weight: 700; letter-spacing: -.5px; }}
  .header-left h1 span {{ color: #a5b4fc; }}
  .header-left p {{ color: var(--muted); margin-top: .35rem; font-size: .875rem; }}
  .dedup-note {{
    display: inline-block; margin-left: .75rem; padding: .15rem .6rem;
    background: rgba(245,158,11,.15); border: 1px solid rgba(245,158,11,.3);
    color: var(--yellow); border-radius: 99px; font-size: .7rem; font-weight: 600;
  }}
  .pass-rate-big {{ text-align: right; }}
  .pass-rate-big .rate {{ font-size: 4rem; font-weight: 800; line-height: 1;
    background: linear-gradient(135deg, var(--green), #86efac);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
  .pass-rate-big .rate.bad {{ background: linear-gradient(135deg, var(--red), #fca5a5);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
  .pass-rate-big .rate-label {{ color: var(--muted); font-size: .8rem; text-transform: uppercase; letter-spacing: 1px; margin-top: .2rem; }}

  /* ── Layout ── */
  .container {{ max-width: 1400px; margin: 0 auto; padding: 2rem 3rem; }}
  section {{ margin-bottom: 2.5rem; }}
  h2 {{ font-size: 1rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: var(--muted); margin-bottom: 1.25rem; }}

  /* ── KPI Cards ── */
  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }}
  .kpi-card {{
    background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
    padding: 1.25rem 1.5rem; position: relative; overflow: hidden;
    transition: transform .2s, box-shadow .2s;
  }}
  .kpi-card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0,0,0,.4); }}
  .kpi-card::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: var(--accent);
  }}
  .kpi-card.green::before {{ background: var(--green); }}
  .kpi-card.red::before {{ background: var(--red); }}
  .kpi-card.yellow::before {{ background: var(--yellow); }}
  .kpi-label {{ font-size: .75rem; color: var(--muted); text-transform: uppercase; letter-spacing: .5px; }}
  .kpi-value {{ font-size: 2.25rem; font-weight: 700; margin-top: .35rem; line-height: 1; }}
  .kpi-unit {{ font-size: .9rem; font-weight: 400; color: var(--muted); margin-left: 2px; }}
  .kpi-sub {{ font-size: .75rem; color: var(--muted); margin-top: .4rem; }}

  /* ── Charts row ── */
  .charts-row {{ display: grid; grid-template-columns: 280px 1fr; gap: 1.5rem; align-items: start; }}
  .chart-card {{
    background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem;
  }}
  .chart-card h3 {{ font-size: .8rem; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; color: var(--muted); margin-bottom: 1rem; }}
  .donut-wrap {{ position: relative; }}
  .donut-center {{
    position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
    text-align: center; pointer-events: none;
  }}
  .donut-center .dc-val {{ font-size: 1.8rem; font-weight: 700; }}
  .donut-center .dc-label {{ font-size: .65rem; color: var(--muted); text-transform: uppercase; letter-spacing: .5px; }}

  /* ── Page type cards ── */
  .pt-grid {{ display: flex; gap: 1rem; flex-wrap: wrap; }}
  .pt-card {{
    background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
    padding: 1.25rem 1.5rem; flex: 1; min-width: 220px;
  }}
  .pt-name {{ font-size: .85rem; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: .5px; }}
  .pt-rate {{ font-size: 2.5rem; font-weight: 800; margin: .4rem 0; }}
  .pt-rate.good {{ color: var(--green); }}
  .pt-rate.bad {{ color: var(--red); }}
  .pt-meta {{ display: flex; gap: 1rem; flex-wrap: wrap; font-size: .8rem; color: var(--muted); }}
  .pt-meta strong {{ color: var(--text); }}

  /* ── Screenshot gallery ── */
  .gallery-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
  }}
  .gallery-item {{
    background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
    overflow: hidden; cursor: pointer; transition: transform .2s, box-shadow .2s;
  }}
  .gallery-item:hover {{ transform: translateY(-3px); box-shadow: 0 8px 30px rgba(0,0,0,.5); border-color: var(--accent); }}
  .gallery-item img {{ width: 100%; height: 130px; object-fit: cover; object-position: top; display: block; }}
  .gallery-label {{
    padding: .5rem .75rem; font-size: .7rem; color: var(--muted);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    border-top: 1px solid var(--border);
  }}

  /* ── Lightbox ── */
  #lightbox {{
    display: none; position: fixed; inset: 0; background: rgba(0,0,0,.85);
    z-index: 1000; align-items: center; justify-content: center;
    backdrop-filter: blur(4px);
  }}
  #lightbox.open {{ display: flex; }}
  .lb-inner {{
    position: relative; max-width: 90vw; max-height: 90vh;
    background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
    overflow: hidden; display: flex; flex-direction: column;
  }}
  .lb-inner img {{ max-width: 90vw; max-height: 80vh; object-fit: contain; display: block; }}
  #lb-caption {{ padding: .75rem 1rem; font-size: .8rem; color: var(--muted); text-align: center; }}
  .lb-close {{
    position: absolute; top: .75rem; right: .75rem;
    background: rgba(0,0,0,.6); border: 1px solid var(--border); color: var(--text);
    border-radius: 50%; width: 2rem; height: 2rem; cursor: pointer;
    font-size: 1rem; display: flex; align-items: center; justify-content: center;
    transition: background .15s;
  }}
  .lb-close:hover {{ background: var(--red); border-color: var(--red); }}

  /* ── Table ── */
  .table-wrap {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }}
  table {{ width: 100%; border-collapse: collapse; font-size: .875rem; }}
  thead {{ background: var(--surface2); }}
  th {{
    padding: .9rem 1rem; text-align: left; font-size: .75rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: .5px; color: var(--muted);
    cursor: pointer; user-select: none; white-space: nowrap; transition: color .15s;
  }}
  th:hover {{ color: var(--text); }}
  th.sorted {{ color: var(--accent); }}
  th .sort-icon {{ margin-left: .3rem; opacity: .4; }}
  th.sorted .sort-icon {{ opacity: 1; }}
  td {{ padding: .8rem 1rem; border-top: 1px solid var(--border); vertical-align: middle; }}
  tr.pass-row:hover {{ background: rgba(34,197,94,.05); }}
  tr.fail-row:hover {{ background: rgba(239,68,68,.05); }}
  .num {{ font-variant-numeric: tabular-nums; text-align: right; color: var(--muted); }}
  td.num {{ color: var(--text); }}
  .url-cell a {{ color: #818cf8; text-decoration: none; font-size: .8rem; }}
  .url-cell a:hover {{ color: #a5b4fc; text-decoration: underline; }}
  .page-tag {{
    display: inline-block; padding: .2rem .6rem; border-radius: 99px;
    background: var(--surface2); border: 1px solid var(--border);
    font-size: .72rem; font-weight: 600; color: var(--muted); white-space: nowrap;
  }}
  .badge {{
    display: inline-block; padding: .25rem .7rem; border-radius: 99px;
    font-size: .72rem; font-weight: 700; letter-spacing: .5px;
  }}
  .badge.pass {{ background: rgba(34,197,94,.15); color: var(--green); border: 1px solid rgba(34,197,94,.3); }}
  .badge.fail {{ background: rgba(239,68,68,.15); color: var(--red); border: 1px solid rgba(239,68,68,.3); }}

  /* ── Footer ── */
  footer {{ text-align: center; color: var(--muted); font-size: .75rem; padding: 2rem 1rem; border-top: 1px solid var(--border); }}

  @media (max-width: 900px) {{
    .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .charts-row {{ grid-template-columns: 1fr; }}
    .container {{ padding: 1.5rem; }}
    .header {{ padding: 1.5rem; }}
  }}
</style>
</head>
<body>

<header class="header">
  <div class="header-left">
    <h1>Performance <span>Report</span></h1>
    <p>Run <code>{timestamp}</code> &nbsp;&#183;&nbsp; {total} pages measured &nbsp;&#183;&nbsp; openlibrary.org {dedup_notice}</p>
  </div>
  <div class="pass-rate-big">
    <div class="rate {'bad' if pass_rate < 50 else ''}">{pass_rate}%</div>
    <div class="rate-label">Pass Rate</div>
  </div>
</header>

<div class="container">

  <!-- KPI Cards -->
  <section>
    <h2>Summary</h2>
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Total Pages</div>
        <div class="kpi-value">{total}</div>
        <div class="kpi-sub">across {len(page_types)} page type(s)</div>
      </div>
      <div class="kpi-card green">
        <div class="kpi-label">Passed</div>
        <div class="kpi-value" style="color:var(--green)">{passed}</div>
        <div class="kpi-sub">within threshold</div>
      </div>
      <div class="kpi-card red">
        <div class="kpi-label">Failed</div>
        <div class="kpi-value" style="color:var(--red)">{failed}</div>
        <div class="kpi-sub">exceeded threshold</div>
      </div>
      <div class="kpi-card yellow">
        <div class="kpi-label">Avg Load Time</div>
        <div class="kpi-value">{avg_load}<span class="kpi-unit">ms</span></div>
        <div class="kpi-sub">FP avg {avg_fp}ms &nbsp;&#183;&nbsp; DCL avg {avg_dcl}ms</div>
      </div>
    </div>
  </section>

  <!-- Charts -->
  <section>
    <h2>Load Time Breakdown</h2>
    <div class="charts-row">
      <div class="chart-card">
        <h3>Pass / Fail</h3>
        <div class="donut-wrap">
          <canvas id="donutChart" height="220"></canvas>
          <div class="donut-center">
            <div class="dc-val">{pass_rate}%</div>
            <div class="dc-label">Pass Rate</div>
          </div>
        </div>
      </div>
      <div class="chart-card">
        <h3>Load Time per Page (ms)</h3>
        <canvas id="barChart" height="180"></canvas>
      </div>
    </div>
  </section>

  <!-- Page Type Breakdown -->
  <section>
    <h2>By Page Type</h2>
    <div class="pt-grid">
      {page_type_cards}
    </div>
  </section>

  {screenshot_html}

  <!-- Table -->
  <section>
    <h2>All Measurements</h2>
    <div class="table-wrap">
      <table id="resultsTable">
        <thead>
          <tr>
            <th class="num">#</th>
            <th>Page Type</th>
            <th>URL</th>
            <th class="num" data-col="fp">First Paint <span class="sort-icon">&#8597;</span></th>
            <th class="num" data-col="dcl">DOM Loaded <span class="sort-icon">&#8597;</span></th>
            <th class="num" data-col="load">Load Time <span class="sort-icon">&#8597;</span></th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {table_rows}
        </tbody>
      </table>
    </div>
  </section>

</div>

<footer>
  Generated by openLibraryCrawler -- {timestamp}
</footer>

<script>
  new Chart(document.getElementById('donutChart'), {{
    type: 'doughnut',
    data: {{
      labels: ['Passed', 'Failed'],
      datasets: [{{ data: [{passed}, {failed}], backgroundColor: ['#22c55e', '#ef4444'], borderColor: ['#166534', '#991b1b'], borderWidth: 2 }}]
    }},
    options: {{
      cutout: '70%',
      plugins: {{
        legend: {{ position: 'bottom', labels: {{ color: '#94a3b8', font: {{ size: 12 }} }} }},
        tooltip: {{ callbacks: {{ label: ctx => ' ' + ctx.label + ': ' + ctx.parsed }} }}
      }},
      animation: {{ animateRotate: true, duration: 800 }}
    }}
  }});

  new Chart(document.getElementById('barChart'), {{
    type: 'bar',
    data: {{
      labels: {bar_labels},
      datasets: [
        {{ label: 'Load Time', data: {bar_load}, backgroundColor: {bar_colors}, borderColor: {bar_border}, borderWidth: 1.5, borderRadius: 4, order: 1 }},
        {{ label: 'First Paint', data: {bar_fp}, backgroundColor: 'rgba(99,102,241,0.5)', borderColor: '#6366f1', borderWidth: 1.5, borderRadius: 4, order: 2 }},
        {{ label: 'DOM Loaded', data: {bar_dcl}, backgroundColor: 'rgba(245,158,11,0.4)', borderColor: '#f59e0b', borderWidth: 1.5, borderRadius: 4, order: 3 }}
      ]
    }},
    options: {{
      responsive: true,
      plugins: {{
        legend: {{ labels: {{ color: '#94a3b8', font: {{ size: 11 }} }} }},
        tooltip: {{ callbacks: {{ label: ctx => ' ' + ctx.dataset.label + ': ' + ctx.parsed.y + 'ms' }} }}
      }},
      scales: {{
        x: {{ ticks: {{ color: '#64748b', font: {{ size: 10 }}, maxRotation: 45 }}, grid: {{ color: '#1e2235' }} }},
        y: {{ ticks: {{ color: '#64748b', callback: v => v + 'ms' }}, grid: {{ color: '#1e2235' }} }}
      }},
      animation: {{ duration: 800 }}
    }}
  }});

  let sortCol = null, sortAsc = true;
  document.querySelectorAll('th[data-col]').forEach(th => {{
    th.addEventListener('click', () => {{
      const col = th.dataset.col;
      if (sortCol === col) sortAsc = !sortAsc; else {{ sortCol = col; sortAsc = true; }}
      document.querySelectorAll('th[data-col]').forEach(t => t.classList.remove('sorted'));
      th.classList.add('sorted');
      th.querySelector('.sort-icon').textContent = sortAsc ? '\u2191' : '\u2193';
      const tbody = document.querySelector('#resultsTable tbody');
      const rows = [...tbody.querySelectorAll('tr')];
      const attr = col === 'fp' ? 'data-fp' : col === 'dcl' ? 'data-dcl' : 'data-load';
      rows.sort((a, b) => (parseInt(a.getAttribute(attr)) - parseInt(b.getAttribute(attr))) * (sortAsc ? 1 : -1));
      rows.forEach(r => tbody.appendChild(r));
    }});
  }});

  function openLightbox(src, caption) {{
    document.getElementById('lb-img').src = src;
    document.getElementById('lb-caption').textContent = caption;
    document.getElementById('lightbox').classList.add('open');
  }}
  function closeLightbox() {{
    document.getElementById('lightbox').classList.remove('open');
    document.getElementById('lb-img').src = '';
  }}
  document.addEventListener('keydown', e => {{ if (e.key === 'Escape') closeLightbox(); }});
</script>
</body>
</html>"""

    out = results_path / "report.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\033[92m[REPORT]\033[0m HTML report saved: {out}")
