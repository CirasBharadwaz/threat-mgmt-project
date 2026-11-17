#!/usr/bin/env python3
"""Phase 5 (Integration) validator.

Run from the project root:
    py tools\\validate_phase5.py
Re-runs the Phase 4 validator (which re-runs Phases 0 to 3) first. Standard library only.
"""
import csv
import re
import sys
from datetime import date, datetime, timedelta

import build_phase5_tables
import build_risk_heatmap
from vcommon import Report, is_date, level_for, load_traceability, read_csv, root_from_argv, run_previous, split_list

INT = "05-integration"
REQUIRED_FILES = [f"{INT}/integration-summary.md", f"{INT}/risk-rescoring.md", f"{INT}/kpi-results.md",
                  "evidence/phase5/ca25-containment-narrowed.json"]
RESCORE_COLS = ["rescored_likelihood", "rescored_impact", "rescored_score", "rescored_level",
                "rescore_drivers", "rescore_basis", "rescored_on"]
KPI_TYPES = {"measured in the lab", "simulated", "derived from the register", "not measured"}


def ts(v):
    return datetime.fromisoformat(v.replace("Z", "+00:00"))


def main():
    root = root_from_argv()
    rep = Report("Phase 5 validation")
    run_previous(root, "validate_phase4.py", rep, "Phases 0 to 4")
    missing = [f for f in REQUIRED_FILES if not (root / f).is_file()]
    for f in missing:
        rep.fail(f"missing file: {f}")
    if not missing:
        rep.ok(f"all {len(REQUIRED_FILES)} Phase 5 files present")

    risks = {r["risk_id"]: r for _, r in read_csv(root, "02-risk/risk-register.csv", ["risk_id"] + RESCORE_COLS, rep) or []}
    plan = {r["action_id"]: r for _, r in read_csv(root, "02-risk/risk-treatment-plan.csv", ["action_id"], rep) or []}
    vulns = {r["vuln_id"]: r for _, r in read_csv(root, "03-vulnerability/vulnerability-register.csv", ["vuln_id"], rep) or []}
    incs = {r["inc_id"]: r for _, r in read_csv(root, "04-incident/breach-register.csv", ["inc_id"], rep) or []}
    known = set(plan) | set(vulns) | set(incs)

    # --- Re-scoring ----------------------------------------------------------
    err = 0
    for rid, r in risks.items():
        try:
            lk, im, sc = int(r["rescored_likelihood"]), int(r["rescored_impact"]), int(r["rescored_score"])
        except ValueError:
            rep.fail(f"{rid}: re-scored values must be whole numbers")
            err += 1
            continue
        if not (1 <= lk <= 5 and 1 <= im <= 5) or sc != lk * im or r["rescored_level"] != level_for(sc):
            rep.fail(f"{rid}: re-scored {lk} x {im} = {sc} {r['rescored_level']} is inconsistent with POL-09")
            err += 1
        drivers = split_list(r["rescore_drivers"])
        bad = [d for d in drivers if d not in known]
        if bad:
            rep.fail(f"{rid}: unknown re-score drivers {bad}")
            err += 1
        if sc != int(r["current_score"]) and not drivers:
            rep.fail(f"{rid}: score changed but no driver (CA, V or INC) is named")
            err += 1
        if len(r["rescore_basis"]) < 20 or not is_date(r["rescored_on"]):
            rep.fail(f"{rid}: re-score basis or date missing")
            err += 1
        # honesty rule: a risk exposed by an OPEN vulnerability must not be scored below its Phase 2 score
        open_v = [v for v, row in vulns.items() if rid in split_list(row["risk_ids"]) and row["status"] == "Open"]
        if open_v and sc < int(r["current_score"]):
            rep.fail(f"{rid}: re-scored below Phase 2 although {open_v} is still open")
            err += 1
        if r["rescored_level"] in ("High", "Critical"):
            open_ca = [c for c in split_list(r["treatment_actions"]) if plan.get(c, {}).get("status") != "Done"]
            if not open_ca and "Managing Director" not in r["acceptance"]:
                rep.fail(f"{rid}: re-scored {r['rescored_level']} but no open action and no acceptance")
                err += 1
        if r["rescored_level"] == "Critical":
            m = re.search(r"Managing Director until (\d{4}-\d{2}-\d{2})", r["acceptance"])
            if not m or date.fromisoformat(m.group(1)) - date.fromisoformat(r["rescored_on"]) > timedelta(days=60):
                rep.fail(f"{rid}: Critical after re-scoring needs a Managing Director exception of at most 60 days (POL-09)")
                err += 1
    if risks and not err:
        changed = sum(r["rescored_score"] != r["current_score"] for r in risks.values())
        rep.ok(f"re-scoring: {len(risks)} risks, {changed} changed; scores, levels, drivers and POL-09 rules consistent")
    v05 = vulns.get("V-05")
    if v05 and v05["status"] == "Open":
        r03 = risks.get("R-03", {})
        (rep.ok if r03 and int(r03["rescored_score"]) >= int(r03["current_score"]) else rep.fail)(
            "honesty check: V-05 is open and R-03 is not scored as fixed "
            f"({r03.get('current_score')} -> {r03.get('rescored_score')})")

    hm = root / "02-risk/risk-heatmap.md"
    if hm.is_file() and "## After: re-scored" in hm.read_text(encoding="utf-8") and \
            hm.read_text(encoding="utf-8").replace("\r\n", "\n") == build_risk_heatmap.render(root):
        rep.ok("heat map shows before, after (re-scored) and target, and matches the register")
    else:
        rep.fail("risk-heatmap.md missing the re-scored grid or out of date; run py tools\\build_risk_heatmap.py")
    for name, fn in (("risk-rescoring.md", build_phase5_tables.render_rescoring),
                     ("kpi-results.md", build_phase5_tables.render_kpis)):
        p = root / INT / name
        if p.is_file() and p.read_text(encoding="utf-8").replace("\r\n", "\n") == fn(root):
            rep.ok(f"{name} matches the registers")
        else:
            rep.fail(f"{name} is out of date; run py tools\\build_phase5_tables.py")

    # --- KPIs ----------------------------------------------------------------
    kpis = {r["kpi_id"]: r for _, r in read_csv(root, "01-governance/kpi-register.csv",
                                                 ["kpi_id", "measured_value", "value_type", "evidence"], rep) or []}
    kerr = 0
    for kid, k in kpis.items():
        if k["value_type"] not in KPI_TYPES:
            rep.fail(f"{kid}: value_type must be one of {sorted(KPI_TYPES)}")
            kerr += 1
        elif k["value_type"] != "not measured":
            if k["measured_value"] in ("", "-") or any(not (root / e).is_file() for e in split_list(k["evidence"])) \
                    or not split_list(k["evidence"]):
                rep.fail(f"{kid}: measured value or evidence file missing")
                kerr += 1
    with (root / "04-incident/INC-01-timeline.csv").open(newline="", encoding="utf-8") as fh:
        tl = list(csv.DictReader(fh))
    first = {}
    for e in tl:
        first.setdefault(e["event_type"], ts(e["time_utc"]))
    det = int((first["detection"] - first["attack-start"]).total_seconds())
    dec = int((first["notification-decision"] - first["awareness"]).total_seconds())
    for kid, secs, typ in (("KPI-06", det, "measured in the lab"), ("KPI-05", dec, "simulated")):
        k = kpis.get(kid, {})
        if not k.get("measured_value", "").startswith(f"{secs} s") or k.get("value_type") != typ:
            rep.fail(f"{kid}: expected '{secs} s ...' labelled '{typ}' (from the timeline), got "
                     f"'{k.get('measured_value')}' / '{k.get('value_type')}'")
            kerr += 1
    if kpis and not kerr:
        rep.ok(f"KPI register: values labelled; KPI-06 = {det} s and KPI-05 = {dec} s match the timeline")

    # --- Policy updates and traceability -------------------------------------
    pols = {r["policy_id"]: r for _, r in read_csv(root, "01-governance/policy-register.csv", ["policy_id", "changed_by"], rep) or []}
    perr = 0
    for pid in ("POL-04", "POL-05"):
        p = pols.get(pid, {})
        text = (root / "01-governance" / p.get("file", "x")).read_text(encoding="utf-8") \
            if (root / "01-governance" / p.get("file", "x")).is_file() else ""
        if p.get("version") != "1.1" or "| Version | 1.1 |" not in text or "## Change history" not in text \
                or not re.search(r"^\| 1\.1 \|", text, re.M):
            rep.fail(f"{pid}: must be version 1.1 in the register and the file, with a change history row")
            perr += 1
        for ca in split_list(p.get("changed_by", "")):
            if plan.get(ca, {}).get("source") != "Incident":
                rep.fail(f"{pid}: changed_by {ca} is not an incident corrective action")
                perr += 1
    if not perr:
        rep.ok("POL-04 and POL-05 are version 1.1 with change history, changed by incident CAs")
    links = {(r[0], r[1], r[2]) for _, r in load_traceability(root) if len(r) == 4}
    exp_rs = {(d, "re-scores", rid) for rid, r in risks.items() for d in split_list(r["rescore_drivers"])}
    exp_up = {(c, "updates", pid) for pid, p in pols.items() for c in split_list(p.get("changed_by", ""))}
    act_rs = {x for x in links if x[1] == "re-scores"}
    act_up = {x for x in links if x[1] == "updates"}
    if exp_rs == act_rs and exp_up == act_up:
        rep.ok(f"traceability.csv: {len(act_rs)} 're-scores' and {len(act_up)} 'updates' links match the registers")
    else:
        rep.fail("traceability.csv re-scores/updates links differ from the registers; run py tools\\build_traceability.py")
    chain = [c for c in ("CA-24", "CA-25") if ("INC-01", "resolved-by", c) in links
             and any(x[0] == c and x[1] == "updates" for x in links)]
    (rep.ok if chain == ["CA-24", "CA-25"] else rep.fail)(
        f"closed loop INC-01 -> {', '.join(chain) or 'none'} -> POL present in traceability.csv")

    # --- Art. 34 reasoning and honesty statements ----------------------------
    ba = (root / "04-incident/INC-01-breach-assessment.md").read_text(encoding="utf-8")
    need = ["Art. 34 reasoning", "9/2022", "masked", "20,000", "identif", "could decide differently"]
    lack = [n for n in need if n not in ba]
    (rep.fail if lack else rep.ok)(f"breach assessment Art. 34 reasoning missing {lack}" if lack else
                                   "breach assessment: Art. 34 reasoning covers data, secrets, scale, identification, "
                                   "EDPB 9/2022 and the alternative view")
    summ = (root / INT / "integration-summary.md").read_text(encoding="utf-8") if (root / INT / "integration-summary.md").is_file() else ""
    (rep.ok if "compressed lab simulation" in summ and "UTC" in summ else rep.fail)(
        "integration summary states that the timeline is a compressed lab simulation and that times are UTC")
    log = (root / "00-scope-and-setup/decision-log.md").read_text(encoding="utf-8")
    (rep.ok if "v1.1" in log and "re-scor" in log else rep.fail)("decision log records the policy versions and the re-scoring")
    return rep.finish(root, "Phase 5 is complete. Ready for Phase 6 (Report).")


if __name__ == "__main__":
    sys.exit(main())
