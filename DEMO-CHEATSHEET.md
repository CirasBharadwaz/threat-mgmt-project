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

## Dry run results

Run automatically with `py tools\demo_dryrun.py --scratch-copy --quick` in a scratch copy. The first
attempt (19:48 UTC) failed at Scene 5: nginx was started before it joined `tm-lab` and could not resolve
`app-patched`. The proxy is now created, connected and only then started. The second attempt passed:

| Scene | Duration | Result | Key output |
|---|---|---|---|
| 1 Start the lab, before the fix | 0.1 min | OK | juice-shop:3000       REACHABLE; 1.1.1.1:443 (internet) blocked (OSError); host.docker.internal:3000 (host) blocked (gaierror);  |
| 2 Find the vulnerabilities | 1.5 min | OK | SQL Injection found |
| 3 Live attack, before the fix | 0.0 min | OK |   SQL injection login bypass: HTTP 200 -> BYPASS SUCCEEDED |
| 4 Compare the fix options | 0.8 min | OK | control: 200, option A: 403, option B: 401 |
| 5 Deploy the fix, same attack again | 0.5 min | OK |   SQL injection login bypass: HTTP 401 -> blocked |
| 6 Incident INC-01 | 0.2 min | OK | 28 requests, 24 accounts; 3 High alerts; CONTAINED |
| 7 Breach clock | 0.0 min | OK | breach clock exit 0 (milestones met) |

Times are without narration and use the quick ZAP active scan; the full scan adds about 15 minutes.
