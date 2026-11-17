#!/usr/bin/env python3
"""Phase 2 (Risk management) validator.

Run from the project root:
    py tools\\validate_phase2.py
Re-runs the Phase 1 validator (which re-runs Phase 0) first. Standard library only.
"""
import re
import sys

import build_risk_heatmap
from vcommon import (
    Report, check_iso_ref, csv_header, ids_in, is_date, level_for, load_assets,
    load_data, load_traceability, read_csv, root_from_argv, run_previous, split_list,
)

RISK = "02-risk"
REQUIRED_FILES = [
    f"{RISK}/risk-register.csv",
    f"{RISK}/risk-treatment-plan.csv",
    f"{RISK}/risk-heatmap.md",
    f"{RISK}/dpia.md",
    f"{RISK}/risk-assessment-summary.md",
]
RISK_COLS = ["risk_id", "title", "threat", "weakness", "consequence", "assets", "data",
             "policy_ids", "risk_owner", "existing_controls", "current_likelihood",
             "current_impact", "current_score", "current_level", "treatment",
             "treatment_actions", "target_likelihood", "target_impact", "target_score",
             "target_level", "acceptance", "status", "review_date"]
PLAN_COLS = ["action_id", "title", "description", "risk_ids", "policy_ids", "iso_controls",
             "owner", "due_date", "status", "source", "notes"]
TREATMENTS = {"Reduce", "Transfer", "Avoid", "Accept"}
RISK_STATUS = {"Open", "Accepted", "Closed", "Withdrawn"}
CA_STATUS = {"Planned", "In progress", "Done", "Withdrawn"}
CA_SOURCE = {"Risk treatment", "Vulnerability management", "Incident"}
DPIA_MARKERS = ["Art. 35(7)(a)", "Art. 35(7)(b)", "Art. 35(7)(c)", "Art. 35(7)(d)", "Art. 35(2)"]


def score_block(rep, where, rid, r, prefix):
    """Validate likelihood, impact, score and level for 'current' or 'target'."""
    try:
        lk, im, sc = (int(r[f"{prefix}_likelihood"]), int(r[f"{prefix}_impact"]),
                      int(r[f"{prefix}_score"]))
    except ValueError:
        rep.fail(f"{where}: {rid} {prefix} likelihood, impact and score must be whole numbers")
        return None
    ok = True
    if not (1 <= lk <= 5 and 1 <= im <= 5):
        rep.fail(f"{where}: {rid} {prefix} likelihood and impact must be 1 to 5")
        ok = False
    if sc != lk * im:
        rep.fail(f"{where}: {rid} {prefix}_score {sc} is not {lk} x {im} = {lk * im}")
        ok = False
    if r[f"{prefix}_level"] != level_for(lk * im):
        rep.fail(f"{where}: {rid} {prefix}_level '{r[prefix + '_level']}' should be "
                 f"'{level_for(lk * im)}' for score {lk * im} (POL-09)")
        ok = False
    return lk * im if ok else None


def main():
    root = root_from_argv()
    rep = Report("Phase 2 validation")
    run_previous(root, "validate_phase1.py", rep, "Phase 1 (and Phase 0)")

    missing = [f for f in REQUIRED_FILES if not (root / f).is_file()]
    for f in missing:
        rep.fail(f"missing file: {f}")
    if not missing:
        rep.ok(f"all {len(REQUIRED_FILES)} Phase 2 files present")

    assets, data = load_assets(root), load_data(root)
    roles = csv_header(root, "01-governance/raci-matrix.csv")[2:]
    pol_rows = read_csv(root, "01-governance/policy-register.csv", ["policy_id"], rep) or []
    policies = {r["policy_id"] for _, r in pol_rows}

    # --- Risk register -------------------------------------------------------
    risks = {}
    reg = read_csv(root, f"{RISK}/risk-register.csv", RISK_COLS, rep) or []
    errors = 0
    for ln, r in reg:
        where = f"risk-register.csv line {ln}"
        rid = r["risk_id"]
        if not re.fullmatch(r"R-\d{2}", rid) or rid in risks:
            rep.fail(f"{where}: bad or duplicate risk ID '{rid}'")
            errors += 1
            continue
        risks[rid] = r
        for col in ("title", "threat", "weakness", "consequence", "existing_controls"):
            if not r[col]:
                rep.fail(f"{where}: {rid} has empty '{col}'")
                errors += 1
        for col, known, label in (("assets", assets, "asset"), ("data", data, "data category"),
                                  ("policy_ids", policies, "policy")):
            vals = split_list(r[col])
            if not vals:
                rep.fail(f"{where}: {rid} lists no {label}")
                errors += 1
            for v in vals:
                if v not in known:
                    rep.fail(f"{where}: {rid} references unknown {label} {v}")
                    errors += 1
        if r["risk_owner"] not in roles:
            rep.fail(f"{where}: {rid} risk_owner '{r['risk_owner']}' is not a RACI role")
            errors += 1
        cur = score_block(rep, where, rid, r, "current")
        tgt = score_block(rep, where, rid, r, "target")
        if cur is None or tgt is None:
            errors += 1
        elif tgt > cur:
            rep.fail(f"{where}: {rid} target score {tgt} is higher than current score {cur}")
            errors += 1
        if r["treatment"] not in TREATMENTS:
            rep.fail(f"{where}: {rid} treatment must be one of {sorted(TREATMENTS)}")
            errors += 1
        actions = split_list(r["treatment_actions"])
        accepted = r["acceptance"] not in ("", "-")
        if r["treatment"] == "Accept":
            if actions:
                rep.fail(f"{where}: {rid} is accepted but lists treatment actions")
                errors += 1
            if not accepted:
                rep.fail(f"{where}: {rid} is accepted but 'acceptance' does not say who accepted it")
                errors += 1
            if r["current_level"] in ("High", "Critical") and "Managing Director" not in r["acceptance"]:
                rep.fail(f"{where}: {rid} is {r['current_level']}; only the Managing Director may accept it (POL-09)")
                errors += 1
        elif not actions:
            rep.fail(f"{where}: {rid} treatment '{r['treatment']}' needs at least one CA-xx action")
            errors += 1
        if r["target_level"] in ("High", "Critical") and "Managing Director" not in r["acceptance"]:
            rep.fail(f"{where}: {rid} target level {r['target_level']} is outside appetite; "
                     "needs written acceptance by the Managing Director (POL-09)")
            errors += 1
        if accepted and r["current_level"] in ("High", "Critical") \
                and "Managing Director" not in r["acceptance"]:
            rep.fail(f"{where}: {rid} exception for a {r['current_level']} risk must be accepted "
                     "by the Managing Director (POL-09)")
            errors += 1
        if r["status"] not in RISK_STATUS:
            rep.fail(f"{where}: {rid} status must be one of {sorted(RISK_STATUS)}")
            errors += 1
        if not is_date(r["review_date"]):
            rep.fail(f"{where}: {rid} review_date is not a YYYY-MM-DD date")
            errors += 1
    if risks and not errors:
        rep.ok(f"risk register: {len(risks)} risks; scores, levels, owners, links and "
               "appetite rules consistent with POL-09")

    # --- Treatment plan ------------------------------------------------------
    plan = {}
    rows = read_csv(root, f"{RISK}/risk-treatment-plan.csv", PLAN_COLS, rep) or []
    perr = 0
    for ln, r in rows:
        where = f"risk-treatment-plan.csv line {ln}"
        cid = r["action_id"]
        if not re.fullmatch(r"CA-\d{2}", cid) or cid in plan:
            rep.fail(f"{where}: bad or duplicate action ID '{cid}'")
            perr += 1
            continue
        plan[cid] = r
        for rid in split_list(r["risk_ids"]):
            if rid not in risks:
                rep.fail(f"{where}: {cid} references unknown risk {rid}")
                perr += 1
        for pid in split_list(r["policy_ids"]):
            if pid not in policies:
                rep.fail(f"{where}: {cid} references unknown policy {pid}")
                perr += 1
        bad_iso = [c for c in split_list(r["iso_controls"]) if not check_iso_ref(c)]
        if bad_iso or not split_list(r["iso_controls"]):
            rep.fail(f"{where}: {cid} has missing or invalid ISO/IEC 27001:2022 controls {bad_iso}")
            perr += 1
        if r["owner"] not in roles:
            rep.fail(f"{where}: {cid} owner '{r['owner']}' is not a RACI role")
            perr += 1
        if not is_date(r["due_date"]):
            rep.fail(f"{where}: {cid} due_date is not a YYYY-MM-DD date")
            perr += 1
        if r["status"] not in CA_STATUS or r["source"] not in CA_SOURCE:
            rep.fail(f"{where}: {cid} status or source not allowed")
            perr += 1
    # two-way consistency register <-> plan
    for rid, r in risks.items():
        for cid in split_list(r["treatment_actions"]):
            if cid not in plan:
                rep.fail(f"{rid} lists {cid}, which is not in the treatment plan")
                perr += 1
            elif rid not in split_list(plan[cid]["risk_ids"]):
                rep.fail(f"{rid} lists {cid}, but {cid} does not list {rid} in risk_ids")
                perr += 1
    for cid, r in plan.items():
        for rid in split_list(r["risk_ids"]):
            if rid in risks and cid not in split_list(risks[rid]["treatment_actions"]):
                rep.fail(f"{cid} lists {rid}, but {rid} does not list {cid} in treatment_actions")
                perr += 1
        if not split_list(r["risk_ids"]):
            rep.fail(f"{cid} is not linked to any risk")
            perr += 1
    if plan and not perr:
        rep.ok(f"treatment plan: {len(plan)} actions; owners, dates and ISO controls valid; "
               "register and plan agree in both directions")

    hc = [rid for rid, r in risks.items() if r["current_level"] in ("High", "Critical")]
    covered = [rid for rid in hc if split_list(risks[rid]["treatment_actions"])]
    if hc:
        pct = round(100 * len(covered) / len(hc))
        (rep.ok if pct == 100 else rep.fail)(
            f"KPI-10: {len(covered)} of {len(hc)} High and Critical risks have a treatment plan ({pct}%)")

    # --- Heat map up to date -------------------------------------------------
    hm = root / RISK / "risk-heatmap.md"
    if hm.is_file() and risks:
        if hm.read_text(encoding="utf-8").replace("\r\n", "\n") == build_risk_heatmap.render(root):
            rep.ok("risk-heatmap.md matches the register")
        else:
            rep.fail("risk-heatmap.md is out of date; run: py tools\\build_risk_heatmap.py")

    # --- Summary counts match ------------------------------------------------
    summ = root / RISK / "risk-assessment-summary.md"
    if summ.is_file() and risks:
        text = summ.read_text(encoding="utf-8")
        mism = []
        for level in ("Critical", "High", "Medium", "Low"):
            m = re.search(rf"^\|\s*{level}\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|", text, re.M)
            cur = sum(1 for r in risks.values() if r["current_level"] == level)
            tgt = sum(1 for r in risks.values() if r["target_level"] == level)
            if not m or (int(m.group(1)), int(m.group(2))) != (cur, tgt):
                mism.append(f"{level} should be {cur}/{tgt}")
        if mism:
            rep.fail(f"risk-assessment-summary.md counts differ from the register: {mism}")
        else:
            rep.ok("risk-assessment-summary.md counts match the register")

    # --- DPIA ----------------------------------------------------------------
    dpia_path = root / RISK / "dpia.md"
    if dpia_path.is_file():
        dt = dpia_path.read_text(encoding="utf-8")
        lacking = [m for m in DPIA_MARKERS if m not in dt]
        if lacking:
            rep.fail(f"dpia.md: missing required parts {lacking}")
        else:
            rep.ok("dpia.md: covers Art. 35(7)(a) to (d) and the DPO's advice (Art. 35(2))")
        uncovered = sorted(rid for rid, r in risks.items() if split_list(r["data"]) and rid not in dt)
        if uncovered:
            rep.fail(f"dpia.md: risks involving personal data not assessed: {uncovered}")
        else:
            rep.ok("dpia.md: every risk that involves personal data is assessed for data subjects")

    # --- R and CA IDs used anywhere in Phase 1 and 2 documents --------------
    dangling = 0
    for folder in ("01-governance", RISK):
        for p in (root / folder).rglob("*"):
            if p.suffix not in (".md", ".csv"):
                continue
            text = p.read_text(encoding="utf-8")
            for kind, known in (("R", risks), ("CA", plan)):
                for ident in sorted(set(ids_in(text, kind)) - set(known)):
                    rep.fail(f"{p.relative_to(root).as_posix()}: references unknown {kind} ID {ident}")
                    dangling += 1
    if not dangling:
        rep.ok("Phase 1 and 2 documents reference only existing R and CA IDs")

    # --- Traceability: governs and treated-by --------------------------------
    exp_gov = {(p, rid) for rid, r in risks.items() for p in split_list(r["policy_ids"])}
    exp_trt = {(rid, c) for rid, r in risks.items() for c in split_list(r["treatment_actions"])}
    act_gov, act_trt, terr = set(), set(), 0
    for ln, row in load_traceability(root):
        if len(row) != 4:
            continue
        for ident in (row[0], row[2]):
            if (ident.startswith("R-") and ident not in risks) or \
                    (ident.startswith("CA-") and ident not in plan):
                rep.fail(f"traceability.csv line {ln}: unknown ID {ident}")
                terr += 1
        if row[1] == "governs":
            act_gov.add((row[0], row[2]))
        elif row[1] == "treated-by":
            act_trt.add((row[0], row[2]))
    for label, exp, act in (("governs", exp_gov, act_gov), ("treated-by", exp_trt, act_trt)):
        for a, b in sorted(exp - act):
            rep.fail(f"traceability.csv: missing '{a} {label} {b}'")
            terr += 1
        for a, b in sorted(act - exp):
            rep.fail(f"traceability.csv: '{a} {label} {b}' is not in the risk register")
            terr += 1
    if not terr:
        rep.ok(f"traceability.csv: {len(act_gov)} 'governs' and {len(act_trt)} 'treated-by' "
               "links match the register")

    # --- Deliberate weak spot picked up as a risk ---------------------------
    weak = [rid for rid, r in risks.items()
            if {"A-02", "A-04"} <= set(split_list(r["assets"]))
            and "POL-04" in split_list(r["policy_ids"])
            and re.search(r"admin", r["weakness"], re.I)]
    if weak:
        rep.ok(f"deliberate weak spot (support admin rights on A-02) is tracked as {', '.join(weak)}")
    else:
        rep.fail("no risk covers the support admin rights on A-02 (assets A-02 and A-04, POL-04)")

    return rep.finish(root, "Phase 2 is complete. Ready for Phase 3 (Vulnerability management).")


if __name__ == "__main__":
    sys.exit(main())
