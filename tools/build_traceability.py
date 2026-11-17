#!/usr/bin/env python3
"""Rebuild the derived links in traceability.csv.

Run from the project root:
    py tools\\build_traceability.py

Derived links are regenerated from the registers:
    POL-xx applies-to A-xx   (01-governance/policy-register.csv, applies_to)
    POL-xx governs R-xx      (02-risk/risk-register.csv, policy_ids)
    R-xx treated-by CA-xx    (02-risk/risk-register.csv, treatment_actions)
All other rows (for example V, INC and re-scores links added in later phases)
are kept unchanged. Standard library only.
"""
import csv
import sys
from pathlib import Path

DERIVED = {"applies-to", "governs", "treated-by", "exposes", "mitigates", "triggers", "resolved-by",
           "re-scores", "updates"}


def split_list(value):
    return [v.strip() for v in value.split(";") if v.strip() and v.strip() != "-"]


def read(path):
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def derived_rows(root):
    rows = []
    for p in read(root / "01-governance/policy-register.csv"):
        for a in split_list(p["applies_to"]):
            rows.append([p["policy_id"], "applies-to", a, p["title"]])
    risks = read(root / "02-risk/risk-register.csv")
    for r in risks:
        for pol in split_list(r["policy_ids"]):
            rows.append([pol, "governs", r["risk_id"], r["title"]])
    for r in risks:
        for ca in split_list(r["treatment_actions"]):
            rows.append([r["risk_id"], "treated-by", ca, "risk treatment plan"])
    vulns = read(root / "03-vulnerability/vulnerability-register.csv")
    for v in vulns:
        for rid in split_list(v["risk_ids"]):
            rows.append([v["vuln_id"], "exposes", rid, v["title"][:80]])
    for v in vulns:
        for ca in split_list(v["fix_action_ids"]):
            rows.append([ca, "mitigates", v["vuln_id"], f"vulnerability status {v['status']}"])
    incidents = read(root / "04-incident/breach-register.csv")
    for i in incidents:
        for vid in split_list(i["vuln_ids"]):
            rows.append([vid, "triggers", i["inc_id"], i["title"][:80]])
        for ca in split_list(i["resolved_by"]):
            rows.append([i["inc_id"], "resolved-by", ca, "incident corrective action"])
    for r in risks:
        for drv in split_list(r.get("rescore_drivers", "")):
            rows.append([drv, "re-scores", r["risk_id"],
                         f"{r['current_score']} -> {r['rescored_score']} ({r['rescored_on']})"])
    for p in read(root / "01-governance/policy-register.csv"):
        for ca in split_list(p.get("changed_by", "")):
            rows.append([ca, "updates", p["policy_id"], f"{p['title']} v{p['version']}"])
    return rows


def main():
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    path = root / "traceability.csv"
    kept = []
    if path.is_file():
        with path.open(newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            next(reader, None)
            kept = [row for row in reader
                    if any(c.strip() for c in row) and (len(row) < 2 or row[1].strip() not in DERIVED)]
    rows = derived_rows(root) + kept
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["from_id", "relation", "to_id", "note"])
        writer.writerows(rows)
    print(f"Wrote {len(rows)} links to {path} ({len(rows) - len(kept)} derived, {len(kept)} kept)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
