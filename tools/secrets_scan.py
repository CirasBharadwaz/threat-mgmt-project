#!/usr/bin/env python3
"""Secrets and personal-data scan of the repository (run before every commit).

Run from the project root:
    py tools\\secrets_scan.py
Scans every file in the working tree (not .git), the text inside the DOCX, and the
git history (commit metadata and committed file contents). Known secret values that
were set during the project are read from files OUTSIDE the repository and compared
without printing them. E-mail addresses inside raw Trivy output (evidence/.../trivy.json) are
public package-maintainer addresses and are reported as INFO. Every hit is shown with file,
line and a masked excerpt.
Exit code 1 if a HIGH finding exists. Standard library only.
"""
import ipaddress
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTSIDE = {  # files outside the repo that hold secrets set during the project
    "Greenbone admin password": (Path.home() / "greenbone-community-container" / "admin-password.txt", r"^password: (\S+)"),
    # lines like "... password: X", "re-applied <ISO time>: X", "reset <ISO time>: X" (the time has colons)
    "support account reset password": (Path.home() / "threat-lab-secrets" / "support-account-reset.txt",
                                       r"^(?:.*\bpassword|(?:re-)?applied \S+|reset \S+): (\S+)\s*$"),
}
# Raw Trivy output lists public package-maintainer and mailing-list addresses from vulnerability databases
TRIVY_OUTPUT = re.compile(r"^evidence/.+/trivy\.json$")
PUBLIC_LAB_CREDENTIALS = {  # published Juice Shop demo credentials (synthetic)
    "J6aVjTgOpRs@?5l!Zkq2AYnCE@RF$P": "Juice Shop support@juice-sh.op demo password",
    "ncc-1701": "Juice Shop jim@juice-sh.op demo password",
}
SYNTHETIC_MAIL = re.compile(r"@(juice-sh\.op|[\w.-]*\.invalid|[\w.-]*\.example|example\.(com|org)|owasp\.org)$", re.I)
PATTERNS = [
    # a quoted literal assigned to a password-like name, also with a prefix or suffix (ADMIN_PASSWORD = "...")
    ("HIGH", "hard-coded password (string literal)", re.compile(
        r"""(?i)\b\w*(?:password|passwd|pwd|secret|api[_-]?key)\w*["']?\s*[:=]\s*(["'])(?![<${%])([^"'\s]{6,})\1""")),
    ("HIGH", "JWT (complete token)", re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}")),
    ("LOW", "JWT fragment (header only)", re.compile(r"eyJ[A-Za-z0-9_-]{8,}(?!\.[A-Za-z0-9_-]{8,}\.)")),
    ("HIGH", "Bearer token", re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}")),
    ("MEDIUM", "cookie header", re.compile(r"\b(Set-Cookie|Cookie):\s*\S+", re.I)),
    ("HIGH", "private key", re.compile(r"BEGIN [A-Z ]*PRIVATE KEY")),
    ("HIGH", "cloud access key", re.compile(r"\b(AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("MEDIUM", "password/secret assignment", re.compile(
        r"""(?i)\b(password|passwd|pwd|secret|api[_-]?key|token)\b["']?\s*[:=]\s*["']?(?!\{|\$|<|\[|\*|-\s|None|null|""|'')([^\s"',;)]{6,})""")),
    ("MEDIUM", "lab test password", re.compile(r"Lab-Test-\d{6}!x")),
    ("INFO", "phone number", re.compile(r"(?<![\w.-])(\+\d{2}[\s/-]?\d{2,4}[\s/-]?\d{3,}[\s/-]?\d{0,6}|\b0\d{2,4}[\s/-]\d{5,}\b)")),
]
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
SKIP_EXT = {".png", ".jpg", ".gif", ".pdf", ".pyc", ".zip"}


def mask(s):
    return s[:4] + "…" + f"({len(s)} chars)" if len(s) > 6 else "***"


def outside_secrets():
    found = {}
    for label, (path, rx) in OUTSIDE.items():
        if path.is_file():
            vals = re.findall(rx, path.read_text(encoding="utf-8", errors="replace"), re.M)
            if vals:
                found[label] = set(vals)
    return found


def files():
    for p in ROOT.rglob("*"):
        if ".git" in p.parts or not p.is_file() or "__pycache__" in p.parts:
            continue
        yield p


def text_of(p):
    if p.suffix == ".docx":
        try:
            xml = zipfile.ZipFile(p).read("word/document.xml").decode("utf-8", "replace")
            return re.sub(r"<[^>]+>", " ", xml)
        except (zipfile.BadZipFile, KeyError):
            return ""
    if p.suffix in SKIP_EXT:
        return None
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def scan_text(name, text, secrets, hits, path=""):
    trivy = bool(TRIVY_OUTPUT.search(path))
    for n, line in enumerate(text.splitlines(), 1):
        for label, vals in secrets.items():
            for v in vals:
                if v in line:
                    hits.append(("HIGH", f"{label} (value set in this project)", name, n, mask(v)))
        for v, what in PUBLIC_LAB_CREDENTIALS.items():
            if v in line:
                hits.append(("LOW", f"public lab credential: {what}", name, n, mask(v)))
        for sev, label, rx in PATTERNS:
            for m in rx.finditer(line):
                val = m.group(0)
                if label in ("password/secret assignment", "hard-coded password (string literal)") and \
                        any(v in val for v in PUBLIC_LAB_CREDENTIALS):
                    continue
                hits.append((sev, label, name, n, mask(val) if sev != "INFO" else val.strip()))
        for m in EMAIL.finditer(line):
            mail = m.group(0)
            if SYNTHETIC_MAIL.search(mail):
                hits.append(("INFO", "synthetic e-mail address", name, n, mail))
            elif trivy:
                hits.append(("INFO", "public maintainer e-mail (Trivy output, known)", name, n, mail))
            else:
                hits.append(("HIGH", "real-looking e-mail address", name, n, mail))
        for m in IPV4.finditer(line):
            try:
                ip = ipaddress.ip_address(m.group(0))
            except ValueError:
                continue
            if ip.is_global:
                hits.append(("MEDIUM", "public IP address", name, n, str(ip)))


def main():
    secrets = outside_secrets()
    hits = []
    if (ROOT / ".env").exists() or list(ROOT.rglob("*.env")):
        hits.append(("HIGH", ".env file present", "-", 0, "-"))
    for p in files():
        t = text_of(p)
        if t:
            rel = p.relative_to(ROOT).as_posix()
            scan_text(rel, t, secrets, hits, rel)
    # git history: commit metadata and committed content
    meta = subprocess.run(["git", "log", "--all", "--format=%h author=%an <%ae> committer=%cn <%ce>"],
                          capture_output=True, text=True, cwd=ROOT).stdout
    for ln in meta.splitlines():
        for mail in EMAIL.findall(ln):
            sev = "INFO" if "noreply" in mail else "HIGH"
            hits.append((sev, "e-mail in git commit metadata", f"git commit {ln.split()[0]}", 0, mail))
    hist = subprocess.run(["git", "log", "--all", "-p", "--format=COMMIT %h"], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=ROOT).stdout
    before = len(hits)
    for chunk in re.split(r"^(?=diff --git )", hist, flags=re.M):  # one chunk per file per commit
        m = re.match(r"diff --git a/(\S+)", chunk)
        scan_text("git history (committed content)", chunk, secrets, hits, m.group(1) if m else "")
    hist_hits = hits[before:]
    # report only history findings that are NOT also in the current files (committed copies of
    # current content would otherwise be counted twice); these are values that exist only in history
    current = {(h[1], h[4]) for h in hits[:before]}
    hits = hits[:before] + [h for h in hist_hits if h[0] in ("HIGH", "MEDIUM") and (h[1], h[4]) not in current]
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "INFO": 3}
    agg = {}
    for sev, label, f, n, ex in hits:
        agg.setdefault((sev, label, f, ex), []).append(n)
    for (sev, label, f, ex), lines in sorted(agg.items(), key=lambda k: (order[k[0][0]], k[0][1], k[0][2])):
        ln = ",".join(str(x) for x in sorted(set(lines))[:6]) + ("…" if len(set(lines)) > 6 else "")
        print(f"[{sev}] {label} | {f}:{ln} | {ex}")
    counts = {s: sum(1 for k in agg if k[0] == s) for s in order}
    print(f"\nSummary: {counts['HIGH']} HIGH, {counts['MEDIUM']} MEDIUM, {counts['LOW']} LOW, {counts['INFO']} INFO "
          f"(distinct file/finding pairs). Known project secrets checked: {', '.join(secrets) or 'none found outside the repo'}")
    return 1 if counts["HIGH"] else 0


if __name__ == "__main__":
    sys.exit(main())
