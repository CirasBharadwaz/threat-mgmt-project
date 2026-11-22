# ShopNova Cyber Threat Management: lab code and evidence

This repository holds only the lab code of the ShopNova Cyber Threat Management project and the evidence
its runs produced. All explanations are in the project documents: Project Structure, Project Flow,
Governance, Risk Assessment, Vulnerability Assessment, Remediation Plan, Incident Response and Process Review.

## What is here

| Folder | Contents |
|---|---|
| `03-vulnerability/lab/` | Lab topology and commands (`README.md`); targeted ZAP scan of the login (`zap_login_ascan.py`) |
| `03-vulnerability/lab/fix/` | The fixes: patched login route, Dockerfile of the patched image, nginx hardening configurations |
| `tools/` | Lab scripts: reset, preflight, scans, attack, detection, containment, breach clock, Greenbone scan, secrets scan |
| `evidence/` | Raw outputs of the runs: `phase3/` (scans before and after the fixes), `phase4/` (incident INC-01), `phase5/` (two retests of the narrowed containment rule after INC-01, CA-25) |

## Requirements

- Docker Desktop, running
- Python 3 with the `py` launcher (standard library only; nothing to install)
- Windows PowerShell; run every command from the project root
- Runs only on `127.0.0.1`: the shop listens on `127.0.0.1:3000` and on the internal Docker network `tm-lab`; the scripts are written for 127.0.0.1 only

Lab passwords are never stored in this repository: the Greenbone admin password is read from ~\greenbone-community-container\admin-password.txt and the containment script writes the new random support password to ~\threat-lab-secrets\.

## Run order

The scripts overwrite `evidence\`, so run them in a separate clone:

```powershell
git clone https://github.com/CirasBharadwaz/threat-mgmt-project.git $HOME\threat-mgmt-demo
cd $HOME\threat-mgmt-demo
```

1. **Prepare**
   ```powershell
   py tools\demo_reset.py       # removes leftover lab containers and networks; frees port 3000
   py tools\demo_preflight.py   # Docker, memory, disk, images, port 3000, Greenbone stopped
   ```
2. **Start the lab**
   ```powershell
   docker network create --internal tm-lab
   docker network create tm-pub
   docker run -d --name juice-shop --network tm-pub -p 127.0.0.1:3000:3000 bkimminich/juice-shop:latest
   docker network connect --alias juice-shop tm-lab juice-shop
   ```
3. **Scan before the fixes**
   ```powershell
   py tools\phase3_lab.py before isolation nmap trivy zap-baseline zap-active sqli
   ```
4. **Apply the fixes** (patched image and WAF compared, then the hardening proxy with the Phase 3 configuration)
   ```powershell
   docker build -t shopnova/juice-shop-patched:ca-06 03-vulnerability\lab\fix
   docker run -d --name app-patched --network tm-lab shopnova/juice-shop-patched:ca-06
   docker run -d --name waf-test --network tm-lab -e BACKEND=http://juice-shop:3000 -e PORT=8080 owasp/modsecurity-crs:nginx
   Start-Sleep 40                                 # Juice Shop needs about 30 s to start
   py tools\phase3_lab.py options fix-options
   docker rm -f juice-shop waf-test
   docker create --name shop-proxy --network tm-pub -p 127.0.0.1:3000:3000 `
     -v "${PWD}\03-vulnerability\lab\fix\nginx-hardening-phase3.conf:/etc/nginx/conf.d/default.conf:ro" nginx:1.27
   docker network connect --alias juice-shop tm-lab shop-proxy
   docker start shop-proxy   # start only after joining tm-lab, so nginx can resolve app-patched
   ```
5. **Scan after the fixes**
   ```powershell
   py tools\phase3_lab.py after isolation nmap trivy zap-baseline zap-active sqli
   ```
   Optional: full scan (Greenbone). It produced no usable result in our runs.
   ```powershell
   docker compose -f $HOME\greenbone-community-container\docker-compose.yml start
   py tools\greenbone_scan.py --cutoff 20:30
   ```
6. **Incident INC-01**
   ```powershell
   py tools\phase4_attack.py attack               # 28 requests, 24 accounts exposed
   py tools\phase4_detect.py                      # three High alerts (rules 1 to 3)
   py tools\phase4_contain.py                     # password reset and narrow proxy block
   py tools\phase4_attack.py verify-containment   # 401 and 403: CONTAINED
   py tools\breach_clock.py --inc INC-01          # all Art. 33 milestones met
   ```
   Juice Shop recreates its database at every start, which restores the published support password.
   After any restart, run `py tools\phase4_contain.py` again.
7. **Clean up**
   ```powershell
   py tools\demo_reset.py
   ```

Before every commit, run `py tools\secrets_scan.py` to check that no secrets or personal data are committed.

## Where results go

- `evidence\phase3\`: `before\`, `options\` (fix comparison) and `after\` (including Greenbone)
- `evidence\phase4\`: `attack\`, `detection\`, `logs\` and `response\`
- `evidence\phase5\`: two retests of the narrowed containment rule after INC-01 (CA-25); no script in this repository writes this folder
