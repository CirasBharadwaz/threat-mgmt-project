#!/usr/bin/env python3
"""Reset the lab to a clean slate before starting the lab (see README.md).

Run from the project root:
    py tools\\demo_reset.py
Removes the lab containers (juice-shop, app-patched, waf-test, shop-proxy) and the lab
networks (tm-lab, tm-pub). Images, the Trivy cache and Greenbone (its containers and data)
are NOT touched. Afterwards port 127.0.0.1:3000 is free and the lab can start.
Note: Juice Shop recreates its database at every start, so the published demo
credentials work again after a reset (this is needed for incident INC-01).
Standard library only; needs Docker.
"""
import socket
import subprocess
import sys

CONTAINERS = ["shop-proxy", "app-patched", "waf-test", "juice-shop"]
NETWORKS = ["tm-lab", "tm-pub"]


def docker(*args):
    return subprocess.run(["docker", *args], capture_output=True, text=True)


def main():
    existing = docker("ps", "-a", "--format", "{{.Names}}").stdout.split()
    for c in CONTAINERS:
        if c in existing:
            r = docker("rm", "-f", c)
            print(f"removed container {c}" if r.returncode == 0 else f"could not remove {c}: {r.stderr.strip()}")
    nets = docker("network", "ls", "--format", "{{.Name}}").stdout.split()
    for n in NETWORKS:
        if n in nets:
            attached = docker("network", "inspect", n, "-f", "{{range .Containers}}{{.Name}} {{end}}").stdout.split()
            for a in attached:   # e.g. a stopped Greenbone scanner that was attached for Phase 3
                docker("network", "disconnect", "-f", n, a)
            r = docker("network", "rm", n)
            print(f"removed network {n}" if r.returncode == 0 else f"could not remove network {n}: {r.stderr.strip()}")
    s = socket.socket()
    s.settimeout(1)
    busy = s.connect_ex(("127.0.0.1", 3000)) == 0
    s.close()
    print("port 127.0.0.1:3000 is free; ready to start the lab" if not busy else "WARNING: port 3000 is still in use")
    return 1 if busy else 0


if __name__ == "__main__":
    sys.exit(main())
