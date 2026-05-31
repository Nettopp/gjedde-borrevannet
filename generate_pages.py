#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import datetime

OUT = os.path.dirname(os.path.abspath(__file__))


def extend_date(iso):
    d = datetime.date.fromisoformat(iso)
    if d.weekday() in (4, 5):  # fredag=4, lørdag=5
        return (d + datetime.timedelta(days=1)).isoformat()
    return iso


def date_range_label(start_iso, end_iso):
    s = datetime.date.fromisoformat(start_iso)
    e = datetime.date.fromisoformat(end_iso)
    months = ['jan','feb','mar','apr','mai','jun','jul','aug','sep','okt','nov','des']
    if start_iso == end_iso:
        return f"{s.day}. {months[s.month - 1]}"
    return f"{s.day}.–{e.day}. {months[s.month - 1]}"


YEARS_RAW = [
    {"year": 2025, "start": "2025-05-23", "location": "Borrevannet"},
    {"year": 2024, "start": "2024-05-24", "location": "Borrevannet"},
    {"year": 2021, "start": "2021-05-22", "location": "Borrevannet"},
    {"year": 2020, "start": "2020-05-15", "location": "Borrevannet"},
    {"year": 2019, "start": "2019-05-25", "location": "Speiderhytta"},
    {"year": 2018, "start": "2018-05-26", "location": "Borrevannet"},
    {"year": 2017, "start": "2017-05-24", "location": "Borrevannet"},
]

for y in YEARS_RAW:
    y["end"]       = extend_date(y["start"])
    y["multiday"]  = y["start"] != y["end"]
    y["label"]     = date_range_label(y["start"], y["end"])
    s = datetime.date.fromisoformat(y["start"])
    e = datetime.date.fromisoformat(y["end"])
    months_no = ['januar','februar','mars','april','mai','juni','juli','august',
                 'september','oktober','november','desember']
    if not y["multiday"]:
        y["date_no"] = f"{s.day}. {months_no[s.month-1]} {s.year}"
    else:
        y["date_no"] = f"{s.day}.–{e.day}. {months_no[s.month-1]} {s.year}"


CSS = """\
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg: #0f1a14;
      --surface: #162010;
      --surface2: #1d2b1a;
      --border: #2e4028;
      --accent: #5a8f4a;
      --accent-light: #7ab868;
      --text: #d6e8cf;
      --text-muted: #7a9970;
      --heading: #e8f5e1;
      --link: #7ab868;
    }

    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      font-size: 16px;
      line-height: 1.7;
      min-height: 100vh;
    }

    nav {
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 0 1.5rem;
      display: flex;
      align-items: center;
      gap: 2rem;
      height: 54px;
      position: sticky;
      top: 0;
      z-index: 100;
    }

    nav .brand {
      font-weight: 700;
      font-size: 1rem;
      color: var(--accent-light);
      letter-spacing: 0.03em;
      text-decoration: none;
    }

    nav a {
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.9rem;
      padding: 0.25rem 0;
      border-bottom: 2px solid transparent;
      transition: color 0.15s, border-color 0.15s;
    }

    nav a:hover { color: var(--text); }
    nav a.active { color: var(--accent-light); border-bottom-color: var(--accent-light); }

    header {
      background: linear-gradient(160deg, #162b1a 0%, #0f1f13 100%);
      border-bottom: 1px solid var(--border);
      padding: 3.5rem 1.5rem 3rem;
      text-align: center;
    }

    header h1 {
      font-size: clamp(2rem, 5vw, 3rem);
      color: var(--heading);
      font-weight: 700;
      letter-spacing: -0.02em;
      margin-bottom: 0.6rem;
    }

    header p {
      color: var(--text-muted);
      font-size: 1.05rem;
      max-width: 520px;
      margin: 0 auto;
    }

    main {
      max-width: 820px;
      margin: 0 auto;
      padding: 2.5rem 1.5rem 4rem;
    }

    .back-link {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      color: var(--text-muted);
      font-size: 0.88rem;
      margin-bottom: 2rem;
      text-decoration: none;
    }

    .back-link:hover { color: var(--text); text-decoration: none; }

    .meta-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 0.8rem;
      margin-bottom: 1.5rem;
    }

    .meta-item {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 0.7rem 1rem;
    }

    .meta-item .label {
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      color: var(--text-muted);
      margin-bottom: 0.2rem;
    }

    .meta-item .value {
      color: var(--heading);
      font-weight: 600;
      font-size: 0.95rem;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin: 1rem 0 1.5rem;
      font-size: 0.93rem;
    }

    th {
      background: var(--surface2);
      color: var(--accent-light);
      font-weight: 600;
      text-align: left;
      padding: 0.6rem 0.8rem;
      border-bottom: 2px solid var(--border);
    }

    td {
      padding: 0.55rem 0.8rem;
      border-bottom: 1px solid var(--border);
      color: var(--text);
    }

    tr:last-child td { border-bottom: none; }
    tr:nth-child(even) td { background: rgba(255,255,255,0.02); }

    h3 {
      font-size: 1rem;
      color: var(--accent-light);
      font-weight: 600;
      margin: 1.5rem 0 0.6rem;
    }

    p { margin-bottom: 0.9rem; color: var(--text); }

    .not-logged {
      color: var(--text-muted);
      font-style: italic;
      font-size: 0.9rem;
    }

    a { color: var(--link); text-decoration: none; }
    a:hover { text-decoration: underline; }

    footer {
      text-align: center;
      padding: 2rem 1.5rem;
      color: var(--text-muted);
      font-size: 0.82rem;
      border-top: 1px solid var(--border);
    }

    .weather-widget {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1rem 1.4rem 1.2rem;
      margin-top: 0.8rem;
    }
    .wx-loading, .wx-error {
      color: var(--text-muted);
      font-size: 0.85rem;
      font-style: italic;
      padding: 0.4rem 0;
    }
    .wx-section { margin-bottom: 10px; }
    .wx-section-label {
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      color: var(--text-muted);
      margin-bottom: 4px;
    }
    .wx-source {
      font-size: 0.72rem;
      color: var(--text-muted);
      margin-top: 8px;
      text-align: right;
    }
    .wx-stats-wrap { overflow-x: auto; margin-top: 1.2rem; }
    .wx-stats-wrap table { font-size: 0.82rem; margin: 0; }
    .wx-stats-wrap th { font-size: 0.75rem; padding: 0.45rem 0.6rem; }
    .wx-stats-wrap td { padding: 0.4rem 0.6rem; }"""


# JS template — uses %%START%% and %%END%% as placeholders
JS_TEMPLATE = """\
(function () {
  var LAT = 59.4119, LON = 10.4677;
  var START = '%%START%%', END = '%%END%%';
  var MULTIDAY = START !== END;
  var GRID = 'rgba(46,64,40,0.55)', MUTED = '#7a9970', FG = '#d6e8cf';
  var NO_DAYS_S = ['s\\u00f8','ma','ti','on','to','fr','l\\u00f8'];
  var NO_DAYS_F = ['S\\u00f8ndag','Mandag','Tirsdag','Onsdag','Torsdag','Fredag','L\\u00f8rdag'];
  var NO_MON   = ['januar','februar','mars','april','mai','juni',
                  'juli','august','september','oktober','november','desember'];

  var TT = {
    backgroundColor: '#1d2b1a', borderColor: '#2e4028', borderWidth: 1,
    titleColor: '#e8f5e1', bodyColor: FG, padding: 8
  };

  function makeLabel(t) {
    var d = new Date(t);
    var hh = String(d.getHours()).padStart(2, '0') + ':00';
    return MULTIDAY ? NO_DAYS_S[d.getDay()] + '\\u00a0' + hh : hh;
  }

  function avg(arr) {
    return arr.length ? arr.reduce(function (a, b) { return a + b; }, 0) / arr.length : null;
  }

  function buildStats(h) {
    var byDay = {};
    h.time.forEach(function (t, i) {
      var day = t.slice(0, 10);
      if (!byDay[day]) byDay[day] = { temp: [], precip: [], wind: [], cloud: [] };
      if (h.temperature_2m[i] !== null) byDay[day].temp.push(h.temperature_2m[i]);
      if (h.precipitation[i]  !== null) byDay[day].precip.push(h.precipitation[i]);
      if (h.windspeed_10m[i]  !== null) byDay[day].wind.push(h.windspeed_10m[i]);
      if (h.cloudcover[i]     !== null) byDay[day].cloud.push(h.cloudcover[i]);
    });

    function f1(v) { return v !== null ? v.toFixed(1) : '\\u2014'; }
    function f0(v) { return v !== null ? Math.round(v).toString() : '\\u2014'; }

    var rows = Object.entries(byDay).map(function (entry) {
      var day = entry[0], d = entry[1];
      var dt = new Date(day + 'T12:00:00');
      var label = NO_DAYS_F[dt.getDay()] + ' ' + dt.getDate() + '.\\u00a0' + NO_MON[dt.getMonth()];
      var tMax  = d.temp.length  ? Math.max.apply(null, d.temp)  : null;
      var tMin  = d.temp.length  ? Math.min.apply(null, d.temp)  : null;
      var tAvg  = avg(d.temp);
      var rain  = d.precip.length ? d.precip.reduce(function (a, b) { return a + b; }, 0) : null;
      var wMax  = d.wind.length  ? Math.max.apply(null, d.wind)  : null;
      var cAvg  = avg(d.cloud);
      var sunH  = d.cloud.filter(function (c) { return c < 30; }).length;
      return '<tr><td>' + label + '</td>'
        + '<td>' + f1(tMax) + '</td>'
        + '<td>' + f1(tMin) + '</td>'
        + '<td>' + f1(tAvg) + '</td>'
        + '<td>' + f1(rain) + '</td>'
        + '<td>' + f1(wMax) + '</td>'
        + '<td>' + f0(cAvg) + '\\u00a0%</td>'
        + '<td>' + sunH + '</td></tr>';
    });

    return '<div class="wx-stats-wrap"><table>'
      + '<thead><tr>'
      + '<th>Dag</th>'
      + '<th>Maks\\u00a0\\u00b0C</th>'
      + '<th>Min\\u00a0\\u00b0C</th>'
      + '<th>Gj.snitt\\u00a0\\u00b0C</th>'
      + '<th>Nedb\\u00f8r\\u00a0mm</th>'
      + '<th>Maks\\u00a0vind\\u00a0m/s</th>'
      + '<th>Skydekke</th>'
      + '<th>Soltimer\\u00b9</th>'
      + '</tr></thead>'
      + '<tbody>' + rows.join('') + '</tbody>'
      + '</table></div>'
      + '<p class="wx-source" style="margin-top:4px">'
      + '\\u00b9 Timer med skydekke under 30\\u00a0%'
      + ' \\u00b7 Kilde: Open-Meteo / ERA5 \\u00b7 Borrevannet, Horten'
      + '</p>';
  }

  function buildCharts(data) {
    var h      = data.hourly;
    var labels = h.time.map(makeLabel);

    new Chart(document.getElementById('wx-temp'), {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Temperatur (\\u00b0C)',
            data: h.temperature_2m,
            borderColor: '#7ab868',
            backgroundColor: 'rgba(122,184,104,0.13)',
            borderWidth: 2, pointRadius: 2, pointHoverRadius: 4,
            fill: true, tension: 0.35, yAxisID: 'yT', order: 1
          },
          {
            label: 'Skydekke (%)',
            data: h.cloudcover,
            borderColor: 'rgba(160,165,185,0.35)',
            backgroundColor: 'rgba(120,130,155,0.1)',
            borderWidth: 1, pointRadius: 0,
            fill: true, tension: 0.3, yAxisID: 'yC', order: 2
          }
        ]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: FG, boxWidth: 12, font: { size: 11 } } },
          tooltip: TT
        },
        scales: {
          x: { grid: { color: GRID }, ticks: { color: MUTED, maxTicksLimit: 12, font: { size: 10 } } },
          yT: {
            type: 'linear', position: 'left',
            title: { display: true, text: '\\u00b0C', color: MUTED, font: { size: 11 } },
            grid: { color: GRID }, ticks: { color: MUTED, font: { size: 10 } }
          },
          yC: {
            type: 'linear', position: 'right', min: 0, max: 100,
            title: { display: true, text: 'skyer\\u00a0%', color: MUTED, font: { size: 11 } },
            grid: { display: false },
            ticks: { color: MUTED, font: { size: 10 }, stepSize: 25,
                     callback: function (v) { return v + '%'; } }
          }
        }
      }
    });

    new Chart(document.getElementById('wx-wind'), {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Vind (m/s)',
            data: h.windspeed_10m,
            type: 'line',
            borderColor: '#5599dd',
            backgroundColor: 'rgba(85,153,221,0.08)',
            borderWidth: 2, pointRadius: 2, pointHoverRadius: 4,
            fill: false, tension: 0.3, yAxisID: 'yW', order: 1
          },
          {
            label: 'Nedb\\u00f8r (mm)',
            data: h.precipitation,
            type: 'bar',
            backgroundColor: 'rgba(85,153,221,0.5)',
            borderColor: 'rgba(85,153,221,0.75)',
            borderWidth: 0, yAxisID: 'yP', order: 2
          }
        ]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: FG, boxWidth: 12, font: { size: 11 } } },
          tooltip: TT
        },
        scales: {
          x: { grid: { color: GRID }, ticks: { color: MUTED, maxTicksLimit: 12, font: { size: 10 } } },
          yW: {
            type: 'linear', position: 'left', min: 0,
            title: { display: true, text: 'm/s', color: MUTED, font: { size: 11 } },
            grid: { color: GRID }, ticks: { color: MUTED, font: { size: 10 } }
          },
          yP: {
            type: 'linear', position: 'right', min: 0,
            title: { display: true, text: 'mm', color: MUTED, font: { size: 11 } },
            grid: { display: false }, ticks: { color: MUTED, font: { size: 10 } }
          }
        }
      }
    });

    document.getElementById('wx-stats').innerHTML = buildStats(h);
    document.getElementById('wx-loading').style.display = 'none';
    document.getElementById('wx-content').style.display  = 'block';
  }

  async function loadWeather() {
    var url = 'https://archive-api.open-meteo.com/v1/archive'
      + '?latitude=' + LAT + '&longitude=' + LON
      + '&start_date=' + START + '&end_date=' + END
      + '&hourly=temperature_2m,precipitation,windspeed_10m,cloudcover'
      + '&timezone=Europe%2FOslo&wind_speed_unit=ms';
    var resp = await fetch(url);
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    var data = await resp.json();
    if (data.error) throw new Error(data.reason || 'API-feil');
    return data;
  }

  loadWeather()
    .then(buildCharts)
    .catch(function (e) {
      document.getElementById('wx-loading').style.display = 'none';
      var err = document.getElementById('wx-error');
      err.textContent = 'Kunne ikke hente v\\u00e6rdata: ' + e.message;
      err.style.display = 'block';
    });
})();"""


def make_page(y):
    year      = y["year"]
    start     = y["start"]
    end       = y["end"]
    label     = y["label"]       # e.g. "23.–24. mai"
    date_no   = y["date_no"]     # e.g. "23.–24. mai 2025"
    location  = y["location"]
    js = JS_TEMPLATE.replace("%%START%%", start).replace("%%END%%", end)

    return f"""<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Gjeddefestivalen {year} &mdash; {location}</title>
  <style>
{CSS}
  </style>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
</head>
<body>

<nav>
  <a href="index.html" class="brand">Borrevannet</a>
  <a href="index.html">Om vannet</a>
  <a href="gjeddefiske.html">Gjeddefiske &amp; festival</a>
  <a href="festivallogg.html" class="active">Festivallogg</a>
</nav>

<header>
  <h1>Gjeddefestivalen {year}</h1>
  <p>{label} &nbsp;&middot;&nbsp; {location}</p>
</header>

<main>

  <a href="festivallogg.html" class="back-link">&#8592; Alle festivaler</a>

  <div class="meta-grid">
    <div class="meta-item">
      <div class="label">Dato</div>
      <div class="value">{date_no}</div>
    </div>
    <div class="meta-item">
      <div class="label">Sted</div>
      <div class="value">{location}</div>
    </div>
  </div>

  <h3>Timevis v&aelig;r &mdash; {label}</h3>
  <div class="weather-widget">
    <p class="wx-loading" id="wx-loading">Henter historiske v&aelig;rdata fra Borrevannet&hellip;</p>
    <p class="wx-error" id="wx-error" style="display:none"></p>
    <div id="wx-content" style="display:none">
      <div class="wx-section">
        <div class="wx-section-label">Temperatur &amp; skydekke</div>
        <div style="height:150px;position:relative"><canvas id="wx-temp"></canvas></div>
      </div>
      <div class="wx-section">
        <div class="wx-section-label">Vind &amp; nedb&oslash;r</div>
        <div style="height:100px;position:relative"><canvas id="wx-wind"></canvas></div>
      </div>
      <div id="wx-stats"></div>
    </div>
  </div>

  <h3>Fangst</h3>
  <p class="not-logged">Ikke loggf&oslash;rt for dette &aring;ret.</p>

  <h3>Historier og hendelser</h3>
  <p class="not-logged">Ikke loggf&oslash;rt for dette &aring;ret.</p>

</main>

<footer>
  Borrevannet, Horten &mdash; Vestfold
</footer>

<script>
{js}
</script>

</body>
</html>
"""


for y in YEARS_RAW:
    fname = f"festivallogg-{y['year']}.html"
    path  = os.path.join(OUT, fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(make_page(y))
    end_info = f" -> {y['end']}" if y["multiday"] else ""
    print(f"  {fname}  ({y['start']}{end_info})")

print("Ferdig.")
