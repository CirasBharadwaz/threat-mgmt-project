#!/usr/bin/env python3
"""Preflight check before recording the demo (DEMO-RUNBOOK.md).

Run from the project root:
    py tools\\demo_preflight.py
Checks Docker, memory, disk, the container images, port 127.0.0.1:3000, leftover lab
containers and networks, and Greenbone (should be stopped while recording).
Prints OK / WARN / FAIL per item; exit code 1 if anything FAILs. Standard library only.
"""
import shutil
import socket
import subprocess
import sys

IMAGES = ["bkimminich/juice-shop:latest", "zaproxy/zap-stable:latest", "instrumentisto/nmap:latest",
          "aquasec/trivy:latest", "owasp/modsecurity-crs:nginx", "nginx:1.27"]
LAB_CONTAINERS = ["juice-shop", "app-patched", "waf-test", "shop-proxy"]
LAB_NETWORKS = ["tm-lab", "tm-pub"]
results = []


def add(level, msg):
    results.append((level, msg))
    print(f"[{level}] {msg}")


def docker(*args):
    try:
        return subprocess.run(["docker", *args], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        return subprocess.CompletedProcess(args, 1, "", str(e))


def main():
    print(f"Python {sys.version.split()[0]}")
    r = docker("info", "--format", "{{.ServerVersion}} {{.MemTotal}}")
    if r.returncode != 0:
        add("FAIL", "Docker engine not reachable: start Docker Desktop")
        return 1
    ver, mem = r.stdout.split()
    gb = int(mem) / 1024 ** 3
    add("OK", f"Docker {ver} running")
    add("OK" if gb >= 6 else "WARN", f"Docker memory {gb:.1f} GB (lab needs about 3 GB without Greenbone)")
    free = shutil.disk_usage(".").free / 1024 ** 3
    add("OK" if free >= 10 else "WARN", f"free disk {free:.0f} GB")
    have = set(docker("images", "--format", "{{.Repository}}:{{.Tag}}").stdout.split())
    missing = [i for i in IMAGES if i not in have]
    add("OK" if not missing else "WARN",
        "all lab images present" if not missing else f"images will be downloaded on first use: {missing}")
    running = docker("ps", "-a", "--format", "{{.Names}}").stdout.split()
    left = [c for c in LAB_CONTAINERS if c in running]
    nets = [n for n in LAB_NETWORKS if n in docker("network", "ls", "--format", "{{.Name}}").stdout.split()]
    add("OK" if not left and not nets else "WARN",
        "no leftover lab containers or networks (ready for Scene 1)" if not left and not nets else
        f"leftovers from an earlier run: containers {left}, networks {nets}; run py tools\\demo_reset.py")
    s = socket.socket()
    s.settimeout(1)
    busy = s.connect_ex(("127.0.0.1", 3000)) == 0
    s.close()
    add("OK" if not busy else "WARN", "port 127.0.0.1:3000 free" if not busy else
        "port 127.0.0.1:3000 in use; run py tools\\demo_reset.py before Scene 1")
    gb_up = [n for n in docker("ps", "--format", "{{.Names}}").stdout.split() if n.startswith("greenbone")]
    add("OK" if not gb_up else "WARN", "Greenbone stopped (frees memory)" if not gb_up else
        f"{len(gb_up)} Greenbone containers running; stop them before recording")
    fails = sum(1 for lv, _ in results if lv == "FAIL")
    warns = sum(1 for lv, _ in results if lv == "WARN")
    print(f"\nPreflight: {fails} FAIL, {warns} WARN. " + ("Ready to record." if not fails and not warns else
                                                         "Fix the items above first." if fails else "Check the warnings."))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
