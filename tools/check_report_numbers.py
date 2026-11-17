#!/usr/bin/env python3
"""Check that the numbers in the report (06-report/*.md) match their sources.

Run from the project root:
    py tools\\check_report_numbers.py
Every check recomputes a value from a register or evidence file and looks for the
statement in the named chapter. A missing or different statement is a MISMATCH.
Exit code 1 if any mismatch is found. Standard library only.
"""
import collections
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REP = ROOT / "06-report"


def rows(rel):
    with (ROOT / rel).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def js(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def t(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def log_time(rel, needle):
    for ln in (ROOT / rel).read_text(encoding="utf-8").splitlines():
        if needle in ln:
            return ln.split()[0]
    return None


def main():
    ch = {p.name: p.read_text(encoding="utf-8") for p in REP.glob("*.md")}
    allt = "\n".join(ch.values())
    checks = []   # (label, source, chapter, regex)

    def chk(label, source, chapter, pattern):
        checks.append((label, source, chapter, pattern))

    words = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve", 16: "sixteen"}

    def num(n):
        w = words.get(n)
        return rf"(?:{n}|{w.capitalize()}|{w})" if w else str(n)

    # --- governance
    pols, kpis = rows("01-governance/policy-register.csv"), rows("01-governance/kpi-register.csv")
    raci, fmap = rows("01-governance/raci-matrix.csv"), rows("01-governance/framework-mapping.csv")
    gaps = len(re.findall(r"^\| \d+ \|", (ROOT / "01-governance/gdpr-baseline-gap-assessment.md").read_text(encoding="utf-8"), re.M))
    dpo = re.search(r"\*\*Total\*\* \| \*\*(\d+)\*\*", (ROOT / "01-governance/governance-structure.md").read_text(encoding="utf-8")).group(1)
    chk("number of policies", "policy-register.csv", "02-governance.md", rf"{num(len(pols))} policies")
    chk("number of KPIs", "kpi-register.csv", "02-governance.md", rf"{num(len(kpis))} KPIs")
    chk("RACI activities", "raci-matrix.csv", "02-governance.md", rf"{len(raci)} recurring activities")
    chk("framework references", "framework-mapping.csv", "02-governance.md", rf"{len(fmap)} references")
    chk("gaps in the gap assessment", "gdpr-baseline-gap-assessment.md", "02-governance.md", rf"{gaps} gaps")
    chk("DPO head count", "governance-structure.md", "02-governance.md", rf"{dpo} such people")
    chk("conclusion: policies, KPIs, references", "registers", "08-conclusion.md",
        rf"{num(len(pols))} policies.*{num(len(kpis))} KPIs.*{len(fmap)} references")

    # --- risk (Phase 2 = without R-17)
    risks = rows("02-risk/risk-register.csv")
    p2 = [r for r in risks if r["risk_id"] != "R-17"]
    chk("Phase 2 risk count", "risk-register.csv (excluding R-17)", "03-risk-management.md", rf"{num(len(p2))} risks were identified")
    for lv in ("Critical", "High", "Medium", "Low"):
        a = sum(r["current_level"] == lv for r in p2)
        b = sum(r["target_level"] == lv for r in p2)
        chk(f"Phase 2 {lv} current/target", "risk-register.csv", "03-risk-management.md", rf"\| {lv} \| {a} \| {b} \|")
    hi = [r["risk_id"] for r in p2 if r["current_level"] == "High"]
    for rid in hi:
        chk(f"{rid} listed as High in Phase 2", "risk-register.csv", "03-risk-management.md", rf"{rid}: ")
    for rid in ("R-01", "R-12"):
        r = next(x for x in risks if x["risk_id"] == rid)
        chk(f"{rid} Phase 2 likelihood/impact", "risk-register.csv", "03-risk-management.md",
            rf"\(likelihood {r['current_likelihood']}, impact {r['current_impact']}\)")
    plan = rows("02-risk/risk-treatment-plan.csv")
    rt = [p for p in plan if p["source"] == "Risk treatment"]
    chk("Phase 2 treatment actions", "risk-treatment-plan.csv (source Risk treatment)", "03-risk-management.md",
        rf"{len(rt)} actions \(CA-01 to CA-{len(rt):02d}\)")
    hc2 = sum(r["current_level"] in ("High", "Critical") for r in p2)
    chk("Phase 2 High+Critical with plan", "risk-register.csv", "03-risk-management.md", rf"All {num(hc2)} High and Critical risks")

    # --- integration: before / after / target
    for lv in ("Critical", "High", "Medium", "Low"):
        a, b, c = (sum(r[f"{k}_level"] == lv for r in risks) for k in ("current", "rescored", "target"))
        chk(f"{lv} before/after/target", "risk-register.csv", "06-integration.md", rf"\| {lv} \| {a} \| {b} \| {c} \|")
    chk("risk total", "risk-register.csv", "06-integration.md", rf"{len(risks)} risks")
    changed = [r for r in risks if r["current_score"] != r["rescored_score"]]
    chk("risks that changed score", "risk-register.csv", "06-integration.md", rf"{num(len(changed))} risks changed score")
    chk("risks unchanged", "risk-register.csv", "06-integration.md", rf"{num(len(risks) - len(changed))} risks keep")
    for r in changed:
        chk(f"{r['risk_id']} re-score", "risk-register.csv", "06-integration.md",
            rf"{r['risk_id']}[^|\n]*\| {r['current_score']} {r['current_level']} \| {r['rescored_score']} {r['rescored_level']} \|")
    hc = sum(r["rescored_level"] in ("High", "Critical") for r in risks)
    chk("KPI-10 after re-scoring", "risk-register.csv", "06-integration.md", rf"100% \({hc} of {hc}\)")
    links = sum(1 for _ in open(ROOT / "traceability.csv", encoding="utf-8")) - 1
    for f in ("06-integration.md", "08-conclusion.md"):
        chk("traceability links", "traceability.csv", f, rf"{links} links")
    for rid in ("R-01", "R-12", "R-03"):
        r = next(x for x in risks if x["risk_id"] == rid)
        chk(f"conclusion {rid} new score", "risk-register.csv", "08-conclusion.md", rf"{rid}[^,;)]*?{r['rescored_score']}")

    # --- executive summary and current state (must match the re-scored register)
    lvl = {lv: tuple(sum(r[f"{k}_level"] == lv for r in risks) for k in ("current", "rescored", "target"))
           for lv in ("Critical", "High", "Medium", "Low")}
    for lv, (a, b, c) in lvl.items():
        chk(f"exec summary {lv} before/now/target", "risk-register.csv", "00-executive-summary.md",
            rf"\| {lv} \| {a} \| {b} \| {c} \|")
    cur = ", ".join(f"{lvl[lv][1]} {lv}" for lv in ("Critical", "High", "Medium")) + f" and {lvl['Low'][1]} Low"
    chk("conclusion current state", "risk-register.csv", "08-conclusion.md", re.escape(cur))
    for rid in ("R-01", "R-03"):
        r = next(x for x in risks if x["risk_id"] == rid)
        chk(f"exec summary {rid} current score", "risk-register.csv", "00-executive-summary.md",
            rf"{rid}[^\n]*?: {r['rescored_score']}\.")
    chk("exec summary: plan target not reached", "risk-register.csv", "00-executive-summary.md",
        rf"target of {lvl['Critical'][2]} Critical and {lvl['High'][2]} High has not been reached")
    chk("exec summary Phase 2 risk count", "risk-register.csv", "00-executive-summary.md", rf"{len(p2)} risks were identified")
    vregs = rows("03-vulnerability/vulnerability-register.csv")
    chk("exec summary vulnerabilities", "vulnerability-register.csv", "00-executive-summary.md",
        rf"{len(vregs)} vulnerabilities were recorded")
    chk("exec summary fixed", "vulnerability-register.csv", "00-executive-summary.md",
        rf"{num(sum(v['status'] == 'Fixed' for v in vregs))} were fixed")
    chk("exec summary R-12", "risk-register.csv", "00-executive-summary.md",
        rf"R-12 \(SQL injection\) went from {next(x for x in risks if x['risk_id'] == 'R-12')['current_score']} to "
        rf"{next(x for x in risks if x['risk_id'] == 'R-12')['rescored_score']}")
    for f in ("03-risk-management.md", "06-integration.md"):
        chk("current Critical/High stated next to the plan", "risk-register.csv", f,
            rf"{lvl['Critical'][1]} Critical[^.]*{lvl['High'][1]} High")

    # --- vulnerabilities
    vulns = rows("03-vulnerability/vulnerability-register.csv")
    chk("number of findings", "vulnerability-register.csv", "04-vulnerability-management.md", rf"{num(len(vulns))} findings")
    for v in vulns:
        chk(f"{v['vuln_id']} CVSS", "vulnerability-register.csv", "04-vulnerability-management.md",
            rf"\| {v['vuln_id']} \|[^\n]*\| {v['cvss_score']} {v['cvss_severity']}")
        chk(f"{v['vuln_id']} status", "vulnerability-register.csv", "04-vulnerability-management.md",
            rf"\| {v['vuln_id']} \|[^\n]*\| {v['status']}")
    tr = js("evidence/phase3/before/trivy.json")
    sev = collections.Counter(x["Severity"] for r in tr.get("Results", []) for x in (r.get("Vulnerabilities") or []))
    total = sum(sev.values())
    chk("Trivy breakdown", "evidence/phase3/before/trivy.json", "04-vulnerability-management.md",
        rf"{total} known CVEs: {sev['CRITICAL']} Critical, {sev['HIGH']} High, {sev['MEDIUM']} Medium, {sev['LOW']} Low, {sev['UNKNOWN']} Unknown")
    tra = js("evidence/phase3/after/trivy.json")
    total_a = sum(1 for r in tra.get("Results", []) for x in (r.get("Vulnerabilities") or []))
    chk("Trivy after", "evidence/phase3/after/trivy.json", "04-vulnerability-management.md", rf"unchanged \({total_a}\)")
    for f in ("06-integration.md", "05-incident-response.md"):
        pass
    chk("Trivy total in integration", "trivy.json", "06-integration.md", rf"{total} CVEs, {sev['CRITICAL']} Critical")
    for st, label in (("before", "before"), ("after", "after")):
        z = js(f"evidence/phase3/{st}/zap-baseline.json")
        al = [a for s in z["site"] for a in s["alerts"]]
        med = sum(1 for a in al if a["riskdesc"].startswith("Medium"))
        inf = sum(1 for a in al if a["riskdesc"].startswith("Informational"))
        chk(f"ZAP baseline {label}", f"evidence/phase3/{st}/zap-baseline.json", "04-vulnerability-management.md",
            rf"{len(al)} warnings \({med} Medium, {inf} informational\)")
    tb = log_time("evidence/phase3/before/run-log.txt", "SQL injection login bypass: HTTP 200")
    ta = log_time("evidence/phase3/after/run-log.txt", "SQL injection login bypass: HTTP 401")
    chk("SQLi before time", "evidence/phase3/before/run-log.txt", "04-vulnerability-management.md", re.escape(tb[11:19]))
    chk("SQLi after time", "evidence/phase3/after/run-log.txt", "04-vulnerability-management.md", re.escape(ta[11:19]))
    zt = None
    lines = (ROOT / "evidence/phase3/before/run-log.txt").read_text(encoding="utf-8").splitlines()
    for i, ln in enumerate(lines):
        if "zap_login_ascan.py" in ln and i + 1 < len(lines) and "exit code 0" in lines[i + 1]:
            zt = lines[i + 1].split()[0]
    k01 = (t(ta) - t(zt)).total_seconds() / 3600
    chk("KPI-01 hours", "run logs (ZAP alert -> verified fix)", "04-vulnerability-management.md", rf"{k01:.2f} hours")
    chk("KPI-01 ZAP alert time", "evidence/phase3/before/run-log.txt", "04-vulnerability-management.md", re.escape(zt[11:19]))
    chk("KPI-01 in integration", "kpi-register.csv", "06-integration.md", rf"{k01:.2f} h")

    # --- incident
    ex = js("evidence/phase4/attack/exfiltration-summary.json")
    chk("attack requests", "exfiltration-summary.json", "05-incident-response.md", rf"{ex['requests']} requests")
    chk("accounts exposed", "exfiltration-summary.json", "05-incident-response.md", rf"All {ex['accounts_exposed']} lab accounts")
    chk("attack window", "exfiltration-summary.json", "05-incident-response.md",
        rf"{ex['attack_start_utc'][11:19]} and {ex['attack_end_utc'][11:19]} UTC")
    tl = rows("04-incident/INC-01-timeline.csv")
    first = {}
    for e in tl:
        first.setdefault(e["event_type"], t(e["time_utc"]))
    det = int((first["detection"] - first["attack-start"]).total_seconds())
    cont = [t(e["time_utc"]) for e in tl if e["event_type"] == "containment"]
    contained = int((max(cont) - first["attack-start"]).total_seconds())
    dec = int((first["notification-decision"] - first["awareness"]).total_seconds())
    for f in ("05-incident-response.md", "06-integration.md", "08-conclusion.md"):
        chk("KPI-06 seconds", "INC-01-timeline.csv", f, rf"{det} s(econds)?")
    for f in ("05-incident-response.md", "08-conclusion.md"):
        chk("containment seconds", "INC-01-timeline.csv", f, rf"{contained} seconds")
    for f in ("05-incident-response.md", "06-integration.md"):
        chk("KPI-05 seconds", "INC-01-timeline.csv", f, rf"{dec} s(econds)?")
    for kind in ("detection", "awareness"):
        chk(f"{kind} time", "INC-01-timeline.csv", "05-incident-response.md", first[kind].strftime("%H:%M:%S"))
    for c in cont:
        chk("containment time", "INC-01-timeline.csv", "05-incident-response.md", c.strftime("%H:%M:%S"))
    dl = first["awareness"].timestamp() + 72 * 3600
    chk("Art. 33 deadline", "INC-01-timeline.csv + 72 h", "05-incident-response.md",
        datetime.fromtimestamp(dl, timezone.utc).strftime("%Y-%m-%d %H:%M"))
    al = js("evidence/phase4/detection/alerts.json")["alerts"]
    for a in al:
        if a["rule"] in (1, 2):
            chk(f"rule {a['rule']} count", "alerts.json", "05-incident-response.md", rf"\| {a['rule']} \|[^\n]*{a['count']} requests")
    enisa = re.search(r"\*\*Severity\*\* \| \*\*([\d.]+)", (ROOT / "04-incident/INC-01-breach-assessment.md").read_text(encoding="utf-8")).group(1)
    chk("ENISA severity", "INC-01-breach-assessment.md", "05-incident-response.md", rf"ENISA severity {enisa}")
    c25 = js("evidence/phase5/ca25-containment-narrowed.json")["tests"]
    chk("CA-25 sign-up status", "ca25-containment-narrowed.json", "05-incident-response.md", rf"\({c25[0]['http_status']}\)")
    r1 = js("evidence/phase5/ca25-test-run1-reset-lost-after-restart.json")["time_utc"][11:16]
    chk("restart detected time", "ca25-test-run1-...json", "05-incident-response.md", rf"{r1} UTC")

    # --- KPI table values match the register
    kv = {k["kpi_id"]: k for k in kpis}
    for kid, needle in (("KPI-02", "100% (1 of 1 due"), ("KPI-05", "55 s (0.02 h)"), ("KPI-06", "18 s")):
        ok_reg = kv[kid]["measured_value"].startswith(needle)
        checks.append((f"{kid} value in register starts with '{needle}'", "kpi-register.csv", None, ok_reg))
        chk(f"{kid} value in report", "kpi-register.csv", "06-integration.md", rf"{kid}[^\n]*\| {re.escape(needle)}[^\n|]*\| {kv[kid]['value_type']} \|")

    # --- placeholders and known stale values
    for pat, why in ((r"GREENBONE_STATUS", "Greenbone placeholder"), (r"\[Your name", "author placeholder"),
                     (r"\b0\.3 h(ours)?\b", "old KPI-01 value (corrected to 0.13 h)")):
        checks.append((f"no {why}", "-", None, not re.search(pat, allt)))

    mism = []
    for label, source, chapter, pat in checks:
        if chapter is None:
            ok = pat
        else:
            text = ch.get(chapter, "")
            ok = re.search(pat, text, re.S) is not None
            if not ok and not pat.startswith(r"\|"):   # prose may wrap across lines
                ok = re.search(pat, re.sub(r"\s+", " ", text)) is not None
        print(f"[{'MATCH' if ok else 'MISMATCH'}] {label}  ({source} -> {chapter or 'report'})")
        if not ok:
            mism.append(label)
    print(f"\n{len(checks) - len(mism)} of {len(checks)} checks match; {len(mism)} mismatch(es)")
    for m in mism:
        print("  MISMATCH:", m)
    return 1 if mism else 0


if __name__ == "__main__":
    sys.exit(main())
