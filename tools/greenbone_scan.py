#!/usr/bin/env python3
"""Wait for the Greenbone feed, then scan ONLY the lab shop on tm-lab (Phase 3).

Run from the project root (PowerShell):
    py tools\\greenbone_scan.py --cutoff 20:30
The target is the IP address of the 'juice-shop' alias on the internal network
tm-lab (port 3000 only). If the feed is not ready by the cutoff (local time), the
script stops and records that in the run log. Output: evidence/phase3/after/
greenbone-report.xml, greenbone-results.txt, run-log.txt. Needs Docker.
"""
import argparse
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GB_DIR = Path.home() / "greenbone-community-container"
OUT = ROOT / "evidence" / "phase3" / "after"
FULL_AND_FAST = "daba56c8-73ec-11df-a475-002264764cea"
OPENVAS_SCANNER = "08b69003-5fc2-4037-a479-93b440211c73"
XML_FORMAT = "a994b278-1f62-11e1-96ac-406186ea4fc5"


def log(msg):
    line = f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}  greenbone: {msg}"
    print(line, flush=True)
    with (OUT / "run-log.txt").open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def password():
    text = (GB_DIR / "admin-password.txt").read_text(encoding="utf-8")
    return re.search(r"^password: (\S+)", text, re.M).group(1)


def gmp(xml):
    proc = subprocess.run(
        ["docker", "compose", "-f", str(GB_DIR / "docker-compose.yml"), "run", "--rm", "-T", "gvm-tools",
         "gvm-cli", "--gmp-username", "admin", "--gmp-password", password(), "socket", "--xml", xml],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=GB_DIR)
    return proc.stdout + proc.stderr


def target_ip():
    out = subprocess.run(["docker", "inspect", "-f", "{{(index .NetworkSettings.Networks \"tm-lab\").IPAddress}}",
                          "shop-proxy"], capture_output=True, text=True).stdout.strip()
    if not re.fullmatch(r"172\.\d+\.\d+\.\d+", out):
        raise SystemExit(f"Could not resolve the lab shop on tm-lab: {out!r}")
    return out


def feed_ready():
    feeds = gmp("<get_feeds/>")
    syncing = "<currently_syncing>" in feeds
    configs = gmp("<get_configs/>")
    return (not syncing) and "Full and fast" in configs, syncing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cutoff", default="20:30", help="local time HH:MM after which to give up")
    args = ap.parse_args()
    hh, mm = map(int, args.cutoff.split(":"))
    log(f"waiting for the feed (cutoff {args.cutoff} local time)")
    while True:
        ready, syncing = feed_ready()
        if ready:
            break
        now = datetime.now()
        if (now.hour, now.minute) >= (hh, mm):
            log(f"feed not ready at the cutoff ({'still syncing' if syncing else 'scan configs missing'}); "
                "no Greenbone scan run")
            return 3
        time.sleep(180)
    ip = target_ip()
    log(f"feed ready; target = lab shop on tm-lab {ip}, port T:3000 only")
    run_tag = datetime.now(timezone.utc).strftime("%H%M%S")
    r = gmp(f"<create_target><name>Phase 3 lab shop {ip} run {run_tag}</name><hosts>{ip}</hosts>"
            f"<port_range>T:3000</port_range><alive_tests>Consider Alive</alive_tests></create_target>")
    tid = re.search(r'create_target_response[^>]*id="([^"]+)"', r)
    if not tid:
        log(f"create_target failed: {r[:200]}")
        return 1
    r = gmp(f"<create_task><name>Phase 3 lab scan run {run_tag}</name><target id=\"{tid.group(1)}\"/>"
            f"<config id=\"{FULL_AND_FAST}\"/><scanner id=\"{OPENVAS_SCANNER}\"/></create_task>")
    task = re.search(r'create_task_response[^>]*id="([^"]+)"', r)
    if not task:
        log(f"create_task failed: {r[:200]}")
        return 1
    r = gmp(f"<start_task task_id=\"{task.group(1)}\"/>")
    rep = re.search(r"<report_id>([^<]+)</report_id>", r)
    if not rep:
        log(f"start_task failed: {r[:200]}")
        return 1
    log(f"scan started: task {task.group(1)}, report {rep.group(1)}")
    while True:
        st = gmp(f"<get_tasks task_id=\"{task.group(1)}\"/>")
        status = re.search(r"<status>([^<]+)</status>", st)
        prog = re.search(r"<progress>(-?\d+)", st)
        if status and status.group(1) in ("Done", "Stopped", "Interrupted"):
            break
        now = datetime.now()
        if (now.hour, now.minute) >= (hh, mm):
            gmp(f"<stop_task task_id=\"{task.group(1)}\"/>")
            log(f"cutoff {args.cutoff} reached during the scan (progress {prog.group(1) if prog else '?'}%); scan stopped")
            return 3
        time.sleep(60)
    log(f"scan finished with status {status.group(1)}")
    xml = gmp(f"<get_reports report_id=\"{rep.group(1)}\" format_id=\"{XML_FORMAT}\" details=\"1\" "
              f"filter=\"apply_overrides=0 min_qod=70 levels=hmlg rows=500\"/>")
    (OUT / "greenbone-report.xml").write_text(xml, encoding="utf-8")
    results = re.findall(r"<result id=.*?</result>", xml, re.S)
    lines = []
    for res in results:
        name = re.search(r"<name>([^<]*)</name>", res)
        sev = re.search(r"<severity>([^<]*)</severity>", res)
        port = re.search(r"<port>([^<]*)</port>", res)
        lines.append(f"{sev.group(1) if sev else '?':>5}  {port.group(1) if port else '?':<12} {name.group(1) if name else '?'}")
    (OUT / "greenbone-results.txt").write_text("\n".join(sorted(lines, reverse=True)) + "\n", encoding="utf-8")
    log(f"report saved: {len(results)} results (greenbone-report.xml, greenbone-results.txt)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
