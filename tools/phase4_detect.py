#!/usr/bin/env python3
"""Phase 4 detection: collect the lab shop's logs and apply detection rules.

Detection sources (no SIEM): the nginx access log of the shop proxy (edge log)
and the Juice Shop application log. Run from the project root:
    py tools\\phase4_detect.py
Output: evidence/phase4/logs/ (raw logs) and evidence/phase4/detection/
(alerts.json, detection-report.md). Standard library only; needs Docker.

Rules (the alerting logic of CA-24):
  rule 1  admin user-data endpoint accessed (/api/Users, /rest/user/authentication-details)
  rule 2  enumeration burst: >= 20 API requests from one client within 60 seconds
  rule 3  login followed by admin user-data access within 5 minutes (possible account takeover)
  rule 4  SQL injection indicators (quote or SQL keywords in the URL, or HTTP 500 on login)
"""
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "evidence" / "phase4" / "logs"
OUTD = ROOT / "evidence" / "phase4" / "detection"
LINE = re.compile(r'(?P<ip>\S+) \S+ \S+ \[(?P<ts>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+)[^"]*" '
                  r'(?P<status>\d{3}) \S+ "[^"]*" "(?P<ua>[^"]*)"')
ADMIN_DATA = re.compile(r"^/(api/Users|rest/user/authentication-details)")
SQLI = re.compile(r"(%27|'|%22|\bunion\b|\bselect\b|--|%2d%2d)", re.I)


def now():
    return datetime.now(timezone.utc)


def collect():
    LOGS.mkdir(parents=True, exist_ok=True)
    proxy = subprocess.run(["docker", "logs", "shop-proxy"], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
    (LOGS / "proxy-access.log").write_text(proxy.stdout, encoding="utf-8")
    (LOGS / "proxy-error.log").write_text(proxy.stderr, encoding="utf-8")
    (LOGS / "app").mkdir(exist_ok=True)
    subprocess.run(["docker", "cp", "app-patched:/juice-shop/logs/.", str(LOGS / "app")],
                   capture_output=True, text=True)
    return proxy.stdout


def parse(text):
    events = []
    for raw in text.splitlines():
        m = LINE.search(raw)
        if not m:
            continue
        ts = datetime.strptime(m["ts"], "%d/%b/%Y:%H:%M:%S %z").astimezone(timezone.utc)
        events.append({"time": ts, **{k: m[k] for k in ("ip", "method", "path", "status", "ua")}})
    return sorted(events, key=lambda e: e["time"])


def iso(ts):
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def detect(events):
    alerts = []
    admin = [e for e in events if ADMIN_DATA.match(e["path"]) and e["status"] == "200"]
    by_ip = defaultdict(list)
    for e in admin:
        by_ip[e["ip"]].append(e)
    for ip, evs in by_ip.items():
        alerts.append({"rule": 1, "severity": "High" if len(evs) > 10 else "Medium",
                       "title": "Admin user-data endpoints accessed", "client": ip,
                       "first_event": iso(evs[0]["time"]), "last_event": iso(evs[-1]["time"]),
                       "count": len(evs), "examples": sorted({e["path"] for e in evs})[:5]})
    api = defaultdict(list)
    for e in events:
        if e["path"].startswith(("/api/", "/rest/")):
            api[e["ip"]].append(e)
    for ip, evs in api.items():
        for i in range(len(evs)):
            window = [x for x in evs[i:] if x["time"] - evs[i]["time"] <= timedelta(seconds=60)]
            if len(window) >= 20:
                alerts.append({"rule": 2, "severity": "High", "title": "Enumeration burst (>= 20 API requests in 60 s)",
                               "client": ip, "first_event": iso(window[0]["time"]),
                               "last_event": iso(window[-1]["time"]), "count": len(window)})
                break
    logins = [e for e in events if e["path"].startswith("/rest/user/login") and e["method"] == "POST"
              and e["status"] == "200"]
    for lg in logins:
        follow = [e for e in admin if e["ip"] == lg["ip"] and timedelta(0) <= e["time"] - lg["time"] <= timedelta(minutes=5)]
        if follow:
            alerts.append({"rule": 3, "severity": "High",
                           "title": "Login followed by admin user-data access within 5 minutes (possible account takeover)",
                           "client": lg["ip"], "first_event": iso(lg["time"]), "last_event": iso(follow[-1]["time"]),
                           "count": len(follow), "user_agent": lg["ua"]})
            break
    sqli = [e for e in events if SQLI.search(e["path"]) or (e["path"].startswith("/rest/user/login") and e["status"] == "500")]
    if sqli:
        alerts.append({"rule": 4, "severity": "High", "title": "SQL injection indicators",
                       "client": sqli[0]["ip"], "first_event": iso(sqli[0]["time"]),
                       "last_event": iso(sqli[-1]["time"]), "count": len(sqli)})
    return sorted(alerts, key=lambda a: a["first_event"])


def main():
    run_at = now()
    events = parse(collect())
    alerts = detect(events)
    OUTD.mkdir(parents=True, exist_ok=True)
    result = {"detection_run_utc": iso(run_at), "events_parsed": len(events), "alerts": alerts}
    (OUTD / "alerts.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    lines = [f"# Detection report", "", f"Detection run: {iso(run_at)}. Source: nginx access log of "
             f"`shop-proxy` ({len(events)} requests parsed) and the Juice Shop application log "
             "(`evidence/phase4/logs/`).", "",
             "| Rule | Severity | Alert | Client | First event (UTC) | Last event (UTC) | Count |",
             "|---|---|---|---|---|---|---|"]
    for a in alerts:
        lines.append(f"| {a['rule']} | {a['severity']} | {a['title']} | {a['client']} | {a['first_event']} "
                     f"| {a['last_event']} | {a['count']} |")
    if not alerts:
        lines.append("| - | - | no alerts | - | - | - | - |")
    (OUTD / "detection-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
