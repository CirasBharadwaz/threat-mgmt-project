"""Shared helpers for the phase validators (standard library only)."""
import csv
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ID_PATTERNS = {
    "A": r"A-\d{2}",
    "D": r"D-\d{2}",
    "POL": r"POL-\d{2}",
    "R": r"R-\d{2}",
    "V": r"V-\d{2,3}",
    "INC": r"INC-\d{2}",
    "CA": r"CA-\d{2}",
    "KPI": r"KPI-\d{2}",
}
ANY_ID = re.compile(r"^(A|D|POL|R|V|INC|CA|KPI)-\d{2,3}$")

# ISO/IEC 27001:2022 Annex A: number of controls per theme
ISO_ANNEX_A = {5: 37, 6: 8, 7: 14, 8: 34}
NIST_CATEGORIES = {
    "GV.OC", "GV.RM", "GV.RR", "GV.PO", "GV.OV", "GV.SC",
    "ID.AM", "ID.RA", "ID.IM",
    "PR.AA", "PR.AT", "PR.DS", "PR.PS", "PR.IR",
    "DE.CM", "DE.AE",
    "RS.MA", "RS.AN", "RS.CO", "RS.MI",
    "RC.RP", "RC.CO",
}
LEVELS = [(1, 4, "Low"), (5, 9, "Medium"), (10, 16, "High"), (20, 25, "Critical")]


def level_for(score):
    for low, high, name in LEVELS:
        if low <= score <= high:
            return name
    return None


class Report:
    def __init__(self, title):
        self.title = title
        self.results = []

    def add(self, level, msg):
        self.results.append((level, msg))

    def ok(self, msg):
        self.add("PASS", msg)

    def warn(self, msg):
        self.add("WARN", msg)

    def todo(self, msg):
        self.add("TODO", msg)

    def fail(self, msg):
        self.add("FAIL", msg)

    def count(self, level):
        return sum(1 for lv, _ in self.results if lv == level)

    def finish(self, root, ready_msg):
        print(f"{self.title} for: {root}\n")
        for level, msg in self.results:
            print(f"[{level}] {msg}")
        c = {k: self.count(k) for k in ("PASS", "WARN", "TODO", "FAIL")}
        print(f"\nSummary: {c['PASS']} passed, {c['WARN']} warnings, "
              f"{c['TODO']} to fill in, {c['FAIL']} failed")
        if c["FAIL"]:
            print("Result: NOT READY. Fix every [FAIL] first.")
            return 1
        if c["TODO"]:
            print("Result: structure is valid, but [TODO] items remain.")
            return 0
        print(f"Result: {ready_msg}")
        return 0


def root_from_argv():
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).resolve()
    return Path(__file__).resolve().parent.parent


def read_csv(root, rel, required_cols, rep):
    """Return a list of (line_no, row) or None if the file is unusable."""
    path = root / rel
    if not path.is_file():
        rep.fail(f"{rel}: file missing")
        return None
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        header = reader.fieldnames or []
        missing = [c for c in required_cols if c not in header]
        if missing:
            rep.fail(f"{rel}: missing columns {missing}")
            return None
        rows, bad = [], 0
        for line_no, row in enumerate(reader, start=2):
            if None in row or any(v is None for v in row.values()):
                rep.fail(f"{rel} line {line_no}: wrong number of columns")
                bad += 1
                continue
            rows.append((line_no, {k: v.strip() for k, v in row.items()}))
    if not bad:
        rep.ok(f"{rel}: {len(rows)} rows, columns OK")
    return rows


def csv_header(root, rel):
    path = root / rel
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        return next(csv.reader(fh), [])


def ids_in(text, kind):
    return re.findall(rf"\b{ID_PATTERNS[kind]}\b", text)


def split_list(value):
    return [v.strip() for v in value.split(";") if v.strip() and v.strip() != "-"]


def is_date(value):
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def load_assets(root):
    with (root / "00-scope-and-setup/asset-register.csv").open(newline="", encoding="utf-8") as fh:
        return {r["asset_id"].strip(): r for r in csv.DictReader(fh)}


def load_data(root):
    with (root / "00-scope-and-setup/data-inventory.csv").open(newline="", encoding="utf-8") as fh:
        return {r["data_id"].strip(): r for r in csv.DictReader(fh)}


def load_traceability(root):
    path = root / "traceability.csv"
    rows = []
    if not path.is_file():
        return rows
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        next(reader, None)
        for line_no, row in enumerate(reader, start=2):
            if any(c.strip() for c in row):
                rows.append((line_no, [c.strip() for c in row]))
    return rows


def run_previous(root, script, rep, label):
    """Run an earlier phase validator; PASS if it exits 0."""
    proc = subprocess.run(
        [sys.executable, str(root / "tools" / script), str(root)],
        capture_output=True, text=True, encoding="utf-8",
    )
    summary = next((ln for ln in proc.stdout.splitlines() if ln.startswith("Summary:")), "no summary")
    if proc.returncode == 0:
        rep.ok(f"{label} still valid ({summary.removeprefix('Summary: ')})")
    else:
        rep.fail(f"{label} fails; run tools/{script} ({summary.removeprefix('Summary: ')})")
    return proc.returncode == 0


_CVSS_W = {
    "AV": {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2},
    "AC": {"L": 0.77, "H": 0.44},
    "UI": {"N": 0.85, "R": 0.62},
    "CIA": {"H": 0.56, "L": 0.22, "N": 0.0},
}


def _roundup(x):
    i = round(x * 100000)
    return i / 100000.0 if i % 10000 == 0 else (i // 10000 + 1) / 10.0


def cvss31(vector):
    """Return the CVSS 3.1 base score for a vector, or None if the vector is invalid."""
    m = re.fullmatch(r"CVSS:3\.[01]/AV:([NALP])/AC:([LH])/PR:([NLH])/UI:([NR])/S:([UC])/"
                     r"C:([HLN])/I:([HLN])/A:([HLN])", vector or "")
    if not m:
        return None
    av, ac, pr, ui, s, c, i, a = m.groups()
    changed = s == "C"
    prw = {"N": 0.85, "L": 0.68 if changed else 0.62, "H": 0.5 if changed else 0.27}[pr]
    iss = 1 - (1 - _CVSS_W["CIA"][c]) * (1 - _CVSS_W["CIA"][i]) * (1 - _CVSS_W["CIA"][a])
    impact = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02) ** 15 if changed else 6.42 * iss
    expl = 8.22 * _CVSS_W["AV"][av] * _CVSS_W["AC"][ac] * prw * _CVSS_W["UI"][ui]
    if impact <= 0:
        return 0.0
    return _roundup(min((1.08 if changed else 1) * (impact + expl), 10))


def cvss_severity(score):
    if score == 0:
        return "None"
    return "Low" if score < 4 else "Medium" if score < 7 else "High" if score < 9 else "Critical"


def check_iso_ref(ref):
    m = re.fullmatch(r"A\.([5-8])\.(\d{1,2})", ref)
    if m:
        theme, num = int(m.group(1)), int(m.group(2))
        return 1 <= num <= ISO_ANNEX_A[theme]
    return re.fullmatch(r"Clause (4|5|6|7|8|9|10)(\.\d+){0,2}", ref) is not None
