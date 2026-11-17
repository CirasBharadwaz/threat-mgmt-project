#!/usr/bin/env python3
"""Timed dry run of DEMO-RUNBOOK.md, scene by scene, in a SCRATCH COPY of the project.

Run from the project root of a copy (never in the submission folder; it overwrites evidence\\):
    py tools\\demo_dryrun.py --scratch-copy [--quick]
--quick uses the short ZAP active scan (rule 40018 only) instead of the full one.
Writes demo-dryrun-results.md (scene, duration, result) into the copy's root.
Ends with the lab reset to a clean slate. Standard library only; needs Docker.
"""
import json
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
FIX = ROOT / "03-vulnerability" / "lab" / "fix"


def sh(*cmd, check=False):
    r = subprocess.run(list(cmd), capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=ROOT)
    if check and r.returncode != 0:
        raise RuntimeError(f"{' '.join(map(str, cmd))}\n{r.stdout[-400:]}\n{r.stderr[-400:]}")
    return r


def wait_http(url, seconds=120):
    for _ in range(seconds):
        try:
            if urllib.request.urlopen(url, timeout=3).status == 200:
                return True
        except Exception:
            time.sleep(1)
    return False


def last_line(path, needle):
    p = ROOT / path
    lines = [ln for ln in p.read_text(encoding="utf-8").splitlines() if needle in ln] if p.is_file() else []
    return lines[-1].strip()[:110] if lines else "(not found)"


def scene1():
    sh("docker", "network", "create", "--internal", "tm-lab", check=True)
    sh("docker", "network", "create", "tm-pub", check=True)
    sh("docker", "run", "-d", "--name", "juice-shop", "--network", "tm-pub", "-p", "127.0.0.1:3000:3000",
       "bkimminich/juice-shop:latest", check=True)
    sh("docker", "network", "connect", "--alias", "juice-shop", "tm-lab", "juice-shop", check=True)
    if not wait_http("http://127.0.0.1:3000/"):
        raise RuntimeError("Juice Shop did not start")
    sh(PY, "tools/phase3_lab.py", "before", "isolation", check=True)
    return (ROOT / "evidence/phase3/before/network-isolation.txt").read_text(encoding="utf-8").replace("\n", "; ")


def scene2(quick):
    sh(PY, "tools/phase3_lab.py", "before", "nmap", "trivy", "zap-baseline", check=True)
    sh(PY, "tools/phase3_lab.py", "before", "zap-active-quick" if quick else "zap-active", check=True)
    alerts = (ROOT / "evidence/phase3/before/zap-active-alerts.txt").read_text(encoding="utf-8")
    return "SQL Injection found" if "SQL Injection" in alerts else "SQL Injection NOT found"


def scene3():
    r = sh(PY, "tools/phase3_lab.py", "before", "sqli", check=True)
    return next((ln.strip()[22:] for ln in r.stdout.splitlines() if "SQL injection" in ln), r.stdout[-120:])


def scene4():
    sh("docker", "build", "-q", "-t", "shopnova/juice-shop-patched:ca-06", str(FIX), check=True)
    sh("docker", "run", "-d", "--name", "app-patched", "--network", "tm-lab", "shopnova/juice-shop-patched:ca-06", check=True)
    sh("docker", "run", "-d", "--name", "waf-test", "--network", "tm-lab", "-e", "BACKEND=http://juice-shop:3000",
       "-e", "PORT=8080", "owasp/modsecurity-crs:nginx", check=True)
    time.sleep(45)
    sh(PY, "tools/phase3_lab.py", "options", "fix-options", check=True)
    data = json.loads((ROOT / "evidence/phase3/options/fix-options-sqli.json").read_text(encoding="utf-8"))
    inj = [d for d in data if d["request"].startswith("SQL")]
    return ", ".join(f"{d['option'].split(':')[0]}: {d['http_status']}" for d in inj[::2])


def scene5():
    sh("docker", "rm", "-f", "juice-shop", "waf-test", check=True)
    sh("docker", "create", "--name", "shop-proxy", "--network", "tm-pub", "-p", "127.0.0.1:3000:3000",
       "-v", f"{FIX / 'nginx-hardening-phase3.conf'}:/etc/nginx/conf.d/default.conf:ro", "nginx:1.27", check=True)
    sh("docker", "network", "connect", "--alias", "juice-shop", "tm-lab", "shop-proxy", check=True)
    sh("docker", "start", "shop-proxy", check=True)   # only after joining tm-lab
    if not wait_http("http://127.0.0.1:3000/"):
        raise RuntimeError("proxy did not come up")
    r = sh(PY, "tools/phase3_lab.py", "after", "isolation", "sqli", "zap-baseline", check=True)
    return next((ln.strip()[22:] for ln in r.stdout.splitlines() if "SQL injection" in ln), r.stdout[-120:])


def scene6():
    a = sh(PY, "tools/phase4_attack.py", "attack", check=True)
    d = sh(PY, "tools/phase4_detect.py", check=True)
    sh(PY, "tools/phase4_contain.py", check=True)
    v = sh(PY, "tools/phase4_attack.py", "verify-containment")
    alerts = sum(1 for ln in d.stdout.splitlines() if ln.startswith("| ") and "High" in ln)
    acc = json.loads((ROOT / "evidence/phase4/attack/exfiltration-summary.json").read_text(encoding="utf-8"))
    return f"{acc['requests']} requests, {acc['accounts_exposed']} accounts; {alerts} High alerts; {v.stdout.strip().splitlines()[-1]}"


def scene7():
    c = sh(PY, "tools/breach_clock.py", "--inc", "INC-01")
    return "breach clock exit 0 (milestones met)" if c.returncode == 0 else "breach clock reports a miss"


def main():
    if "--scratch-copy" not in sys.argv:
        print(__doc__)
        print("Refusing to run without --scratch-copy: the dry run overwrites evidence\\ in this folder.")
        return 2
    quick = "--quick" in sys.argv
    sh(PY, "tools/demo_reset.py")
    scenes = [("1 Start the lab, before the fix", scene1), ("2 Find the vulnerabilities", lambda: scene2(quick)),
              ("3 Live attack, before the fix", scene3), ("4 Compare the fix options", scene4),
              ("5 Deploy the fix, same attack again", scene5), ("6 Incident INC-01", scene6),
              ("7 Breach clock", scene7)]
    rows, total0 = [], time.time()
    for name, fn in scenes:
        t0 = time.time()
        try:
            res, ok = fn(), "OK"
        except Exception as e:     # keep going so the report shows every scene
            res, ok = str(e).splitlines()[0][:110], "FAILED"
        dur = time.time() - t0
        rows.append((name, f"{dur / 60:.1f} min", ok, res))
        print(f"{name}: {ok} in {dur / 60:.1f} min - {res}", flush=True)
    sh(PY, "tools/demo_reset.py")
    lines = [f"# Demo dry run ({datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')})", "",
             f"Mode: {'quick ZAP active scan (rule 40018 only)' if quick else 'full ZAP active scan'}. "
             f"Total {(time.time() - total0) / 60:.1f} min. Lab reset to a clean slate afterwards.", "",
             "| Scene | Duration | Result | Key output |", "|---|---|---|---|"]
    lines += [f"| {a} | {b} | {c} | {d.replace('|', '/')} |" for a, b, c, d in rows]
    (ROOT / "demo-dryrun-results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0 if all(r[2] == "OK" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
