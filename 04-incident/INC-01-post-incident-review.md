# INC-01 post-incident review (POL-05 statement 13)

Participants (simulated): Information Security Officer (incident lead), Head of IT, DPO, Head of Support,
Managing Director. Date: 2026-11-17, same day as the incident. Format: blameless review. The question is
why the system allowed the incident, not who made a mistake.

## 1. Summary

| Item | Value |
|---|---|
| Incident | INC-01, personal data breach through a phished support account with admin rights |
| Severity | SEV-1 (customer data of about 20,000 people in the ShopNova scenario; 24 lab accounts) |
| Attack window | 2026-11-17 17:37:37 to 17:37:41 UTC (4 seconds, 28 requests) |
| Detected | 17:37:55 UTC, by log detection rules 1 to 3 (KPI-06: 18 seconds) |
| Contained | 17:38:27 UTC (50 seconds after the attack started) |
| Awareness | 17:39:18 UTC |
| Notification decision | 17:40:13 UTC (KPI-05: 0.02 hours; target at most 72 hours) |
| BlnBDI notified | 17:40:13 UTC (simulated); Art. 33 deadline 2026-11-20 17:39 UTC |
| Customers informed | 17:40:13 UTC (simulated, voluntary) |
| Data | D-01 (name, email) and D-06 (IP addresses); no passwords, payment data or addresses |

The full timeline is in `INC-01-timeline.csv`. Run `py tools\breach_clock.py --inc INC-01` to check it
against the deadlines.

## 2. Root causes

| # | Cause | Linked item |
|---|---|---|
| 1 | Support staff hold **admin rights** they do not need. A stolen support password therefore gave access to every customer record | R-01, V-06, POL-04 known gap; CA-01 was still "Planned" |
| 2 | The support account is **shared**, not personal. This breaks POL-04 statement 2 and makes it impossible to say which person's password was phished | V-06, POL-04 |
| 3 | **No multi-factor authentication**, so the password alone was enough | CA-02 still "Planned" |
| 4 | **Issued login tokens stay valid after a password change.** The reset alone would not have stopped the attacker; the proxy block was needed | new CA-24 |
| 5 | The admin data endpoints have **no rate limit and no volume check**. 28 requests in 4 seconds were allowed | rule 2 now detects this; prevention still open |

## 3. What went well

- **Detection worked within seconds.** Rules 1 to 3 (CA-15) each raised a High alert. The scenario
  assumes the detection job runs every 15 minutes; in production, the worst case is therefore about
  15 minutes, still far inside the 24-hour KPI-06 target.
- **Containment was fast and verified.** The replay of the attack failed (HTTP 401 and 403).
- **Evidence was preserved.** Logs and attack data were saved before any further change.
- **The Phase 3 fixes helped.**
  - The SQL injection (V-01) was closed, so the attacker needed a real password.
  - Because the access logs were no longer public (V-04), the attacker could not read them.
- **The decision process followed POL-05.** It ran from risk assessment through the DPO's advice to the
  Managing Director's decision, all well inside 72 hours.

## 4. What went less well

- **The emergency block also stopped new sign-ups.** It closed `/api/Users`, which the shop also uses for
  `POST` customer registration. This is acceptable for a short time, but the rule must be narrowed (CA-25).
- **Known risk, not treated in time.** R-01 was rated Critical in Phase 2, with a temporary exception
  until 2026-12-15. The incident happened inside that exception window. The Managing Director accepted a
  Critical risk for four weeks, and it materialised.
- **A restart undid the containment (found during Phase 5).** Docker restarted at 18:04 UTC. The lab
  app re-creates its database at every start, which silently restored the phished support password.
  The CA-25 test at 18:09 UTC caught it (`evidence/phase5/ca25-test-run1-reset-lost-after-restart.json`),
  and the reset was re-applied. Lesson: containment kept in application state must be re-verified after
  any restart or redeployment. This is now POL-05 v1.1 statement 10.
- **Thin detection basis.** Detection relied on the proxy log only; the application log has the same
  requests but no user identity. A SIEM with user context (the original CA-15 plan with Wazuh) would
  improve triage.

## 5. Corrective actions

| ID | Action | Owner | Due | Status |
|---|---|---|---|---|
| CA-22 | Emergency block of the admin user-data endpoints at the proxy | Head of IT | 2026-11-17 | Done |
| CA-23 | Reset the support account password; then replace the shared account with personal accounts | Head of IT | 2026-11-17 | Done (reset); personal accounts under CA-01 |
| CA-24 | Revoke issued tokens on password change and shorten token lifetime | Head of IT | 2026-12-15 | Planned |
| CA-25 | Narrow the CA-22 rule so customer sign-up (`POST /api/Users`) works again, while reading user data stays blocked | Head of IT | 2026-11-18 | Done 2026-11-17 (tested: sign-up 201, user-data reads 403; `evidence/phase5/ca25-containment-narrowed.json`) |
| CA-01 | Remove admin rights from support (existing) | Head of IT | **brought forward to 2026-11-24** | Planned |
| CA-02 | MFA for staff accounts (existing) | Head of IT | **brought forward to 2026-11-24** | Planned |

The links `INC-01 resolved-by CA-22` and `INC-01 resolved-by CA-23` are recorded in `traceability.csv`.

## 6. Effect on risks (input to Phase 5)

| Risk | Change | Reason |
|---|---|---|
| R-01 | Likelihood rises from 4 to 5 ("already happening") until CA-01 and CA-02 are done | The risk materialised |
| R-11 | Likelihood can fall once CA-14 and CA-15 are confirmed | Detection 18 s, decision 0.02 h, both far inside target |
| R-02 | No change | Phishing is assumed as the entry point; it still needs CA-04 training |

The formal re-scoring (`CA-xx re-scores R-xx`) follows in Phase 5.

## 7. Lessons for governance

- **A temporary exception to a Critical risk is a bet.** POL-09 allows up to 60 days. The review
  recommends cutting this to 14 days for risks involving customer data at scale.
- **POL-04 statement 2 (no shared accounts) needs a check.** It is added to the quarterly access review (CA-03).
- **Policies updated (Phase 5).**
  - POL-04 v1.1 adds statement 10 (invalidate tokens on a password reset; 1-hour staff tokens) and
    corrects the false compensating control in the known gap.
  - POL-05 v1.1 extends statement 10 (revoke tokens during containment, keep blocks narrow, re-verify
    after restarts).
  - Both changes are traceable as `INC-01 resolved-by CA-24/CA-25` and `CA-24/CA-25 updates POL-04/POL-05`.
