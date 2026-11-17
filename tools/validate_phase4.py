#!/usr/bin/env python3
"""Phase 4 (Incident response) validator.

Run from the project root:
    py tools\\validate_phase4.py
Re-runs the Phase 3 validator (which re-runs Phases 0 to 2) first. Standard library only.
"""
import csv
import json
import re
import subprocess
import sys
from datetime import datetime, timezone

from vcommon import (
    Report, load_data, load_traceability, read_csv, root_from_argv, run_previous, split_list,
)

INC = "04-incident"
EV = "evidence/phase4"
REQUIRED_FILES = [
    f"{INC}/README.md", f"{INC}/INC-01-timeline.csv", f"{INC}/INC-01-breach-assessment.md",
    f"{INC}/INC-01-art33-notification.md", f"{INC}/INC-01-art34-customer-notice.md",
    f"{INC}/INC-01-post-incident-review.md", f"{INC}/breach-register.csv",
    "tools/breach_clock.py", "tools/phase4_attack.py", "tools/phase4_detect.py",
    f"{EV}/attack/attack-log.json", f"{EV}/attack/exfiltration-summary.json",
    f"{EV}/attack/containment-verification.json", f"{EV}/detection/alerts.json",
    f"{EV}/logs/proxy-access.log", f"{EV}/response/containment-log.txt", f"{EV}/response/exercise-log.txt",
]
REQUIRED_EVENTS = ["attack-start", "detection", "containment", "awareness", "md-informed",
                   "risk-assessed", "notification-decision", "authority-notified", "review"]
BREACH_COLS = ["inc_id", "title", "severity", "awareness_utc", "data_categories", "data_subjects",
               "approx_records", "risk_to_subjects", "authority_notified", "authority_notified_utc",
               "subjects_informed", "subjects_informed_utc", "decision_reason", "vuln_ids", "risk_ids",
               "resolved_by", "status", "evidence"]
ART33 = ["33(3)(a)", "33(3)(b)", "33(3)(c)", "33(3)(d)"]
ART34 = ["What happened", "Which of your data", "What could this mean", "What should you do",
         "What are we doing", "data protection officer"]


def ts(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def main():
    root = root_from_argv()
    rep = Report("Phase 4 validation")
    run_previous(root, "validate_phase3.py", rep, "Phases 0 to 3")

    missing = [f for f in REQUIRED_FILES if not (root / f).is_file()]
    for f in missing:
        rep.fail(f"missing file: {f}")
    if not missing:
        rep.ok(f"all {len(REQUIRED_FILES)} Phase 4 files and evidence present")

    # --- Timeline ------------------------------------------------------------
    timeline = read_csv(root, f"{INC}/INC-01-timeline.csv",
                        ["time_utc", "event_type", "description", "source", "evidence"], rep) or []
    events, terr = [], 0
    for ln, e in timeline:
        try:
            events.append((ts(e["time_utc"]), e["event_type"], e))
        except ValueError:
            rep.fail(f"INC-01-timeline.csv line {ln}: bad time '{e['time_utc']}'")
            terr += 1
        if not (root / e["evidence"]).is_file():
            rep.fail(f"INC-01-timeline.csv line {ln}: evidence file missing: {e['evidence']}")
            terr += 1
    times = [t for t, _, _ in events]
    if times != sorted(times):
        rep.fail("INC-01-timeline.csv: events are not in time order")
        terr += 1
    first = {}
    for t, kind, _ in events:
        first.setdefault(kind, t)
    lacking = [k for k in REQUIRED_EVENTS if k not in first]
    if lacking:
        rep.fail(f"INC-01-timeline.csv: missing event types {lacking}")
        terr += 1
    elif not (first["attack-start"] <= first["detection"] <= first["awareness"]
              <= first["notification-decision"] <= first["authority-notified"]):
        rep.fail("INC-01-timeline.csv: expected attack-start <= detection <= awareness <= decision <= notification")
        terr += 1
    if not terr and timeline:
        rep.ok(f"INC-01 timeline: {len(events)} events in order, all required steps present, every event has evidence")

    # --- Breach clock --------------------------------------------------------
    proc = subprocess.run([sys.executable, str(root / "tools" / "breach_clock.py"), "--inc", "INC-01"],
                          capture_output=True, text=True, encoding="utf-8", cwd=root)
    kpi = [ln.strip() for ln in proc.stdout.splitlines() if ln.startswith("KPI-")]
    if proc.returncode == 0 and "MISSED" not in proc.stdout:
        rep.ok("breach clock: all POL-05 and Art. 33 milestones met; " + "; ".join(kpi))
    else:
        rep.fail("breach clock reports a missed milestone; run py tools\\breach_clock.py --inc INC-01")

    # --- Detection and containment evidence ---------------------------------
    try:
        alerts = json.loads((root / EV / "detection/alerts.json").read_text(encoding="utf-8"))
        attack = json.loads((root / EV / "attack/attack-log.json").read_text(encoding="utf-8"))
        cont = json.loads((root / EV / "attack/containment-verification.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        alerts, attack, cont = {}, [], {}
        rep.fail("detection, attack or containment evidence unreadable")
    if alerts and attack:
        high = [a for a in alerts.get("alerts", []) if a["severity"] == "High"]
        if not high:
            rep.fail("alerts.json: no High alert raised for the attack")
        elif "detection" in first and ts(alerts["detection_run_utc"]) != first["detection"]:
            rep.fail("timeline detection time differs from alerts.json detection_run_utc")
        elif ts(high[0]["first_event"]) < ts(attack[0]["time_utc"]).replace(second=0):
            rep.fail("first alerted event is earlier than the attack start")
        else:
            rep.ok(f"detection: {len(high)} High alerts (rules {sorted({a['rule'] for a in high})}) "
                   "match the attack window and the timeline")
    if cont:
        if cont.get("contained") and all(a["http_status"] in (401, 403) for a in cont.get("attempts", [])):
            rep.ok("containment verified: replay of the attack refused (" +
                   ", ".join(str(a["http_status"]) for a in cont["attempts"]) + ")")
        else:
            rep.fail("containment-verification.json does not show the attack refused")
    attack_src = (root / "tools/phase4_attack.py").read_text(encoding="utf-8")
    if 'BASE = "http://127.0.0.1:3000"' in attack_src:
        rep.ok("attack script targets only the local lab shop (127.0.0.1:3000)")
    else:
        rep.fail("phase4_attack.py must target only http://127.0.0.1:3000")

    # --- Notification texts --------------------------------------------------
    a33 = (root / INC / "INC-01-art33-notification.md").read_text(encoding="utf-8") \
        if (root / INC / "INC-01-art33-notification.md").is_file() else ""
    lack33 = [m for m in ART33 if m not in a33]
    (rep.fail if lack33 else rep.ok)(
        f"Art. 33 notification: missing {lack33}" if lack33 else
        "Art. 33 notification covers 33(3)(a) to (d): nature, contact, consequences, measures")
    a34 = (root / INC / "INC-01-art34-customer-notice.md").read_text(encoding="utf-8") \
        if (root / INC / "INC-01-art34-customer-notice.md").is_file() else ""
    lack34 = [m for m in ART34 if m.lower() not in a34.lower()]
    (rep.fail if lack34 else rep.ok)(
        f"Art. 34 customer notice: missing parts {lack34}" if lack34 else
        "Art. 34 customer notice: what happened, data, consequences, advice, measures and DPO contact present")

    # --- Breach register -----------------------------------------------------
    vulns = {r["vuln_id"]: r for _, r in (read_csv(root, "03-vulnerability/vulnerability-register.csv", ["vuln_id"], rep) or [])}
    risks = {r["risk_id"] for _, r in (read_csv(root, "02-risk/risk-register.csv", ["risk_id"], rep) or [])}
    plan = {r["action_id"]: r for _, r in (read_csv(root, "02-risk/risk-treatment-plan.csv", ["action_id"], rep) or [])}
    data = load_data(root)
    pir = (root / INC / "INC-01-post-incident-review.md").read_text(encoding="utf-8") \
        if (root / INC / "INC-01-post-incident-review.md").is_file() else ""
    breaches, berr = {}, 0
    for ln, b in read_csv(root, f"{INC}/breach-register.csv", BREACH_COLS, rep) or []:
        where = f"breach-register.csv line {ln}"
        iid = b["inc_id"]
        if not re.fullmatch(r"INC-\d{2}", iid) or iid in breaches:
            rep.fail(f"{where}: bad or duplicate incident ID '{iid}'")
            berr += 1
            continue
        breaches[iid] = b
        checks = [
            (all(d in data for d in split_list(b["data_categories"])), "unknown data category"),
            (all(v in vulns for v in split_list(b["vuln_ids"])), "unknown vulnerability"),
            (all(r in risks for r in split_list(b["risk_ids"])), "unknown risk"),
            (split_list(b["resolved_by"]) and all(plan.get(c, {}).get("source") == "Incident"
                                                  for c in split_list(b["resolved_by"])),
             "resolved_by must list CAs with source 'Incident'"),
            (all(c in pir for c in split_list(b["resolved_by"])), "post-incident review does not list every resolving CA"),
        ]
        if iid == "INC-01" and "awareness" in first:
            checks.append((ts(b["awareness_utc"]) == first["awareness"], "awareness differs from the timeline"))
            checks.append((ts(b["authority_notified_utc"]) == first.get("authority-notified"),
                           "authority_notified_utc differs from the timeline"))
        for ok, msg in checks:
            if not ok:
                rep.fail(f"{where}: {iid} {msg}")
                berr += 1
    if breaches and not berr:
        rep.ok(f"breach register (Art. 33(5)): {len(breaches)} incident(s); data, vulnerabilities, risks, "
               "CAs and times consistent with the timeline and the review")
    if "## 2. Root causes" not in pir:
        rep.fail("post-incident review needs a '## 2. Root causes' section")

    # --- Traceability --------------------------------------------------------
    exp_t = {(v, i) for i, b in breaches.items() for v in split_list(b["vuln_ids"])}
    exp_r = {(i, c) for i, b in breaches.items() for c in split_list(b["resolved_by"])}
    act_t, act_r = set(), set()
    for _, row in load_traceability(root):
        if len(row) == 4 and row[1] == "triggers":
            act_t.add((row[0], row[2]))
        elif len(row) == 4 and row[1] == "resolved-by":
            act_r.add((row[0], row[2]))
    diff = (exp_t ^ act_t) | (exp_r ^ act_r)
    if diff:
        rep.fail(f"traceability.csv: triggers/resolved-by links differ from the breach register: {sorted(diff)} "
                 "(run py tools\\build_traceability.py)")
    else:
        rep.ok(f"traceability.csv: {len(act_t)} 'triggers' and {len(act_r)} 'resolved-by' links match the breach register")

    return rep.finish(root, "Phase 4 is complete. Ready for Phase 5 (Integration).")


if __name__ == "__main__":
    sys.exit(main())
