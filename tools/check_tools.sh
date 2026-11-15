#!/usr/bin/env bash
# Phase 0: check your machine for the tools this project needs.
# Run from the project root:  bash tools/check_tools.sh

echo "=== OS ==="
uname -a

echo
echo "=== Tools ==="
# A tool only counts as OK if '--version' actually runs. This catches stubs such as
# the Windows Store 'python3' alias, which exists on PATH but is not Python.
for t in git docker python3 python pip3 nmap pandoc code; do
  if command -v "$t" >/dev/null 2>&1; then
    if ver=$("$t" --version 2>&1); then
      printf "%-10s OK       %s\n" "$t" "$(printf '%s\n' "$ver" | head -n 1)"
    else
      printf "%-10s BROKEN   %s\n" "$t" "found on PATH but '--version' failed (on Windows, likely a Store alias)"
    fi
  else
    printf "%-10s MISSING\n" "$t"
  fi
done

echo
echo "=== Docker daemon ==="
if command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then
    echo "Docker daemon: running"
  else
    echo "Docker daemon: NOT running (start Docker Desktop or the docker service)"
  fi
else
  echo "Docker is not installed (needed from Phase 3)"
fi

echo
echo "=== Memory ==="
RAM_GB=""
if [ -r /proc/meminfo ]; then
  RAM_GB=$(awk '/MemTotal/ {printf "%d", $2/1024/1024}' /proc/meminfo)
elif command -v sysctl >/dev/null 2>&1; then
  RAM_GB=$(( $(sysctl -n hw.memsize 2>/dev/null || echo 0) / 1024 / 1024 / 1024 ))
fi
if [ -n "$RAM_GB" ] && [ "$RAM_GB" -gt 0 ]; then
  echo "RAM: ${RAM_GB} GB"
  if [ "$RAM_GB" -ge 15 ]; then
    echo "Lab plan: comfortable (target app + scanner + SIEM can run together)"
  elif [ "$RAM_GB" -ge 8 ]; then
    echo "Lab plan: tight (run the target, scanner and SIEM one at a time)"
  else
    echo "Lab plan: very limited (use lightweight scanners; we will adapt Phase 3 and 4)"
  fi
else
  echo "RAM: could not detect (tell me your RAM in GB)"
fi

echo
echo "=== Disk (current folder) ==="
df -h . 2>/dev/null | head -n 2
FREE_GB=$(df -Pk . 2>/dev/null | awk 'NR==2 {printf "%d", $4/1024/1024}')
if [ -n "$FREE_GB" ]; then
  if [ "$FREE_GB" -ge 40 ]; then
    echo "Free space: ${FREE_GB} GB (enough for the lab images)"
  else
    echo "Free space: ${FREE_GB} GB (aim for 40 GB or more before Phase 3)"
  fi
fi

echo
echo "Paste this whole output into the chat so we can plan Phase 3 and 4 realistically."
