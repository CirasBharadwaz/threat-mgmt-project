# GDPR and security baseline gap assessment

ShopNova GmbH, version 1.0, 2026-11-16. Prepared by: Information Security Officer. Reviewed by: Data Protection Officer.

## 1. Purpose and method

This assessment records where ShopNova stands today (the "basic maturity" assumed in the scope statement)
against the requirements of the GDPR, the BDSG, ISO/IEC 27001:2022 and NIST CSF 2.0. Each gap points to
the policy that closes it (POL-xx), and from Phase 2 onwards to the risk (R-xx) and corrective action
(CA-xx) that track it.

The current state is based on the scope statement assumptions: no formal policies, ad hoc patching, no
tested incident response plan. Where a fact is not known, it is marked **to verify**.

## 2. Maturity overview (NIST CSF 2.0 tiers)

The tiers are: Tier 1 Partial, Tier 2 Risk Informed, Tier 3 Repeatable, Tier 4 Adaptive.

| CSF function | Current tier | Target tier (12 months) | Main reason for the gap |
|---|---|---|---|
| Govern (GV) | 1 | 2 | No policies, roles or risk appetite before Phase 1 |
| Identify (ID) | 1 | 2 | Asset register and data inventory only created in Phase 0; no risk assessment yet |
| Protect (PR) | 1 | 2 | No MFA, support staff hold admin rights on A-02, backups untested |
| Detect (DE) | 1 | 2 | No central logging or alerting |
| Respond (RS) | 1 | 2 | No incident response plan or breach notification procedure |
| Recover (RC) | 1 | 2 | Restores never tested; no recovery targets |

## 3. Gap register

| # | Requirement | Reference | Current state | Target state | Closed by | Tracked as | Priority |
|---|---|---|---|---|---|---|---|
| 1 | Information security policy approved by management | ISO 27001 cl. 5.2, A.5.1; CSF GV.PO | None | POL-01 approved | POL-01 | n/a (closed in Phase 1) | High |
| 2 | Defined security and privacy roles | ISO 27001 A.5.2; CSF GV.RR | No owner for security; no DPO | Roles in governance structure; external DPO designated | governance-structure.md | n/a (closed in Phase 1) | High |
| 3 | DPO designated and notified to the BlnBDI | GDPR Art. 37(1), 37(7); BDSG § 38 | Not designated (26 people process data daily, so it is required) | External DPO appointed, contact details published and notified | POL-03 | Action outside the risk register (Managing Director) | High |
| 4 | Records of processing | GDPR Art. 30 | Data inventory exists (purpose, legal basis, recipients, retention) but lacks controller and DPO details, transfers and security measures | Complete Art. 30 record | POL-03 | R-14, R-15 (indirect) | Medium |
| 5 | Legal basis for each purpose | GDPR Art. 6, 7 | Recorded in data inventory | Maintained | POL-03 | n/a (met) | Low |
| 6 | Privacy notice | GDPR Art. 13 | To verify: a notice exists but has not been checked against the data inventory | Notice matches inventory and names all recipients | POL-03 | Action outside the risk register | Medium |
| 7 | Data subject request process | GDPR Art. 12 to 22 | Ad hoc email handling, no log, no deadline tracking | Procedure, log, one-month tracking | POL-03 | R-15 / CA-18 | Medium |
| 8 | Retention and deletion | GDPR Art. 5(1)(e), 17 | Periods defined in inventory; no deletion routine; backups keep data | Automated deletion; backup expiry | POL-03, POL-07 | R-14 / CA-17 | Medium |
| 9 | Proof of withdrawn consent | GDPR Art. 7(1), 17(3)(e) | Open: how long proof of a withdrawn newsletter consent may be kept is not decided | Decision by the DPO, recorded in the data inventory | POL-03 | R-16 (consent records) | Low |
| 10 | Processor contracts | GDPR Art. 28 | No data processing agreement with A-06 or the hosting provider; roles of A-05 and A-08 not assessed | Role decided for every supplier; data processing agreements signed | POL-06 | R-10, R-09 / CA-13 | High |
| 11 | Third-country transfers | GDPR Art. 44 to 46 | Hosting in the EU; to verify: location and sub-processors of A-06 | Transfers documented, or none | POL-06 | R-10 / CA-13 | Medium |
| 12 | Least privilege and MFA | GDPR Art. 32; ISO 27001 A.5.15, A.8.2, A.8.5 | Support staff hold admin rights on A-02 (deliberate weak spot); no MFA | Role-based support access; MFA everywhere in POL-04 statement 4 | POL-04 | R-01, R-04 / CA-01, CA-02, CA-08 | Critical |
| 13 | Vulnerability management | GDPR Art. 32(1)(d); ISO 27001 A.8.8 | Ad hoc patching, no scanning | Monthly scans, deadlines, verified fixes | POL-02 | R-03, R-12 / CA-05, CA-06, CA-07 | Critical |
| 14 | Backups and restore | GDPR Art. 32(1)(c); ISO 27001 A.8.13 | Nightly backups in the same account, unencrypted, never restored | 3-2-1, immutable copy, quarterly restore tests | POL-07 | R-05, R-06 / CA-09 | High |
| 15 | Endpoint security | ISO 27001 A.8.1, A.8.7 | No disk encryption or remote wipe confirmed | BitLocker, EDR, device management | POL-08 | R-08, R-02 / CA-12 | Medium |
| 16 | Logging and monitoring | ISO 27001 A.8.15, A.8.16; CSF DE.CM | No central logging | SIEM with daily alert review | POL-05 | R-11 / CA-15 | High |
| 17 | Incident response and breach notification | GDPR Art. 33, 34; ISO 27001 A.5.24 to A.5.28 | No plan, no breach register | POL-05, procedure, annual exercise | POL-05 | R-11 / CA-14 | High |
| 18 | DPIA | GDPR Art. 35 | None | DPIA for customer data processing | POL-03, POL-09 | `02-risk/dpia.md` | Medium |
| 19 | Security awareness | ISO 27001 A.6.3; CSF PR.AT | No training | Annual training plus phishing simulations | POL-01, POL-08 | R-02 / CA-04 | High |
| 20 | Cookie consent | TDDDG § 25 | To verify: consent banner behaviour not checked | Non-essential cookies only after consent | POL-03 | Action outside the risk register | Medium |
| 21 | Risk management method | ISO 27001 cl. 6.1.2, 6.1.3; CSF GV.RM | None | POL-09 method applied in Phase 2 | POL-09 | n/a (closed in Phase 1) | High |

## 4. Summary

- **Closed by Phase 1 documents:** gap 1, gap 2 and gap 21 (policies, roles and risk method now exist). gap 5 was already met.
- **Most urgent:** gap 12 and gap 13 are rated Critical. They map to the two Critical risks R-01 and R-12 in Phase 2.
- **Actions outside the risk register:** gap 3 (appoint the DPO), gap 6 (privacy notice check) and gap 20 (cookie check) are compliance tasks for the Managing Director and the DPO.
- **Open question:** gap 9 (proof of withdrawn consent) needs a DPO decision.

## 5. Limits of this assessment

The current state is assumed from the case description, not audited. The "to verify" items would need
evidence from the real systems. ISO/IEC 27001 certification is not a goal of this project; the standard
is used as a control reference.
