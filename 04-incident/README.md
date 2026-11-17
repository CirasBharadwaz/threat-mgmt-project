# Phase 4: incident response (INC-01)

A simulated personal data breach, run against the Phase 3 lab shop (127.0.0.1:3000 only) on 2026-11-17.
Detection uses the shop's own logs (proxy access log and Juice Shop application log), not a SIEM.

## Scenario

An attacker phishes the password of the shared support account. As at ShopNova (R-01, POL-04 known
gap), the account holds admin rights. The attacker logs in through the normal shop entry and downloads
all customer accounts through admin endpoints. The SQL injection fixed in Phase 3 (V-01) is no longer
usable, so the attacker needs a real password, which is a realistic next step.

## Files

| File | Content |
|---|---|
| `INC-01-timeline.csv` | 15 events from attack start to review, each with its evidence file |
| `INC-01-breach-assessment.md` | EDPB 9/2022 assessment with an ENISA severity cross-check: breach yes, risk (not high), SEV-1 |
| `INC-01-art33-notification.md` | Notification text for the BlnBDI, covering Art. 33(3)(a) to (d) |
| `INC-01-art34-customer-notice.md` | Customer notice with the content of Art. 34(2), sent voluntarily |
| `INC-01-post-incident-review.md` | Root causes, what went well and less well, CA-22 to CA-25, input to Phase 5 |
| `breach-register.csv` | Art. 33(5) record of every breach |

## Evidence (`../evidence/phase4/`)

| Path | Content |
|---|---|
| `attack/attack-log.json` | Every attacker request with time and HTTP status |
| `attack/exfiltration-summary.json` | What was exposed: field names, counts, masked samples (full data not stored) |
| `attack/containment-verification.json` | Replay after containment: 401 and 403 |
| `logs/proxy-access.log`, `logs/app/` | Raw detection sources |
| `detection/alerts.json`, `detection/detection-report.md` | Alerts from rules 1 to 3 |
| `response/containment-log.txt`, `response/exercise-log.txt` | Response steps with real UTC times; simulated steps are marked |

## Reproduce (PowerShell, project root, Phase 3 "after" lab running)

```powershell
py tools\phase4_attack.py attack
py tools\phase4_detect.py
py tools\phase4_attack.py verify-containment    # after the containment steps
py tools\breach_clock.py --inc INC-01
py tools\validate_phase4.py
```

## Results

| KPI | Result | Target |
|---|---|---|
| KPI-06 time to detect | 18 seconds (attack start 17:37:37, alert 17:37:55 UTC) | at most 24 hours |
| KPI-05 awareness to notification decision | 0.02 hours | at most 72 hours |
| Containment | 50 seconds after the attack started | as fast as possible (POL-05 statement 10) |

The lab compresses time. The detection job ran right after the attack, whereas a production schedule of
every 15 minutes would give a worst case of about 15 minutes. The human steps (informing management,
the decisions, the notifications) were simulated as a tabletop exercise.
