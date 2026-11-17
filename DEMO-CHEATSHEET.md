# Demo cheat sheet (one page)

Full steps and safety notes: [`DEMO-RUNBOOK.md`](DEMO-RUNBOOK.md). Record from a separate clone
(`$HOME\threat-mgmt-demo`), because the scripts overwrite `evidence\`. Run all commands in PowerShell,
from the project root.

## Before recording

| Step | Command | Expected |
|---|---|---|
| Clean slate | `py tools\demo_reset.py` | `port 127.0.0.1:3000 is free; ready for Scene 1` |
| Preflight | `py tools\demo_preflight.py` | `Preflight: 0 FAIL, 0 WARN. Ready to record.` |

## Scenes

| # | Show | Command(s) | Expected on screen | Say (one line) |
|---|---|---|---|---|
| 1 | Lab up, isolated | runbook Scene 1 (networks + `juice-shop`), then `py tools\phase3_lab.py before isolation` | `juice-shop:3000 REACHABLE`, internet and host `blocked` | "The shop runs only on 127.0.0.1 and an internal network." |
| 2 | Find vulnerabilities | `py tools\phase3_lab.py before nmap trivy zap-baseline`, then `py tools\phase3_lab.py before zap-active-quick` | Trivy: 116 CVEs, 7 Critical. ZAP: CSP missing, CORS wildcard. Active scan: `High SQL Injection ... param=email` | "A baseline scan is passive; the active scan finds the injection." |
| 3 | Live attack | `py tools\phase3_lab.py before sqli` | `SQL injection login bypass: HTTP 200 -> BYPASS SUCCEEDED` | "Any password, logged in as admin." |
| 4 | Two fix options | runbook Scene 4, then `py tools\phase3_lab.py options fix-options` | WAF 403, patched route 401, real login 200 | "Both block it; only the code fix removes the flaw." |
| 5 | Same attack after the fix | runbook Scene 5, then `py tools\phase3_lab.py after isolation sqli zap-baseline` | `HTTP 401 -> blocked` | "Identical request, now refused." |
| 6 | Incident INC-01 | `py tools\phase4_attack.py attack`, `py tools\phase4_detect.py`, `py tools\phase4_contain.py`, `py tools\phase4_attack.py verify-containment` | 28 requests, 24 accounts; 3 High alerts; `CONTAINED` | "Phished support account with admin rights: detected in seconds, contained in under a minute." |
| 7 | Deadlines and checks | `py tools\breach_clock.py --inc INC-01`, `py tools\validate_phase6.py` | all milestones `met`; 0 failed | "Every claim is traceable and checked." |

## If something goes wrong

| Problem | Fix |
|---|---|
| A command says a container or network already exists | `py tools\demo_reset.py`, then restart from Scene 1 |
| `HTTP 502` from the shop | Juice Shop is still starting; wait about 30 seconds |
| Scene 6 login fails before the attack | The support password is still reset from an earlier run; restart the app container, which resets its database |
| The shop looks broken in the browser | Press Ctrl+F5 (cached old headers) |
| The full ZAP active scan takes too long | Use `zap-active-quick` (SQL injection rule only) |

## After recording

`py tools\demo_reset.py` tears down the lab. Greenbone stays stopped, with its data kept.
