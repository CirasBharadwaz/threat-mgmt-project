#!/usr/bin/env python3
"""Phase 0 validator for the Cyber Threat Management project.

Run from the project root:
    python3 tools/validate_phase0.py
Or point it at another copy of the project:
    python3 tools/validate_phase0.py /path/to/threat-mgmt-project

Levels:
    PASS  check succeeded
    WARN  worth a look, does not block
    TODO  something only you can fill in (for example the deadline)
    FAIL  a real error; fix it before moving on (exit code 1)

Standard library only.
"""
import csv
import re
import sys
from pathlib import Path

ROOT = (
    Path(sys.argv[1]).resolve()
    if len(sys.argv) > 1
    else Path(__file__).resolve().parent.parent
)

SCOPE = "00-scope-and-setup"
REQUIRED_FILES = [
    "README.md",
    "PROGRESS.md",
    ".gitignore",
    "traceability.csv",
    f"{SCOPE}/requirements-checklist.md",
    f"{SCOPE}/scope-statement.md",
    f"{SCOPE}/asset-register.csv",
    f"{SCOPE}/data-inventory.csv",
    f"{SCOPE}/data-flow.mmd",
    f"{SCOPE}/id-scheme.md",
    f"{SCOPE}/decision-log.md",
    f"{SCOPE}/schedule.md",
    "tools/check_tools.sh",
    "tools/validate_phase0.py",
]
REQUIRED_DIRS = [
    "01-governance",
    "02-risk",
    "03-vulnerability/before",
    "03-vulnerability/after",
    "04-incident",
    "05-integration",
    "06-report",
    "appendices",
    "evidence",
]
ASSET_COLS = [
    "asset_id", "asset", "type", "owner", "data_held",
    "location", "criticality_1to5", "notes",
]
DATA_COLS = [
    "data_id", "data_category", "examples", "data_subjects", "purpose",
    "legal_basis", "storage", "access_roles", "retention", "recipients",
    "sensitivity",
]
TRACE_HEADER = ["from_id", "relation", "to_id", "note"]
ANY_ID = re.compile(r"^(A|D|POL|R|V|INC|CA|KPI)-\d{2,3}$")

results = []


def add(level, msg):
    results.append((level, msg))


def ok(msg):
    add("PASS", msg)


def warn(msg):
    add("WARN", msg)


def todo(msg):
    add("TODO", msg)


def fail(msg):
    add("FAIL", msg)


def read_csv(rel, required_cols):
    path = ROOT / rel
    if not path.is_file():
        fail(f"{rel}: file missing")
        return None
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        header = reader.fieldnames or []
        missing = [c for c in required_cols if c not in header]
        if missing:
            fail(f"{rel}: missing columns {missing}")
            return None
        rows, bad = [], 0
        for line_no, row in enumerate(reader, start=2):
            if None in row or any(v is None for v in row.values()):
                fail(f"{rel} line {line_no}: wrong number of columns")
                bad += 1
                continue
            rows.append((line_no, row))
    if not bad:
        ok(f"{rel}: {len(rows)} rows, columns OK")
    return rows


def check_structure():
    missing = [f for f in REQUIRED_FILES if not (ROOT / f).is_file()]
    if missing:
        for f in missing:
            fail(f"missing file: {f}")
    else:
        ok(f"all {len(REQUIRED_FILES)} required files present")
    missing = [d for d in REQUIRED_DIRS if not (ROOT / d).is_dir()]
    if missing:
        for d in missing:
            fail(f"missing folder: {d}")
    else:
        ok(f"all {len(REQUIRED_DIRS)} phase folders present")


def check_assets():
    rows = read_csv(f"{SCOPE}/asset-register.csv", ASSET_COLS)
    assets = {}
    if rows is None:
        return assets
    for ln, r in rows:
        where = f"asset-register.csv line {ln}"
        aid = r["asset_id"].strip()
        if not re.fullmatch(r"A-\d{2}", aid):
            fail(f"{where}: bad asset ID '{aid}' (expected A-01 style)")
            continue
        if aid in assets:
            fail(f"{where}: duplicate asset ID {aid}")
            continue
        assets[aid] = r
        crit = r["criticality_1to5"].strip()
        if not (crit.isdigit() and 1 <= int(crit) <= 5):
            fail(f"{where}: {aid} criticality must be 1 to 5, got '{crit}'")
        for col in ("asset", "type", "owner"):
            if not r[col].strip():
                fail(f"{where}: {aid} has empty '{col}'")
    if assets:
        ok(f"asset register: {len(assets)} unique, well-formed asset IDs")
    return assets


def check_data(assets):
    rows = read_csv(f"{SCOPE}/data-inventory.csv", DATA_COLS)
    data = {}
    if rows is None:
        return data
    for ln, r in rows:
        where = f"data-inventory.csv line {ln}"
        did = r["data_id"].strip()
        if not re.fullmatch(r"D-\d{2}", did):
            fail(f"{where}: bad data ID '{did}' (expected D-01 style)")
            continue
        if did in data:
            fail(f"{where}: duplicate data ID {did}")
            continue
        data[did] = r
        for col in ("data_category", "purpose", "legal_basis", "storage", "retention"):
            if not r[col].strip():
                fail(f"{where}: {did} has empty '{col}'")
        if r["sensitivity"].strip() not in ("Low", "Medium", "High"):
            fail(f"{where}: {did} sensitivity must be Low, Medium or High")
        if not re.search(r"Art\. 6\(1\)\([a-f]\)", r["legal_basis"]):
            warn(f"{where}: {did} legal basis does not cite Art. 6(1)(a-f)")
    if data:
        ok(f"data inventory: {len(data)} unique, well-formed data IDs")

    # Cross-reference: data inventory storage -> asset register
    xref_errors = 0
    for did, r in data.items():
        for aid in re.findall(r"A-\d{2}", r["storage"]):
            if aid not in assets:
                fail(f"{did}: storage references unknown asset {aid}")
                xref_errors += 1
            elif did not in re.findall(r"D-\d{2}", assets[aid]["data_held"]):
                fail(f"{did}: storage lists {aid}, but {aid} does not list {did} in data_held")
                xref_errors += 1
    # Cross-reference: asset data_held -> data inventory (both directions must agree)
    for aid, r in assets.items():
        for did in re.findall(r"D-\d{2}", r["data_held"]):
            if did not in data:
                fail(f"{aid}: data_held references unknown data category {did}")
                xref_errors += 1
            elif aid not in re.findall(r"A-\d{2}", data[did]["storage"]):
                fail(f"{aid}: data_held lists {did}, but {did} does not list {aid} in storage")
                xref_errors += 1
    if not xref_errors and assets and data:
        ok("assets and data inventory cross-reference correctly")
    return data


def check_diagram(assets):
    path = ROOT / SCOPE / "data-flow.mmd"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    if not re.match(r"(flowchart|graph)\s+(LR|RL|TD|TB|BT)\b", first):
        fail("data-flow.mmd: first line must start like 'flowchart LR'")
        return
    for a, b in (("[", "]"), ("(", ")"), ("{", "}")):
        if text.count(a) != text.count(b):
            fail(f"data-flow.mmd: unbalanced '{a}' and '{b}'")
            return
    if "-->" not in text:
        fail("data-flow.mmd: no edges found")
        return
    used = set(re.findall(r"A-\d{2}", text))
    unknown = sorted(used - set(assets))
    if unknown:
        fail(f"data-flow.mmd: references unknown assets {unknown}")
        return
    ok("data-flow.mmd: structure OK, all asset IDs exist in the register")
    absent = sorted(set(assets) - used)
    if absent:
        warn(f"assets not shown in the data flow diagram: {absent}")
    else:
        ok("every asset appears in the data flow diagram")


def check_traceability(assets, data):
    path = ROOT / "traceability.csv"
    if not path.is_file():
        return
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        header = next(reader, [])
        if header != TRACE_HEADER:
            fail(f"traceability.csv: header must be {','.join(TRACE_HEADER)}")
            return
        count, errors = 0, 0
        for line_no, row in enumerate(reader, start=2):
            if not any(c.strip() for c in row):
                continue
            count += 1
            if len(row) != 4:
                fail(f"traceability.csv line {line_no}: expected 4 columns")
                errors += 1
                continue
            for pos in (0, 2):
                ident = row[pos].strip()
                if not ANY_ID.match(ident):
                    fail(f"traceability.csv line {line_no}: bad ID '{ident}'")
                    errors += 1
                elif ident.startswith("A-") and ident not in assets:
                    fail(f"traceability.csv line {line_no}: unknown asset {ident}")
                    errors += 1
                elif ident.startswith("D-") and ident not in data:
                    fail(f"traceability.csv line {line_no}: unknown data category {ident}")
                    errors += 1
            if not row[1].strip():
                fail(f"traceability.csv line {line_no}: empty relation")
                errors += 1
    if not errors:
        ok(f"traceability.csv: header OK, {count} link(s) valid "
           "(R/V/INC/CA/POL IDs are cross-checked from the phase that creates them)")


def check_decision_log():
    path = ROOT / SCOPE / "decision-log.md"
    if not path.is_file():
        return
    entries = [
        ln for ln in path.read_text(encoding="utf-8").splitlines()
        if re.match(r"\|\s*\d{4}-\d{2}-\d{2}\s*\|", ln)
    ]
    if entries:
        ok(f"decision-log.md: {len(entries)} dated entries")
    else:
        fail("decision-log.md: no dated entries found")


def check_requirements():
    path = ROOT / SCOPE / "requirements-checklist.md"
    if not path.is_file():
        return
    fields, blanks = 0, []
    for ln in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^- (.+?):\s*(.*)$", ln)
        if m:
            fields += 1
            if not m.group(2).strip():
                blanks.append(m.group(1))
    if fields == 0:
        fail("requirements-checklist.md: no '- Label: value' lines found")
    elif blanks:
        for b in blanks:
            todo(f"requirements-checklist.md: fill in '{b}'")
    else:
        ok(f"requirements-checklist.md: all {fields} fields filled in")


def check_schedule():
    path = ROOT / SCOPE / "schedule.md"
    if not path.is_file():
        return
    rows, blank = 0, 0
    for ln in path.read_text(encoding="utf-8").splitlines():
        if re.match(r"^\|\s*\d\s*\|", ln):
            rows += 1
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) < 5 or not cells[2] or not cells[3]:
                blank += 1
    if rows != 7:
        fail(f"schedule.md: expected 7 phase rows (0 to 6), found {rows}")
    elif blank:
        todo(f"schedule.md: {blank} of 7 phases still need start/end dates (needs the deadline)")
    else:
        ok("schedule.md: all 7 phases have dates")


def main():
    if not ROOT.is_dir():
        print(f"Not a folder: {ROOT}")
        return 2
    check_structure()
    assets = check_assets()
    data = check_data(assets)
    check_diagram(assets)
    check_traceability(assets, data)
    check_decision_log()
    check_requirements()
    check_schedule()

    print(f"Phase 0 validation for: {ROOT}\n")
    for level, msg in results:
        print(f"[{level}] {msg}")
    counts = {k: sum(1 for lv, _ in results if lv == k) for k in ("PASS", "WARN", "TODO", "FAIL")}
    print(
        f"\nSummary: {counts['PASS']} passed, {counts['WARN']} warnings, "
        f"{counts['TODO']} to fill in, {counts['FAIL']} failed"
    )
    if counts["FAIL"]:
        print("Result: NOT READY. Fix every [FAIL] first.")
        return 1
    if counts["TODO"]:
        print("Result: structure is valid. Phase 0 is complete once the [TODO] items are filled in.")
    else:
        print("Result: Phase 0 is complete. Ready for Phase 1 (Governance).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
