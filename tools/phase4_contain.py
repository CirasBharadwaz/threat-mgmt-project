#!/usr/bin/env python3
"""Phase 4 containment for INC-01 (lab only), as done on 2026-11-17.

Run from the project root (PowerShell), after py tools\\phase4_attack.py attack:
    py tools\\phase4_contain.py
Steps:
  1. CA-23: reset the support account password through the shop API. The new random
     password is written OUTSIDE the repository, to %USERPROFILE%\\threat-lab-secrets\\.
  2. CA-22/CA-25: recreate the proxy with the final configuration
     (03-vulnerability/lab/fix/nginx-hardening.conf), which blocks reading user data
     but still allows customer sign-up.
  3. Append both steps to evidence/phase4/response/containment-log.txt.
Then verify with: py tools\\phase4_attack.py verify-containment
Standard library only; needs Docker. Targets only http://127.0.0.1:3000.
"""
import json
import secrets
import string
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "http://127.0.0.1:3000"
SUPPORT = "support@juice-sh.op"
PUBLISHED_PASSWORD = "J6aVjTgOpRs@?5l!Zkq2AYnCE@RF$P"   # OWASP Juice Shop demo credential (public)
SECRET_FILE = Path.home() / "threat-lab-secrets" / "support-account-reset.txt"
LOG = ROOT / "evidence" / "phase4" / "response" / "containment-log.txt"
FINAL_CONF = ROOT / "03-vulnerability" / "lab" / "fix" / "nginx-hardening.conf"


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"{now()}  {msg}\n")
    print(f"{now()}  {msg}")


def call(method, path, body=None, token=None):
    req = urllib.request.Request(BASE + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json",
                                          **({"Authorization": f"Bearer {token}"} if token else {})})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def docker(*args):
    return subprocess.run(["docker", *args], capture_output=True, text=True)


def main():
    s, t = call("POST", "/rest/user/login", {"email": SUPPORT, "password": PUBLISHED_PASSWORD})
    if s != 200:
        print(f"Support login with the published password returned {s}; the password may already be reset.")
    else:
        token = json.loads(t)["authentication"]["token"]
        new = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(24)) + "!9a"
        q = urllib.parse.urlencode({"current": PUBLISHED_PASSWORD, "new": new, "repeat": new})
        s2, _ = call("GET", "/rest/user/change-password?" + q, token=token)
        SECRET_FILE.parent.mkdir(parents=True, exist_ok=True)
        with SECRET_FILE.open("a", encoding="utf-8") as fh:
            fh.write(f"reset {now()}: {new}\n")
        log(f"containment 1 (CA-23): {SUPPORT} password reset via the shop API -> HTTP {s2}; "
            "new password stored outside the repository")
    docker("rm", "-f", "shop-proxy")
    r = docker("run", "-d", "--name", "shop-proxy", "--network", "tm-pub", "-p", "127.0.0.1:3000:3000",
               "-v", f"{FINAL_CONF}:/etc/nginx/conf.d/default.conf:ro", "nginx:1.27")
    if r.returncode != 0:
        raise SystemExit(r.stderr)
    docker("network", "connect", "--alias", "juice-shop", "tm-lab", "shop-proxy")
    time.sleep(3)
    log("containment 2 (CA-22/CA-25): proxy recreated with nginx-hardening.conf; reading user data blocked, sign-up allowed")
    print("Next: py tools\\phase4_attack.py verify-containment")
    return 0


if __name__ == "__main__":
    sys.exit(main())
