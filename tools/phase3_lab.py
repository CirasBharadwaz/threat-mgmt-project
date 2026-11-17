#!/usr/bin/env python3
"""Phase 3 lab runner: the same scans and attack before and after the fix.

Run from the project root (PowerShell):
    py tools\\phase3_lab.py <stage> <step> [<step> ...]
    stage: before | after | options
    steps: isolation nmap trivy zap-baseline zap-active sqli
Example:
    py tools\\phase3_lab.py before isolation nmap trivy zap-baseline zap-active sqli

Scope rule: every scan targets ONLY the local Juice Shop lab, either as
http://juice-shop:3000 on the internal Docker network 'tm-lab', or as
http://127.0.0.1:3000 from this machine. Nothing else is scanned.
Outputs go to evidence/phase3/<stage>/ with a run log (UTC timestamps).
Standard library only; needs Docker.
"""
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAB_NET = "tm-lab"
TARGET_HOST = "juice-shop"                 # alias on tm-lab (app before, proxy after)
TARGET_URL = f"http://{TARGET_HOST}:3000"
LOCAL_URL = "http://127.0.0.1:3000"
JUICE_IMAGE = "bkimminich/juice-shop:latest"
PATCHED_IMAGE = "shopnova/juice-shop-patched:ca-06"
ZAP_IMAGE = "zaproxy/zap-stable"
NMAP_IMAGE = "instrumentisto/nmap:latest"
TRIVY_IMAGE = "aquasec/trivy:latest"
SQLI_EMAIL = "' OR 1=1--"
ALLOWED_TARGETS = {TARGET_HOST, TARGET_URL, LOCAL_URL, JUICE_IMAGE, PATCHED_IMAGE}


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Run:
    def __init__(self, stage):
        self.out = ROOT / "evidence" / "phase3" / stage
        self.out.mkdir(parents=True, exist_ok=True)
        self.log = self.out / "run-log.txt"

    def note(self, msg):
        # sanitise local paths: logs show <project-root> instead of the user's folder
        msg = msg.replace(str(ROOT), "<project-root>").replace(str(ROOT.parent), "<project-root>\\..")
        line = f"{now()}  {msg}"
        print(line)
        with self.log.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def docker(self, args, save_as=None, check=False):
        self.note("docker " + " ".join(args))
        proc = subprocess.run(["docker", *args], capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        if save_as:
            (self.out / save_as).write_text(proc.stdout + proc.stderr, encoding="utf-8")
        self.note(f"  exit code {proc.returncode}" + (f", output saved to {save_as}" if save_as else ""))
        if check and proc.returncode != 0:
            raise SystemExit(proc.stderr)
        return proc


def guard(target):
    if target not in ALLOWED_TARGETS:
        raise SystemExit(f"Refusing to scan '{target}': only the local Juice Shop lab is in scope.")


def step_isolation(run):
    """Show that a container on tm-lab reaches Juice Shop and nothing else."""
    script = (
        "import socket\n"
        "def probe(host, port):\n"
        "    try:\n"
        "        socket.create_connection((host, port), timeout=4).close(); return 'REACHABLE'\n"
        "    except Exception as e:\n"
        "        return 'blocked (' + type(e).__name__ + ')'\n"
        f"print('juice-shop:3000      ', probe('{TARGET_HOST}', 3000))\n"
        "print('1.1.1.1:443 (internet)', probe('1.1.1.1', 443))\n"
        "print('host.docker.internal:3000 (host)', probe('host.docker.internal', 3000))\n"
    )
    run.docker(["run", "--rm", "--network", LAB_NET, "--entrypoint", "python3", ZAP_IMAGE,
                "-c", script], save_as="network-isolation.txt")


def step_nmap(run):
    guard(TARGET_HOST)
    run.docker(["run", "--rm", "--network", LAB_NET, "-v", f"{run.out}:/out", NMAP_IMAGE,
                "-sV", "-sC", "-p-", "-T4", "-oA", "/out/nmap", TARGET_HOST], save_as="nmap-console.txt")


def step_trivy(run):
    image = PATCHED_IMAGE if run.out.name == "after" else JUICE_IMAGE
    guard(image)
    cache = ROOT.parent / ".trivy-cache"   # outside the repository
    cache.mkdir(exist_ok=True)
    base = ["run", "--rm", "-v", "//var/run/docker.sock:/var/run/docker.sock",
            "-v", f"{cache}:/root/.cache", "-v", f"{run.out}:/out", TRIVY_IMAGE]
    run.docker(base + ["--version"], save_as="trivy-version.txt")
    run.docker(base + ["image", "--scanners", "vuln", "--timeout", "20m", "--no-progress",
                       "--format", "json", "-o", "/out/trivy.json", image],
               save_as="trivy-console.txt")
    run.docker(base + ["convert", "--format", "table", "-o", "/out/trivy-table.txt", "/out/trivy.json"])


def step_zap_baseline(run):
    guard(TARGET_URL)
    run.docker(["run", "--rm", "--network", LAB_NET, "-v", f"{run.out}:/zap/wrk:rw", ZAP_IMAGE,
                "zap-baseline.py", "-t", TARGET_URL, "-J", "zap-baseline.json",
                "-r", "zap-baseline.html", "-w", "zap-baseline.md", "-I", "-z", "-silent"],
               save_as="zap-baseline-console.txt")


def step_zap_active(run):
    guard(TARGET_URL)
    lab = ROOT / "03-vulnerability" / "lab"
    run.docker(["run", "--rm", "--network", LAB_NET, "-v", f"{run.out}:/zap/wrk:rw",
                "-v", f"{lab}:/lab:ro", "--entrypoint", "python3", ZAP_IMAGE,
                "/lab/zap_login_ascan.py", TARGET_URL], save_as="zap-active-console.txt")


def http(method, url, body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, dict(resp.headers), resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode("utf-8", "replace")


def step_sqli(run):
    """Live login bypass: the identical request before and after the fix."""
    guard(LOCAL_URL)
    url = f"{LOCAL_URL}/rest/user/login"
    results = {"time_utc": now(), "target": url, "attempts": []}
    for label, body in (("normal login, wrong password",
                         {"email": "nobody@example.invalid", "password": "wrong"}),
                        ("SQL injection login bypass", {"email": SQLI_EMAIL, "password": "x"})):
        status, headers, text = http("POST", url, body)
        entry = {"attempt": label, "request_body": body, "http_status": status,
                 "response_excerpt": text[:400]}
        token = None
        try:
            auth = json.loads(text).get("authentication", {})
            token = auth.get("token")
            entry["logged_in_as"] = auth.get("umail")
        except (ValueError, AttributeError):
            pass
        if token:
            entry["response_excerpt"] = "token issued (redacted): " + token[:20] + "..."
            w_status, _, w_text = http("GET", f"{LOCAL_URL}/rest/user/whoami", token=token)
            entry["whoami"] = {"http_status": w_status, "body": w_text[:300]}
        entry["verdict"] = "BYPASS SUCCEEDED" if token and label.startswith("SQL") else \
            ("blocked" if label.startswith("SQL") else "rejected as expected" if status == 401 else "check")
        results["attempts"].append(entry)
        run.note(f"  {label}: HTTP {status} -> {entry['verdict']}")
    (run.out / "sqli-login-bypass.json").write_text(json.dumps(results, indent=2), encoding="utf-8")


OPTION_TARGETS = {
    "control: unpatched app, no protection": "http://juice-shop:3000",
    "option A: hardening layer (ModSecurity CRS WAF) in front of the unpatched app": "http://waf-test:8080",
    "option B: patched login route (bound parameters), no WAF": "http://app-patched:3000",
}


def step_fix_options(run):
    """Send the identical SQL injection login to each fix option from inside tm-lab."""
    script = (
        "import json, urllib.request, urllib.error, sys\n"
        "targets = json.loads(sys.argv[1]); out = []\n"
        "for label, base in targets.items():\n"
        "    for name, body in (('SQL injection login bypass', {'email': \"' OR 1=1--\", 'password': 'x'}),\n"
        "                       ('SQL injection variant (comment only)', {'email': \"admin@juice-sh.op'--\", 'password': 'x'}),\n"
        "                       ('legitimate login, wrong password', {'email': 'jim@juice-sh.op', 'password': 'wrong'}),\n"
        "                       ('legitimate login, correct password (lab user)', {'email': 'jim@juice-sh.op', 'password': 'ncc-1701'})):\n"
        "        req = urllib.request.Request(base + '/rest/user/login', data=json.dumps(body).encode(),\n"
        "                                     method='POST', headers={'Content-Type': 'application/json'})\n"
        "        try:\n"
        "            r = urllib.request.urlopen(req, timeout=15); code, text = r.status, r.read().decode()\n"
        "        except urllib.error.HTTPError as e:\n"
        "            code, text = e.code, e.read().decode('utf-8', 'replace')\n"
        "        except Exception as e:\n"
        "            code, text = None, repr(e)\n"
        "        token = 'authentication' in text and 'token' in text\n"
        "        out.append({'option': label, 'url': base + '/rest/user/login', 'request': name,\n"
        "                    'http_status': code, 'token_issued': token, 'excerpt': text[:160]})\n"
        "print(json.dumps(out, indent=2))\n"
    )
    proc = run.docker(["run", "--rm", "--network", LAB_NET, "--entrypoint", "python3", ZAP_IMAGE,
                       "-c", script, json.dumps(OPTION_TARGETS)])
    # keep only the JWT header in the stored excerpts; the payload and signature are redacted
    redacted = re.sub(r"(eyJ[A-Za-z0-9_-]+)[.][A-Za-z0-9_.-]*", lambda m: m.group(1) + ".[redacted]", proc.stdout)
    (run.out / "fix-options-sqli.json").write_text(redacted, encoding="utf-8")
    for r in json.loads(proc.stdout or "[]"):
        run.note(f"  {r['option']} | {r['request']}: HTTP {r['http_status']}, token issued: {r['token_issued']}")


STEPS = {"isolation": step_isolation, "nmap": step_nmap, "trivy": step_trivy,
         "zap-baseline": step_zap_baseline, "zap-active": step_zap_active, "sqli": step_sqli,
         "fix-options": step_fix_options}


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("before", "after", "options") or \
            any(s not in STEPS for s in sys.argv[2:]):
        print(__doc__)
        return 2
    run = Run(sys.argv[1])
    for step in sys.argv[2:]:
        run.note(f"== step {step} ({sys.argv[1]})")
        STEPS[step](run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
