#!/usr/bin/env python3
"""Phase 3 (Vulnerability management) validator.

Run from the project root:
    py tools\\validate_phase3.py
Re-runs the Phase 2 validator (which re-runs Phases 1 and 0) first. Standard library only.
"""
import json
import re
import sys
from datetime import date, timedelta

from vcommon import (
    Report, cvss31, cvss_severity, is_date, load_assets, load_data, load_traceability,
    read_csv, root_from_argv, run_previous, split_list,
)

VULN = "03-vulnerability"
EV = "evidence/phase3"
REQUIRED_FILES = [
    f"{VULN}/vulnerability-register.csv", f"{VULN}/phase3-summary.md", f"{VULN}/fix-options.md",
    f"{VULN}/lab/README.md", f"{VULN}/lab/zap_login_ascan.py", f"{VULN}/lab/fix/login.js",
    f"{VULN}/lab/fix/login.original.js", f"{VULN}/lab/fix/Dockerfile",
    f"{VULN}/lab/fix/nginx-hardening.conf", f"{VULN}/before/README.md", f"{VULN}/after/README.md",
    f"{EV}/before/run-log.txt", f"{EV}/after/run-log.txt", f"{EV}/options/fix-options-sqli.json",
]
COLS = ["vuln_id", "title", "asset", "source_tool", "evidence_before", "cwe", "cvss_vector",
        "cvss_score", "cvss_severity", "exploited_in_lab", "internet_facing", "personal_data",
        "business_priority", "priority_reason", "deadline_days", "risk_ids", "fix_action_ids",
        "detected_on", "status", "fixed_on", "evidence_after", "notes"]
BASE_PRIORITY = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}
DEADLINE = {1: 7, 2: 30, 3: 90, 4: 180}
STATUS = {"Open", "Fixed", "Mitigated", "Accepted"}
ALLOWED_SCAN_TARGETS = ("juice-shop", "http://juice-shop:3000", "http://127.0.0.1:3000")


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def main():
    root = root_from_argv()
    rep = Report("Phase 3 validation")
    run_previous(root, "validate_phase2.py", rep, "Phases 0 to 2")

    missing = [f for f in REQUIRED_FILES if not (root / f).is_file()]
    for f in missing:
        rep.fail(f"missing file: {f}")
    if not missing:
        rep.ok(f"all {len(REQUIRED_FILES)} Phase 3 files and evidence logs present")

    assets, data = load_assets(root), load_data(root)
    risks = {r["risk_id"]: r for _, r in (read_csv(root, "02-risk/risk-register.csv", ["risk_id"], rep) or [])}
    plan = {r["action_id"]: r for _, r in (read_csv(root, "02-risk/risk-treatment-plan.csv", ["action_id"], rep) or [])}

    # --- Vulnerability register ---------------------------------------------
    vulns, errors = {}, 0
    for ln, v in read_csv(root, f"{VULN}/vulnerability-register.csv", COLS, rep) or []:
        where = f"vulnerability-register.csv line {ln}"
        vid = v["vuln_id"]
        if not re.fullmatch(r"V-\d{2,3}", vid) or vid in vulns:
            rep.fail(f"{where}: bad or duplicate ID '{vid}'")
            errors += 1
            continue
        vulns[vid] = v
        if v["asset"] not in assets:
            rep.fail(f"{where}: {vid} unknown asset {v['asset']}")
            errors += 1
        for d in split_list(v["personal_data"]):
            if d not in data:
                rep.fail(f"{where}: {vid} unknown data category {d}")
                errors += 1
        for rid in split_list(v["risk_ids"]) or ["(none)"]:
            if rid not in risks:
                rep.fail(f"{where}: {vid} must link to an existing risk, got {rid}")
                errors += 1
        for cid in split_list(v["fix_action_ids"]) or ["(none)"]:
            if cid not in plan:
                rep.fail(f"{where}: {vid} must link to an existing CA, got {cid}")
                errors += 1
        for f in split_list(v["evidence_before"]):
            if not (root / f).is_file():
                rep.fail(f"{where}: {vid} evidence file missing: {f}")
                errors += 1
        score = cvss31(v["cvss_vector"])
        if score is None:
            rep.fail(f"{where}: {vid} invalid CVSS vector '{v['cvss_vector']}'")
            errors += 1
        else:
            if f"{score:.1f}" != v["cvss_score"]:
                rep.fail(f"{where}: {vid} CVSS score {v['cvss_score']} but the vector gives {score:.1f}")
                errors += 1
            if cvss_severity(score) != v["cvss_severity"]:
                rep.fail(f"{where}: {vid} severity should be {cvss_severity(score)}")
                errors += 1
            m = re.fullmatch(r"P([1-4])", v["business_priority"])
            base = BASE_PRIORITY.get(cvss_severity(score), 4)
            if not m:
                rep.fail(f"{where}: {vid} business_priority must be P1 to P4")
                errors += 1
            else:
                p = int(m.group(1))
                if p not in (base, base - 1):
                    rep.fail(f"{where}: {vid} priority P{p} is more than one level from severity "
                             f"(P{base}); POL-02 allows raising by at most one level")
                    errors += 1
                if p == base - 1 and "raise" not in v["priority_reason"].lower():
                    rep.fail(f"{where}: {vid} is raised to P{p}; priority_reason must say why")
                    errors += 1
                want = 3 if p == 1 and v["exploited_in_lab"] == "yes" and v["internet_facing"] == "yes" \
                    else DEADLINE[p]
                if v["deadline_days"] != str(want):
                    rep.fail(f"{where}: {vid} deadline_days should be {want} for P{p} (POL-02 statement 4)")
                    errors += 1
        if v["status"] not in STATUS or not is_date(v["detected_on"]):
            rep.fail(f"{where}: {vid} status or detected_on invalid")
            errors += 1
        if v["status"] == "Fixed":
            if not is_date(v["fixed_on"]):
                rep.fail(f"{where}: {vid} is Fixed but has no fixed_on date")
                errors += 1
            after = split_list(v["evidence_after"])
            if not after or any(not (root / f).is_file() for f in after):
                rep.fail(f"{where}: {vid} is Fixed but its verification evidence is missing")
                errors += 1
            if not any(plan.get(c, {}).get("status") in ("Done", "In progress")
                       for c in split_list(v["fix_action_ids"])):
                rep.fail(f"{where}: {vid} is Fixed but none of its CAs is Done or In progress")
                errors += 1
        elif v["status"] == "Open" and is_date(v["detected_on"]) and v["deadline_days"].isdigit():
            due = date.fromisoformat(v["detected_on"]) + timedelta(days=int(v["deadline_days"]))
            (rep.warn if date.today() > due else rep.ok)(
                f"{vid} is open; POL-02 deadline {due}" + (" has PASSED" if date.today() > due else " not yet reached"))
    if vulns and not errors:
        rep.ok(f"vulnerability register: {len(vulns)} findings; CVSS scores recomputed from vectors; "
               "priorities and deadlines follow POL-02; links to A, D, R and CA valid")

    fixed = [k for k, v in vulns.items() if v["status"] == "Fixed"]
    (rep.ok if 3 <= len(fixed) <= 5 else rep.warn)(f"{len(fixed)} findings fixed in the lab (target 3 to 5): {fixed}")
    r12 = [k for k, v in vulns.items() if "R-12" in split_list(v["risk_ids"]) and v["status"] == "Fixed"]
    (rep.ok if r12 else rep.fail)(f"R-12 (SQL injection) has a fixed vulnerability: {r12 or 'none'}")

    # --- Same attack before and after ----------------------------------------
    b = load_json(root / EV / "before/sqli-login-bypass.json")
    a = load_json(root / EV / "after/sqli-login-bypass.json")
    if b and a:
        sb = next((x for x in b["attempts"] if x["attempt"].startswith("SQL")), {})
        sa = next((x for x in a["attempts"] if x["attempt"].startswith("SQL")), {})
        if sb.get("request_body") != sa.get("request_body"):
            rep.fail("before and after attacks used different request bodies")
        elif sb.get("verdict") == "BYPASS SUCCEEDED" and sa.get("verdict") == "blocked":
            rep.ok(f"same attack {sb['request_body']['email']!r}: before HTTP {sb['http_status']} bypass, "
                   f"after HTTP {sa['http_status']} blocked")
        else:
            rep.fail(f"expected bypass before and blocked after; got {sb.get('verdict')} / {sa.get('verdict')}")
    else:
        rep.fail("sqli-login-bypass.json missing or unreadable before or after")

    zb = (root / EV / "before/zap-active-alerts.txt")
    za = (root / EV / "after/zap-active-alerts.txt")
    if zb.is_file() and za.is_file():
        if "SQL Injection" in zb.read_text(encoding="utf-8") and "SQL Injection" not in za.read_text(encoding="utf-8"):
            rep.ok("ZAP active scan: SQL Injection found before, not found after")
        else:
            rep.fail("ZAP active scan should show SQL Injection before and not after")

    opts = load_json(root / EV / "options/fix-options-sqli.json") or []
    for label in ("option A", "option B"):
        inj = [o for o in opts if o["option"].startswith(label) and o["request"].startswith("SQL")]
        ok_login = [o for o in opts if o["option"].startswith(label) and "correct password" in o["request"]]
        if inj and not any(o["token_issued"] for o in inj) and ok_login and ok_login[0]["token_issued"]:
            rep.ok(f"fix {label}: all {len(inj)} injection variants blocked; legitimate login still works")
        else:
            rep.fail(f"fix {label}: test results missing or not as expected")

    # --- Isolation and scope -------------------------------------------------
    for stage in ("before", "after"):
        p = root / EV / stage / "network-isolation.txt"
        t = p.read_text(encoding="utf-8") if p.is_file() else ""
        lines = t.splitlines()
        if lines and "REACHABLE" in lines[0] and all("blocked" in ln for ln in lines[1:] if ln.strip()):
            rep.ok(f"{stage}: lab network reaches Juice Shop only (internet and host blocked)")
        else:
            rep.fail(f"{stage}: network-isolation.txt missing or shows unexpected reachability")
    scope_errors = 0
    for stage in ("before", "after", "options"):
        p = root / EV / stage / "run-log.txt"
        for ln in (p.read_text(encoding="utf-8").splitlines() if p.is_file() else []):
            if "nmap" in ln and "-oA" in ln and not ln.rstrip().endswith(" juice-shop"):
                rep.fail(f"{stage} run-log: Nmap target outside scope: {ln.strip()[:120]}")
                scope_errors += 1
            if "zap-baseline.py" in ln or "zap_login_ascan.py" in ln:
                if "http://juice-shop:3000" not in ln:
                    rep.fail(f"{stage} run-log: ZAP target outside scope: {ln.strip()[:120]}")
                    scope_errors += 1
    if not scope_errors:
        rep.ok("run logs: every Nmap and ZAP scan targeted only the lab Juice Shop")

    # --- Traceability --------------------------------------------------------
    exp_x = {(k, r) for k, v in vulns.items() for r in split_list(v["risk_ids"])}
    exp_m = {(c, k) for k, v in vulns.items() for c in split_list(v["fix_action_ids"])}
    act_x, act_m, terr = set(), set(), 0
    for ln, row in load_traceability(root):
        if len(row) != 4:
            continue
        if row[0].startswith("V-") and row[0] not in vulns or row[2].startswith("V-") and row[2] not in vulns:
            rep.fail(f"traceability.csv line {ln}: unknown V ID")
            terr += 1
        if row[1] == "exposes":
            act_x.add((row[0], row[2]))
        elif row[1] == "mitigates":
            act_m.add((row[0], row[2]))
    for label, exp, act in (("exposes", exp_x, act_x), ("mitigates", exp_m, act_m)):
        for x, y in sorted(exp ^ act):
            rep.fail(f"traceability.csv: '{x} {label} {y}' does not match the vulnerability register "
                     "(run py tools\\build_traceability.py)")
            terr += 1
    if not terr:
        rep.ok(f"traceability.csv: {len(act_x)} 'exposes' and {len(act_m)} 'mitigates' links match the register")

    # --- Greenbone outcome ---------------------------------------------------
    summary = (root / VULN / "phase3-summary.md")
    stext = summary.read_text(encoding="utf-8") if summary.is_file() else ""
    section = stext.split("## 6. Greenbone", 1)[1].split("\n## ", 1)[0] if "## 6. Greenbone" in stext else ""
    report = root / EV / "after/greenbone-report.xml"
    if re.search(r"Status: \*\*pending", section):
        rep.todo("Greenbone result pending: add the report, or record the limitation after the 20:30 cutoff")
    elif re.search(r"Status: \*\*done", section):
        (rep.ok if report.is_file() else rep.fail)(
            "Greenbone scan done and its report is in evidence/phase3/after/greenbone-report.xml"
            if report.is_file() else "phase3-summary.md says Greenbone is done, but greenbone-report.xml is missing")
    elif "limitation" in section.lower():
        rep.ok("Greenbone: no usable scan result; limitation recorded in phase3-summary.md")
    else:
        rep.fail("phase3-summary.md must contain a '## 6. Greenbone' section with the result or the limitation")

    return rep.finish(root, "Phase 3 is complete. Ready for Phase 4 (Incident response).")


if __name__ == "__main__":
    sys.exit(main())
