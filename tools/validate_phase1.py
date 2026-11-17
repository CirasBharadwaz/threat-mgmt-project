#!/usr/bin/env python3
"""Phase 1 (Governance) validator.

Run from the project root:
    py tools\\validate_phase1.py
Re-runs the Phase 0 validator first. Standard library only.
"""
import re
import sys

from vcommon import (
    NIST_CATEGORIES, Report, check_iso_ref, csv_header, ids_in, is_date,
    load_assets, load_data, load_traceability, read_csv, root_from_argv,
    run_previous, split_list,
)

GOV = "01-governance"
REQUIRED_FILES = [
    f"{GOV}/governance-structure.md",
    f"{GOV}/raci-matrix.csv",
    f"{GOV}/policy-register.csv",
    f"{GOV}/framework-mapping.csv",
    f"{GOV}/kpi-register.csv",
    f"{GOV}/gdpr-baseline-gap-assessment.md",
]
POLICY_COLS = ["policy_id", "title", "owner", "approver", "applies_to", "format",
               "status", "version", "approved_on", "next_review", "file"]
MAPPING_COLS = ["policy_id", "framework", "reference", "title"]
KPI_COLS = ["kpi_id", "name", "definition", "formula", "target", "frequency",
            "data_source", "owner", "policy_id", "measured_in_phase", "baseline"]
REQUIRED_SECTIONS = ["Purpose", "Scope", "Roles", "Policy statements", "Compliance", "Review"]
WORD_RANGES = {"full": (800, 3000), "concise": (350, 1100), "one-page": (150, 500)}
RACI_VALUES = {"", "R", "A", "C", "I", "A/R"}


def main():
    root = root_from_argv()
    rep = Report("Phase 1 validation")
    run_previous(root, "validate_phase0.py", rep, "Phase 0")

    missing = [f for f in REQUIRED_FILES if not (root / f).is_file()]
    for f in missing:
        rep.fail(f"missing file: {f}")
    if not missing:
        rep.ok(f"all {len(REQUIRED_FILES)} Phase 1 files present")

    assets, data = load_assets(root), load_data(root)
    gov_text = (root / GOV / "governance-structure.md").read_text(encoding="utf-8") \
        if (root / GOV / "governance-structure.md").is_file() else ""

    # --- RACI ---------------------------------------------------------------
    header = csv_header(root, f"{GOV}/raci-matrix.csv")
    roles = header[2:] if header[:2] == ["activity", "policy_id"] else []
    if not roles:
        rep.fail("raci-matrix.csv: header must start with activity,policy_id followed by roles")
    else:
        absent = [r for r in roles if r not in gov_text]
        if absent:
            rep.fail(f"raci-matrix.csv roles not defined in governance-structure.md: {absent}")
        else:
            rep.ok(f"RACI: all {len(roles)} roles are defined in governance-structure.md")
    policies = {}
    prow = read_csv(root, f"{GOV}/policy-register.csv", POLICY_COLS, rep) or []
    for ln, r in prow:
        policies[r["policy_id"]] = (ln, r)

    raci = read_csv(root, f"{GOV}/raci-matrix.csv", ["activity", "policy_id"], rep) or []
    raci_errors = 0
    for ln, r in raci:
        cells = [r.get(role, "") for role in roles]
        bad = [c for c in cells if c not in RACI_VALUES]
        a_count = sum(1 for c in cells if "A" in c)
        r_count = sum(1 for c in cells if "R" in c)
        where = f"raci-matrix.csv line {ln} ({r['activity']})"
        if bad:
            rep.fail(f"{where}: invalid values {bad}; use R, A, C, I or A/R")
            raci_errors += 1
        if a_count != 1:
            rep.fail(f"{where}: needs exactly one A, found {a_count}")
            raci_errors += 1
        if r_count < 1:
            rep.fail(f"{where}: needs at least one R")
            raci_errors += 1
        if r["policy_id"] not in policies:
            rep.fail(f"{where}: unknown policy {r['policy_id']}")
            raci_errors += 1
    if raci and not raci_errors:
        rep.ok(f"RACI: {len(raci)} activities, each with exactly one A and at least one R")

    # --- Policy register and policy files ----------------------------------
    pol_errors = 0
    seen = set()
    for pid, (ln, r) in policies.items():
        where = f"policy-register.csv line {ln}"
        if not re.fullmatch(r"POL-\d{2}", pid):
            rep.fail(f"{where}: bad policy ID '{pid}'")
            pol_errors += 1
            continue
        if pid in seen:
            rep.fail(f"{where}: duplicate {pid}")
            pol_errors += 1
        seen.add(pid)
        for col in ("owner", "approver"):
            if r[col] not in roles:
                rep.fail(f"{where}: {pid} {col} '{r[col]}' is not a RACI role")
                pol_errors += 1
        unknown = [a for a in split_list(r["applies_to"]) if a not in assets]
        if unknown or not split_list(r["applies_to"]):
            rep.fail(f"{where}: {pid} applies_to has unknown or no assets {unknown}")
            pol_errors += 1
        if r["format"] not in WORD_RANGES:
            rep.fail(f"{where}: {pid} format must be one of {list(WORD_RANGES)}")
            pol_errors += 1
        for col in ("approved_on", "next_review"):
            if not is_date(r[col]):
                rep.fail(f"{where}: {pid} {col} is not a YYYY-MM-DD date")
                pol_errors += 1
        path = root / GOV / r["file"]
        if not path.is_file():
            rep.fail(f"{where}: {pid} file missing: {GOV}/{r['file']}")
            pol_errors += 1
            continue
        text = path.read_text(encoding="utf-8")
        first = text.lstrip().splitlines()[0] if text.strip() else ""
        if not first.startswith(f"# {pid} "):
            rep.fail(f"{r['file']}: first heading must start with '# {pid} '")
            pol_errors += 1
        if not re.search(rf"\|\s*Policy ID\s*\|\s*{pid}\s*\|", text):
            rep.fail(f"{r['file']}: header table must state Policy ID {pid}")
            pol_errors += 1
        m = re.search(r"\|\s*Owner\s*\|\s*([^|]+?)\s*\|", text)
        if not m or m.group(1) != r["owner"]:
            rep.fail(f"{r['file']}: owner in header ({m.group(1) if m else 'none'}) "
                     f"differs from register ({r['owner']})")
            pol_errors += 1
        missing_sec = [s for s in REQUIRED_SECTIONS
                       if not re.search(rf"^##\s+{re.escape(s)}\s*$", text, re.M)]
        if missing_sec:
            rep.fail(f"{r['file']}: missing sections {missing_sec}")
            pol_errors += 1
        words = len(re.findall(r"\w+", text))
        low, high = WORD_RANGES.get(r["format"], (0, 10**9))
        if not low <= words <= high:
            rep.warn(f"{pid}: {words} words is outside the '{r['format']}' range {low}-{high}")
        else:
            rep.ok(f"{pid}: sections complete, {words} words ({r['format']})")
    if policies and not pol_errors:
        rep.ok(f"policy register: {len(policies)} policies; IDs, owners, assets, dates and files consistent")

    # --- Framework mapping ---------------------------------------------------
    mapping = read_csv(root, f"{GOV}/framework-mapping.csv", MAPPING_COLS, rep) or []
    coverage = {pid: set() for pid in policies}
    map_errors = 0
    for ln, r in mapping:
        where = f"framework-mapping.csv line {ln}"
        fw, ref = r["framework"], r["reference"]
        if r["policy_id"] not in policies:
            rep.fail(f"{where}: unknown policy {r['policy_id']}")
            map_errors += 1
            continue
        valid = (
            (fw == "ISO/IEC 27001:2022" and check_iso_ref(ref))
            or (fw == "NIST CSF 2.0" and ref in NIST_CATEGORIES)
            or (fw == "GDPR" and re.fullmatch(r"Art\. (\d{1,2})", ref) and 1 <= int(ref[5:]) <= 99)
            or (fw in ("BDSG", "TDDDG") and re.fullmatch(r"§ \d+", ref))
        )
        if not valid:
            rep.fail(f"{where}: invalid reference '{ref}' for framework '{fw}'")
            map_errors += 1
            continue
        coverage[r["policy_id"]].add("ISO" if fw.startswith("ISO") else
                                     "NIST" if fw.startswith("NIST") else "LAW")
    for pid, kinds in coverage.items():
        lacking = {"ISO", "NIST", "LAW"} - kinds
        if lacking:
            rep.fail(f"framework-mapping.csv: {pid} has no mapping for {sorted(lacking)}")
            map_errors += 1
    if mapping and not map_errors:
        rep.ok(f"framework mapping: {len(mapping)} valid references; every policy maps to "
               "ISO/IEC 27001:2022, NIST CSF 2.0 and GDPR/BDSG")

    # --- KPI register --------------------------------------------------------
    kpis = read_csv(root, f"{GOV}/kpi-register.csv", KPI_COLS, rep) or []
    kpi_errors, kpi_ids = 0, set()
    for ln, r in kpis:
        where = f"kpi-register.csv line {ln}"
        if not re.fullmatch(r"KPI-\d{2}", r["kpi_id"]) or r["kpi_id"] in kpi_ids:
            rep.fail(f"{where}: bad or duplicate KPI ID '{r['kpi_id']}'")
            kpi_errors += 1
        kpi_ids.add(r["kpi_id"])
        if r["policy_id"] not in policies:
            rep.fail(f"{where}: unknown policy {r['policy_id']}")
            kpi_errors += 1
        if r["owner"] not in roles:
            rep.fail(f"{where}: owner '{r['owner']}' is not a RACI role")
            kpi_errors += 1
        if not re.fullmatch(r"Phase [0-6]", r["measured_in_phase"]):
            rep.fail(f"{where}: measured_in_phase must be 'Phase N'")
            kpi_errors += 1
    if kpis and not kpi_errors:
        rep.ok(f"KPI register: {len(kpis)} KPIs with valid IDs, owners and policies")

    # --- IDs used in Phase 1 documents --------------------------------------
    texts = {p.relative_to(root).as_posix(): p.read_text(encoding="utf-8")
             for p in (root / GOV).rglob("*") if p.suffix in (".md", ".csv")}
    known = {"A": set(assets), "D": set(data), "POL": set(policies), "KPI": kpi_ids}
    dangling = 0
    for rel, text in texts.items():
        for kind, ids in known.items():
            for ident in sorted(set(ids_in(text, kind)) - ids):
                rep.fail(f"{rel}: references unknown {kind} ID {ident}")
                dangling += 1
    if not dangling:
        rep.ok("Phase 1 documents reference only existing A, D, POL and KPI IDs "
               "(R and CA references are checked by validate_phase2.py)")

    # --- Traceability: POL applies-to A -------------------------------------
    expected = {(pid, a) for pid, (_, r) in policies.items() for a in split_list(r["applies_to"])}
    actual = set()
    trace_errors = 0
    for ln, row in load_traceability(root):
        if len(row) != 4:
            continue  # Phase 0 validator reports this
        if row[0].startswith("POL-") and row[0] not in policies:
            rep.fail(f"traceability.csv line {ln}: unknown policy {row[0]}")
            trace_errors += 1
        if row[1] == "applies-to":
            actual.add((row[0], row[2]))
    for pair in sorted(expected - actual):
        rep.fail(f"traceability.csv: missing '{pair[0]} applies-to {pair[1]}' (from policy register)")
        trace_errors += 1
    for pair in sorted(actual - expected):
        rep.fail(f"traceability.csv: '{pair[0]} applies-to {pair[1]}' is not in the policy register")
        trace_errors += 1
    if not trace_errors:
        rep.ok(f"traceability.csv: {len(actual)} 'applies-to' links match the policy register")

    # --- Deliberate weak spot is picked up by POL-04 -----------------------
    pol04 = policies.get("POL-04")
    if pol04 and (root / GOV / pol04[1]["file"]).is_file():
        t = (root / GOV / pol04[1]["file"]).read_text(encoding="utf-8")
        if "A-02" in t and re.search(r"admin", t, re.I) and "R-01" in t:
            rep.ok("POL-04 records the deliberate weak spot (support admin rights on A-02, R-01)")
        else:
            rep.fail("POL-04 must record the support admin rights on A-02 as a known gap linked to R-01")

    return rep.finish(root, "Phase 1 is complete. Ready for Phase 2 (Risk management).")


if __name__ == "__main__":
    sys.exit(main())
