# Demo runbook: screen recordings of the lab

This runbook replays the lab work of Phases 3 and 4 in a fixed order, for screen recordings.
All commands are Windows PowerShell, run from the project root.

## Safety and scope

- **Everything runs locally.** The shop listens only on `127.0.0.1:3000` and on the internal Docker
  network `tm-lab`, which has no internet access and no route to the host.
- **Scan only the lab.** Every scan and attack in this runbook targets only the lab shop, and the tools
  refuse other targets. Never point them at a system you do not own.
- **Record from a separate clone.** The scripts write their output into `evidence\`, so a demo run in
  the submission folder would overwrite the committed evidence:

```powershell
git clone https://github.com/CirasBharadwaz/threat-mgmt-project.git $HOME\threat-mgmt-demo
cd $HOME\threat-mgmt-demo
```

**Prerequisites:** Docker Desktop is running, and `py` (Python 3) is installed. The first run downloads
these container images:

- `bkimminich/juice-shop`
- `zaproxy/zap-stable`
- `instrumentisto/nmap`
- `aquasec/trivy`
- `owasp/modsecurity-crs:nginx`
- `nginx:1.27`

**Durations measured on 2026-11-17:**

| Step | Duration |
|---|---|
| Nmap | about 1.5 min |
| Trivy, first run (vulnerability database download) | about 4 min |
| ZAP baseline | about 6 min |
| ZAP active scan of the login | about 15 min |

## Scene 1: start the lab, before the fix (about 2 min)

```powershell
docker network create --internal tm-lab
docker network create tm-pub
docker run -d --name juice-shop --network tm-pub -p 127.0.0.1:3000:3000 bkimminich/juice-shop:latest
docker network connect --alias juice-shop tm-lab juice-shop
py tools\phase3_lab.py before isolation      # shows: shop reachable, internet and host blocked
```

Show http://127.0.0.1:3000 in the browser.

## Scene 2: find the vulnerabilities

```powershell
py tools\phase3_lab.py before nmap trivy zap-baseline
py tools\phase3_lab.py before zap-active      # the slow part: record the start and the result only
Get-Content evidence\phase3\before\zap-active-alerts.txt   # "SQL Injection ... param=email"
```

## Scene 3: the live attack, before the fix

```powershell
py tools\phase3_lab.py before sqli            # "SQL injection login bypass: HTTP 200 -> BYPASS SUCCEEDED"
```

## Scene 4: compare the two fix options

```powershell
docker build -t shopnova/juice-shop-patched:ca-06 03-vulnerability\lab\fix
docker run -d --name app-patched --network tm-lab shopnova/juice-shop-patched:ca-06
docker run -d --name waf-test --network tm-lab -e BACKEND=http://juice-shop:3000 -e PORT=8080 owasp/modsecurity-crs:nginx
Start-Sleep 40                                 # Juice Shop needs about 30 s to start
py tools\phase3_lab.py options fix-options     # WAF: 403; patched route: 401; real login still 200
```

## Scene 5: deploy the fix and repeat the same attack

The proxy uses the Phase 3 configuration, which does not yet contain the INC-01 block.

```powershell
docker rm -f juice-shop waf-test
docker run -d --name shop-proxy --network tm-pub -p 127.0.0.1:3000:3000 `
  -v "${PWD}\03-vulnerability\lab\fix\nginx-hardening-phase3.conf:/etc/nginx/conf.d/default.conf:ro" nginx:1.27
docker network connect --alias juice-shop tm-lab shop-proxy
py tools\phase3_lab.py after isolation sqli zap-baseline    # same attack: HTTP 401 -> blocked
```

## Scene 6: the incident INC-01

The attack logs in with the published Juice Shop support password, which stands for the phished
password in the scenario.

```powershell
py tools\phase4_attack.py attack               # 28 requests, 24 accounts exposed
py tools\phase4_detect.py                      # three High alerts (rules 1 to 3)
py tools\phase4_contain.py                     # password reset (CA-23) and narrow proxy block (CA-22/CA-25)
py tools\phase4_attack.py verify-containment   # 401 and 403: CONTAINED
```

**Restart note.** Juice Shop recreates its database at every start, which restores the published support
password. After any restart, run `py tools\phase4_contain.py` again (POL-05 v1.1, statement 10).

## Scene 7: the breach clock and the validators

```powershell
py tools\breach_clock.py --inc INC-01          # all Art. 33 milestones met
py tools\validate_phase6.py                    # runs the validators of every phase
```

## Clean up

```powershell
docker rm -f shop-proxy app-patched juice-shop waf-test 2>$null
docker network rm tm-lab tm-pub
```

**Greenbone** is not part of the recordings. Its containers are stopped but their data is kept; restart
them with:

```powershell
docker compose -f $HOME\greenbone-community-container\docker-compose.yml start
```
