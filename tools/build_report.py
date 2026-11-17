#!/usr/bin/env python3
"""Build the final report (HTML, PDF, DOCX) without pandoc.

Run from the project root (PowerShell):
    py tools\\build_report.py            # final build (refuses open placeholders)
    py tools\\build_report.py --draft    # allows placeholders
Steps: figures as SVG from the registers and evidence -> PNG (Edge headless screenshot)
-> Markdown chapters to one HTML file with a table of contents -> PDF (Edge headless print)
-> DOCX (Microsoft Word via PowerShell COM). Outputs in 06-report/build/.
Standard library only; needs Microsoft Edge and Microsoft Word (already installed).
"""
import csv
import html
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REP = ROOT / "06-report"
FIG = REP / "figures"
OUT = REP / "build"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
NAME = "ShopNova-threat-management-report"
CHAPTERS = ["00-executive-summary.md", "01-introduction-and-scope.md", "02-governance.md", "03-risk-management.md",
            "04-vulnerability-management.md", "05-incident-response.md", "06-integration.md",
            "07-limitations.md", "08-conclusion.md", "90-appendix-evidence.md", "99-references.md"]
TITLE_FIELDS = ("University", "Course name", "Lecturer", "Matriculation number", "Submission date")
PLACEHOLDER = re.compile(r"GREENBONE_STATUS|\[Your name")
C = {"bg": "#ffffff", "fg": "#1b2230", "muted": "#5d6676", "line": "#c9ced8", "accent": "#2f5d8a",
     "L": "#cfe5cf", "M": "#f5e3b5", "H": "#f3c4a8", "C": "#e59a8c"}


def rows(rel):
    with (ROOT / rel).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def esc(t):
    return html.escape(str(t), quote=True)


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="Segoe UI, Arial, sans-serif"><rect width="{w}" height="{h}" fill="{C["bg"]}"/>{body}</svg>')


# ---------------------------------------------------------------- figures
def fig_dataflow():
    text = (ROOT / "00-scope-and-setup/data-flow.mmd").read_text(encoding="utf-8")
    nodes = {k: lab for k, lab in re.findall(r"(\w+)[\[\(]+\(?([^\]\)]+)\)?[\]\)]+", text)}
    edges = re.findall(r"(\w+)(?:[\[\(][^\]\)]*[\]\)]+\]?)?\s*-->\s*(?:\|\"?([^|\"]*)\"?\|)?\s*(\w+)", text)
    pos = {"C": (110, 200), "W": (390, 200), "P": (690, 60), "L": (930, 150), "M": (930, 250),
           "D": (690, 380), "B": (930, 380), "ADM": (110, 380), "S": (390, 500)}
    bw, bh = 190, 52
    labels = []
    body = ['<defs><marker id="a" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">'
            f'<path d="M0,0 L10,4 L0,8 z" fill="{C["muted"]}"/></marker></defs>']
    for a, label, b in edges:
        if a not in pos or b not in pos:
            continue
        (x1, y1), (x2, y2) = pos[a], pos[b]
        dx, dy = x2 - x1, y2 - y1
        sx = x1 + (bw / 2 if dx > 0 else -bw / 2 if dx < 0 else 0)
        ex = x2 - (bw / 2 if dx > 0 else -bw / 2 if dx < 0 else 0)
        sy, ey = (y1, y2) if dx else (y1 + (bh / 2 if dy > 0 else -bh / 2), y2 - (bh / 2 if dy > 0 else -bh / 2))
        body.append(f'<line x1="{sx}" y1="{sy}" x2="{ex}" y2="{ey}" stroke="{C["muted"]}" stroke-width="1.6" marker-end="url(#a)"/>')
        if label:
            lx, ly, tw = (sx + ex) / 2, (sy + ey) / 2, 6.6 * len(label) + 10
            labels.append(f'<rect x="{lx - tw / 2}" y="{ly - 11}" width="{tw}" height="18" rx="3" fill="#ffffff" '
                          f'stroke="{C["line"]}" stroke-width="0.8"/><text x="{lx}" y="{ly + 3}" font-size="12" '
                          f'fill="{C["accent"]}" text-anchor="middle">{esc(label)}</text>')
    for k, (x, y) in pos.items():
        lab = nodes.get(k, k).strip("()[] ")
        store = k in ("D", "B")
        body.append(f'<rect x="{x - bw / 2}" y="{y - bh / 2}" width="{bw}" height="{bh}" rx="{18 if store else 6}" '
                    f'fill="#eef3f8" stroke="{C["accent"]}" stroke-width="1.4"/>')
        body.append(f'<text x="{x}" y="{y + 5}" font-size="14" fill="{C["fg"]}" text-anchor="middle">{esc(lab)}</text>')
    return svg(1040, 550, "".join(body + labels))


def heat_grid(risks, prefix, ox, oy, title):
    cell, out = 74, []
    out.append(f'<text x="{ox + 2.5 * cell}" y="{oy - 30}" font-size="16" font-weight="600" fill="{C["fg"]}" text-anchor="middle">{esc(title)}</text>')
    cells = {}
    for r in risks:
        cells.setdefault((int(r[f"{prefix}_likelihood"]), int(r[f"{prefix}_impact"])), []).append(r["risk_id"])
    for li in range(5, 0, -1):
        for im in range(1, 6):
            s = li * im
            band = "L" if s <= 4 else "M" if s <= 9 else "H" if s <= 16 else "C"
            x, y = ox + (im - 1) * cell, oy + (5 - li) * cell
            out.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{C[band]}" stroke="#ffffff" stroke-width="2"/>')
            ids = sorted(cells.get((li, im), []))
            for i, rid in enumerate(ids):
                out.append(f'<text x="{x + cell / 2}" y="{y + 20 + i * 15}" font-size="12.5" fill="{C["fg"]}" text-anchor="middle">{rid}</text>')
    for i in range(1, 6):
        out.append(f'<text x="{ox + (i - 0.5) * cell}" y="{oy + 5 * cell + 18}" font-size="12" fill="{C["muted"]}" text-anchor="middle">{i}</text>')
        out.append(f'<text x="{ox - 12}" y="{oy + (5 - i + 0.5) * cell + 4}" font-size="12" fill="{C["muted"]}" text-anchor="middle">{i}</text>')
    out.append(f'<text x="{ox + 2.5 * cell}" y="{oy + 5 * cell + 38}" font-size="12" fill="{C["muted"]}" text-anchor="middle">Impact</text>')
    out.append(f'<text x="{ox - 34}" y="{oy + 2.5 * cell}" font-size="12" fill="{C["muted"]}" text-anchor="middle" '
               f'transform="rotate(-90 {ox - 34} {oy + 2.5 * cell})">Likelihood</text>')
    return "".join(out)


def fig_heatmap():
    risks = rows("02-risk/risk-register.csv")
    body = heat_grid(risks, "current", 80, 60, "Before: Phase 2 assessment")
    body += heat_grid(risks, "rescored", 560, 60, "After: re-scored (Phases 3 and 4)")
    lx = 80
    for band, name in (("L", "Low 1-4"), ("M", "Medium 5-9"), ("H", "High 10-16"), ("C", "Critical 20-25")):
        body += f'<rect x="{lx}" y="500" width="16" height="16" fill="{C[band]}"/><text x="{lx + 22}" y="513" font-size="12" fill="{C["fg"]}">{name}</text>'
        lx += 150
    return svg(980, 530, body)


def scan_metrics():
    def jl(p):
        return json.loads((ROOT / p).read_text(encoding="utf-8"))
    out = []
    for st in ("before", "after"):
        z = jl(f"evidence/phase3/{st}/zap-baseline.json")
        warn = sum(1 for s in z["site"] for a in s["alerts"] if not a["riskdesc"].startswith("Informational"))
        za = (ROOT / f"evidence/phase3/{st}/zap-active-alerts.txt").read_text(encoding="utf-8")
        high = sum(1 for ln in za.splitlines() if ln.startswith("High"))
        tr = jl(f"evidence/phase3/{st}/trivy.json")
        crit = sum(1 for r in tr.get("Results", []) for v in (r.get("Vulnerabilities") or []) if v["Severity"] == "CRITICAL")
        sq = jl(f"evidence/phase3/{st}/sqli-login-bypass.json")
        bypass = sum(1 for a in sq["attempts"] if a.get("verdict") == "BYPASS SUCCEEDED")
        ex = (ROOT / f"evidence/phase3/{st}/manual-exposed-files.txt").read_text(encoding="utf-8")
        if st == "before":
            exposed = len(re.findall(r"^## GET /(ftp|support/logs)\b.*\n HTTP/1\.1 200|^## GET /(ftp|support/logs)", ex, re.M)) and \
                      sum(1 for blk in re.split(r"^## ", ex, flags=re.M)
                          if re.match(r"GET /(ftp|support/logs|encryptionkeys)", blk) and "HTTP/1.1 200" in blk)
        else:
            exposed = len(re.findall(r"GET /(?:ftp|support/logs|encryptionkeys)\S* -> HTTP 200", ex))
        out.append({"ZAP baseline warnings (Medium+)": warn, "ZAP active: High alerts": high,
                    "Trivy Critical CVEs": crit, "Live SQLi bypass succeeded": bypass,
                    "Exposed paths answering 200": exposed})
    return out


def fig_scans():
    before, after = scan_metrics()
    keys = list(before)
    mx = max(max(before.values()), max(after.values()), 1)
    body, y = [], 50
    body.append(f'<rect x="560" y="12" width="14" height="14" fill="#c1665a"/><text x="580" y="24" font-size="12" fill="{C["fg"]}">before the fix</text>')
    body.append(f'<rect x="700" y="12" width="14" height="14" fill="{C["accent"]}"/><text x="720" y="24" font-size="12" fill="{C["fg"]}">after the fix</text>')
    for k in keys:
        body.append(f'<text x="20" y="{y + 18}" font-size="13" fill="{C["fg"]}">{esc(k)}</text>')
        for i, (val, col) in enumerate(((before[k], "#c1665a"), (after[k], C["accent"]))):
            w = 0 if val == 0 else max(4, 420 * val / mx)
            yy = y + i * 16
            body.append(f'<rect x="300" y="{yy}" width="{w}" height="13" fill="{col}"/>')
            body.append(f'<text x="{306 + w}" y="{yy + 11}" font-size="11.5" fill="{C["fg"]}">{val}</text>')
        y += 52
    body.append(f'<text x="20" y="{y + 8}" font-size="11" fill="{C["muted"]}">Values read from evidence/phase3/before and /after. '
                'Trivy CVEs are unchanged: V-05 stays open (CA-21).</text>')
    return svg(820, y + 24, "".join(body)), before, after


def fig_timeline():
    tl = rows("04-incident/INC-01-timeline.csv")
    t0 = datetime.fromisoformat(tl[0]["time_utc"].replace("Z", "+00:00"))
    groups = []
    for e in tl:
        t = datetime.fromisoformat(e["time_utc"].replace("Z", "+00:00"))
        sec = (t - t0).total_seconds()
        if groups and groups[-1][0] == sec:
            groups[-1][2].append(e["event_type"])
        else:
            groups.append([sec, e["time_utc"][11:19], [e["event_type"]]])
    span = max(g[0] for g in groups) or 1
    x0, x1, ax = 60, 1060, 120
    color = {"attack-start": "#c1665a", "attack-step": "#c1665a", "detection": "#a8711b", "containment": C["accent"]}
    body = [f'<text x="{x0}" y="28" font-size="12" fill="{C["muted"]}">INC-01, 2026-11-17, UTC. Compressed lab simulation; '
            'decision and notification steps simulated (tabletop).</text>',
            f'<line x1="{x0}" y1="{ax}" x2="{x1}" y2="{ax}" stroke="{C["fg"]}" stroke-width="1.5"/>']
    for s_ in range(0, int(span) + 1, 30):
        x = x0 + (x1 - x0) * s_ / span
        body.append(f'<line x1="{x}" y1="{ax - 4}" x2="{x}" y2="{ax + 4}" stroke="{C["fg"]}"/>'
                    f'<text x="{x}" y="{ax + 22}" font-size="11" fill="{C["muted"]}" text-anchor="middle">{s_} s</text>')
    last_x, level = -100, 0
    for n, (sec, clock, kinds) in enumerate(groups, 1):
        x = x0 + (x1 - x0) * sec / span
        level = level + 1 if x - last_x < 26 else 0
        last_x = x
        col = color.get(kinds[0], "#4f7a52")
        y = ax - 22 - level * 22
        body.append(f'<line x1="{x}" y1="{ax}" x2="{x}" y2="{y + 8}" stroke="{col}" stroke-width="1"/>'
                    f'<circle cx="{x}" cy="{ax}" r="5" fill="{col}"/>'
                    f'<circle cx="{x}" cy="{y}" r="10" fill="{col}"/>'
                    f'<text x="{x}" y="{y + 4}" font-size="11" font-weight="600" fill="#ffffff" text-anchor="middle">{n}</text>')
    half = (len(groups) + 1) // 2
    for n, (sec, clock, kinds) in enumerate(groups, 1):
        col_x = x0 if n <= half else x0 + 520
        row_y = 190 + ((n - 1) % half) * 24
        body.append(f'<text x="{col_x}" y="{row_y}" font-size="12.5" fill="{C["fg"]}"><tspan font-weight="600">{n}</tspan>'
                    f'  {clock} (+{int(sec)} s)  {esc(", ".join(dict.fromkeys(kinds)))}</text>')
    return svg(1120, 190 + half * 24 + 10, "".join(body))


def render_png(svg_path, png_path, w, h):
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                    f"--screenshot={png_path}", f"--window-size={w},{h}", svg_path.as_uri()],
                   capture_output=True, timeout=120)
    return png_path.is_file()


def build_figures():
    FIG.mkdir(parents=True, exist_ok=True)
    scans, before, after = fig_scans()
    figs = {"fig1-data-flow": fig_dataflow(), "fig2-heatmap-before-after": fig_heatmap(),
            "fig3-scans-before-after": scans, "fig4-incident-timeline": fig_timeline()}
    for name, s in figs.items():
        p = FIG / f"{name}.svg"
        p.write_text(s, encoding="utf-8")
        w, h = map(int, re.search(r'width="(\d+)" height="(\d+)"', s).groups())
        png = FIG / f"{name}.png"
        if png.exists():
            png.unlink()
        if not render_png(p, png, w, h):
            raise SystemExit(f"Edge could not render {p}")
    (FIG / "fig3-values.json").write_text(json.dumps({"before": before, "after": after}, indent=2), encoding="utf-8")
    return list(figs)


# ---------------------------------------------------------------- evidence appendix
EVIDENCE_NOTES = {
    "run-log.txt": "every command with UTC time and exit code", "network-isolation.txt": "lab network reaches the shop only",
    "nmap.nmap": "Nmap port and service scan", "trivy.json": "Trivy image scan (JSON)", "trivy-table.txt": "Trivy image scan (table)",
    "zap-baseline.json": "ZAP passive baseline scan", "zap-active-alerts.txt": "ZAP active scan of the login, alerts",
    "sqli-login-bypass.json": "live SQL injection login attempt", "manual-exposed-files.txt": "manual check of /ftp, logs, keys",
    "fix-options-sqli.json": "same injection against WAF and patched route", "attack-log.json": "INC-01 attacker requests",
    "exfiltration-summary.json": "INC-01 exposed fields and counts (no full data)", "containment-verification.json": "INC-01 attack replay after containment",
    "alerts.json": "INC-01 detection alerts", "proxy-access.log": "detection source: proxy access log",
    "containment-log.txt": "INC-01 containment steps", "exercise-log.txt": "INC-01 response steps (simulated steps marked)",
    "ca25-containment-narrowed.json": "CA-25 test: sign-up works, data reads blocked",
    "ca25-test-run1-reset-lost-after-restart.json": "CA-25 first run: restart had undone the CA-23 reset",
    "greenbone-report.xml": "Greenbone run 3: host reached, port 3000 not tested (limitation)",
    "greenbone-run1-empty-report.xml": "Greenbone run 1: empty, scanner tests not loaded",
    "greenbone-ospd-openvas-log-1.txt": "Greenbone scanner log: 'failed to load VTs'",
}


def evidence_appendix():
    refs = {}

    def add(path, ident):
        for p in [x.strip() for x in path.split(";") if x.strip() and x.strip() != "-"]:
            if p.startswith("evidence/"):
                refs.setdefault(p, set()).add(ident)
    for v in rows("03-vulnerability/vulnerability-register.csv"):
        add(v["evidence_before"], v["vuln_id"])
        add(v["evidence_after"], v["vuln_id"])
    for e in rows("04-incident/INC-01-timeline.csv"):
        add(e["evidence"], "INC-01")
    for k in rows("01-governance/kpi-register.csv"):
        add(k["evidence"], k["kpi_id"])
    for p, ident in (("evidence/phase3/before/run-log.txt", "CA-05"), ("evidence/phase3/after/run-log.txt", "CA-05"),
                     ("evidence/phase3/before/network-isolation.txt", "CA-05"), ("evidence/phase3/after/network-isolation.txt", "CA-05"),
                     ("evidence/phase4/attack/attack-log.json", "INC-01"), ("evidence/phase4/logs/proxy-access.log", "CA-15"),
                     ("evidence/phase4/response/containment-log.txt", "CA-22;CA-23"),
                     ("evidence/phase5/ca25-containment-narrowed.json", "CA-25"),
                     ("evidence/phase5/ca25-test-run1-reset-lost-after-restart.json", "CA-23"),
                     ("evidence/phase3/after/greenbone-report.xml", "CA-05"),
                     ("evidence/phase3/after/greenbone-run1-empty-report.xml", "CA-05"),
                     ("evidence/phase3/after/greenbone-ospd-openvas-log-1.txt", "CA-05")):
        for i in ident.split(";"):
            add(p, i)
    lines = ["# Appendix A: Evidence files", "",
             "Generated by `tools/build_report.py` from the registers and the timeline. Every path is relative",
             "to the project root and exists in the repository. Related IDs are the items that cite the file.", "",
             "| No. | Evidence file | Content | Related IDs |", "|---|---|---|---|"]
    for i, (p, ids) in enumerate(sorted(refs.items()), 1):
        if not (ROOT / p).is_file():
            raise SystemExit(f"evidence file missing: {p}")
        lines.append(f"| {i} | `{p}` | {EVIDENCE_NOTES.get(Path(p).name, '')} | {', '.join(sorted(ids))} |")
    lines.append("")
    (REP / "90-appendix-evidence.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return len(refs)


# ---------------------------------------------------------------- markdown to html
def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def inline(t):
    codes = []
    t = re.sub(r"`([^`]+)`", lambda m: codes.append(m.group(1)) or f"\x00{len(codes) - 1}\x00", t)
    t = esc(t)
    t = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}">', t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    return re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{esc(codes[int(m.group(1))])}</code>", t)


def md_to_html(md, toc):
    out, lines, i = [], md.replace("\r\n", "\n").split("\n"), 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            out.append("<pre><code>" + esc("\n".join(lines[i + 1:j])) + "</code></pre>")
            i = j + 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*)", ln)
        if m:
            lvl, txt = len(m.group(1)), m.group(2)
            hid = slug(txt)
            if lvl <= 2:
                toc.append((lvl, txt, hid))
            out.append(f'<h{lvl} id="{hid}">{inline(txt)}</h{lvl}>')
            i += 1
            continue
        if ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s\-:|]+\|$", lines[i + 1]):
            head = [c.strip() for c in ln.strip("|").split("|")]
            i += 2
            body = []
            while i < len(lines) and lines[i].startswith("|"):
                body.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append("<table><thead><tr>" + "".join(f"<th>{inline(h)}</th>" for h in head) + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
                       + "</tbody></table>")
            continue
        if re.match(r"^\s*(-|\d+\.)\s+", ln):
            items, stack, html_l = [], [], []
            while i < len(lines) and (re.match(r"^\s*(-|\d+\.)\s+", lines[i]) or
                                      (lines[i].startswith("  ") and lines[i].strip() and items)):
                mm = re.match(r"^(\s*)(-|\d+\.)\s+(.*)", lines[i])
                if mm:
                    items.append([len(mm.group(1)), "ol" if mm.group(2)[0].isdigit() else "ul", mm.group(3)])
                else:
                    items[-1][2] += " " + lines[i].strip()
                i += 1
            for ind, kind, txt in items:
                while stack and ind < stack[-1][0]:
                    html_l.append(f"</li></{stack.pop()[1]}>")
                if not stack or ind > stack[-1][0]:
                    html_l.append(f"<{kind}>")
                    stack.append((ind, kind))
                else:
                    html_l.append("</li>")
                html_l.append(f"<li>{inline(txt)}")
            while stack:
                html_l.append(f"</li></{stack.pop()[1]}>")
            out.append("".join(html_l))
            continue
        if not ln.strip():
            i += 1
            continue
        para = [ln.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,4}\s|\||```|\s*(-|\d+\.)\s)", lines[i]):
            para.append(lines[i].strip())
            i += 1
        text = " ".join(para)
        im = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", text)
        if im:
            out.append(f'<figure><img src="{im.group(2)}" alt="{esc(im.group(1))}"><figcaption>{inline(im.group(1))}</figcaption></figure>')
        else:
            out.append(f"<p>{inline(text)}</p>")
    return "\n".join(out)


CSS = """
@page { size: A4; margin: 20mm 18mm 20mm 18mm; }
body { font-family: Calibri, 'Segoe UI', Arial, sans-serif; font-size: 10.5pt; line-height: 1.45; color: #1b2230; background: #ffffff; }
h1 { font-size: 19pt; color: #2f5d8a; page-break-before: always; margin-top: 0; }
h2 { font-size: 13.5pt; color: #1b2230; margin-top: 18pt; }
h3 { font-size: 11.5pt; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; font-size: 9pt; page-break-inside: auto; }
th, td { border: 1px solid #c9ced8; padding: 3pt 5pt; vertical-align: top; text-align: left; }
th { background: #eef3f8; }
tr { page-break-inside: avoid; }
code { font-family: Consolas, monospace; font-size: 8.8pt; background: #f2f4f7; padding: 0 2px; }
pre { background: #f2f4f7; padding: 6pt; font-size: 8.5pt; white-space: pre-wrap; }
figure { margin: 10pt 0; text-align: center; page-break-inside: avoid; }
figure img { max-width: 100%; }
figcaption { font-size: 9pt; color: #5d6676; margin-top: 4pt; }
.title { page-break-after: always; padding-top: 60mm; }
.title h1 { page-break-before: avoid; font-size: 26pt; }
.title p { font-size: 12pt; color: #5d6676; }
.title table.fields { width: 75%; font-size: 11pt; margin: 14pt 0; }
.title table.fields th { width: 38%; }
.fill { background: #fff1a8; border: 1px dashed #b38f00; padding: 0 4px; color: #6b5200; font-weight: 600; }
.title p.note { font-size: 9.5pt; }
.toc h1 { page-break-before: avoid; }
.toc ul { list-style: none; padding-left: 0; }
.toc li.l2 { padding-left: 16pt; font-size: 9.5pt; }
.toc a { color: #1b2230; text-decoration: none; }
"""


def build_html(draft, author):
    parts, toc = [], []
    tp = REP / "title-page.json"
    fields = json.loads(tp.read_text(encoding="utf-8")) if tp.is_file() else {}
    for ch in CHAPTERS:
        md = (REP / ch).read_text(encoding="utf-8")
        if PLACEHOLDER.search(md) and not draft:
            raise SystemExit(f"{ch} still contains a placeholder; finish it or use --draft")
        parts.append(md_to_html(md, toc))
    toc_html = '<div class="toc"><h1 id="contents">Contents</h1><ul>' + "".join(
        f'<li class="l{lvl}"><a href="#{hid}">{esc(txt)}</a></li>' for lvl, txt, hid in toc) + "</ul></div>"
    title = ('<div class="title"><h1>Cyber Threat Management: Governance, Risk, Vulnerability and Incident Response</h1>'
             '<p>Case study: ShopNova GmbH (fictional Berlin web shop). All data is synthetic.</p>'
             f'<p>Semester project</p><p>Author: <strong>{esc(author)}</strong></p>'
             '<table class="fields"><tbody>'
             + "".join(f'<tr><th>{k}</th><td>{esc(fields[k])}</td></tr>' if fields.get(k) else
                       f'<tr><th>{k}</th><td><span class="fill">[TO BE FILLED IN: {k.lower()}]</span></td></tr>'
                       for k in TITLE_FIELDS)
             + '</tbody></table>'
             + ('<p class="note">Highlighted fields are placeholders and must be completed before submission '
                '(06-report/title-page.json).</p>' if not all(fields.get(k) for k in TITLE_FIELDS) else '')
             + '<p>Report version: 17 November 2026</p></div>')
    doc = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>ShopNova Threat Management Report</title>'
           f'<style>{CSS}</style></head><body>{title}{toc_html}{"".join(parts)}</body></html>')
    OUT.mkdir(parents=True, exist_ok=True)
    p = REP / f"{NAME}.html"          # next to figures/ so relative image paths work
    p.write_text(doc, encoding="utf-8")
    import hashlib
    info = {ch: hashlib.sha256((REP / ch).read_bytes().replace(b"\r\n", b"\n")).hexdigest() for ch in CHAPTERS}
    (OUT / "build-info.json").write_text(json.dumps({"author": author, "sources": info}, indent=2), encoding="utf-8")
    return p, len(toc)


def build_pdf(html_path):
    pdf = OUT / f"{NAME}.pdf"
    if pdf.exists():
        pdf.unlink()
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", html_path.as_uri()], capture_output=True, timeout=180)
    return pdf if pdf.is_file() else None


def build_docx(html_path):
    docx = OUT / f"{NAME}.docx"
    if docx.exists():
        docx.unlink()
    ps = f"""
$ErrorActionPreference = 'Stop'
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {{
  $d = $w.Documents.Open('{html_path}', $false, $true)
  foreach ($s in @($d.InlineShapes)) {{ if ($s.LinkFormat) {{ $s.LinkFormat.SavePictureWithDocument = $true; $s.LinkFormat.BreakLink() }} }}
  foreach ($s in @($d.Shapes)) {{ if ($s.LinkFormat) {{ $s.LinkFormat.SavePictureWithDocument = $true; $s.LinkFormat.BreakLink() }} }}
  $d.SaveAs2('{docx}', 16)
  $d.Close($false)
}} finally {{ $w.Quit() }}
"""
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print(r.stderr[-800:])
    return docx if docx.is_file() else None


def main():
    draft = "--draft" in sys.argv
    author = sys.argv[sys.argv.index("--author") + 1] if "--author" in sys.argv else \
        subprocess.run(["git", "config", "user.name"], capture_output=True, text=True, cwd=ROOT).stdout.strip() or "Author"
    figs = build_figures()
    n_ev = evidence_appendix()
    html_path, n_toc = build_html(draft, author)
    pdf = build_pdf(html_path)
    docx = build_docx(html_path)
    print(f"figures: {len(figs)} ({', '.join(figs)})")
    print(f"evidence appendix: {n_ev} files")
    print(f"HTML: {html_path} ({n_toc} contents entries)")
    print(f"PDF:  {pdf or 'FAILED'}")
    print(f"DOCX: {docx or 'FAILED'}")
    return 0 if pdf and docx else 1


if __name__ == "__main__":
    sys.exit(main())
