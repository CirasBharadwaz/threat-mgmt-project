# Risk assessment summary

ShopNova GmbH, version 1.0, 2026-11-16. Prepared by: Information Security Officer. Approved by: Managing
Director (simulated). Method: POL-09 (ISO/IEC 27001:2022 clauses 6.1.2 and 6.1.3, ISO/IEC 27005:2022).

## 1. Scope and inputs

- **Scope:** all assets A-01 to A-08 and personal data D-01 to D-05, as set in the scope statement.
- **Inputs:** asset register, data inventory, data flow diagram, the gap assessment in `01-governance/`, and the "basic maturity" assumptions in the scope statement (no formal policies, ad hoc patching, no tested incident response).
- **Files:**
  - `risk-register.csv`: 17 risks (R-17 added in Phase 3);
  - `risk-treatment-plan.csv`: 21 actions (CA-19 to CA-21 added in Phase 3);
  - `risk-heatmap.md`: generated from the register;
  - `dpia.md`: the data subject view.

## 2. Results

| Level | Current | Target |
|---|---|---|
| Critical | 2 | 0 |
| High | 9 | 0 |
| Medium | 5 | 9 |
| Low | 1 | 8 |
| **Total** | **17** | **17** |

**Update 2026-11-17 (Phase 3):** the vulnerability scans found a misconfiguration that no Phase 2 risk
covered: exposed files, public access logs and wildcard CORS. It was added as R-17 (High; treated by
CA-19 and CA-20). This is the feedback loop working as designed. The original Phase 2 result was 16
risks: 2 Critical, 8 High, 5 Medium, 1 Low.

All 11 High and Critical risks have an approved treatment plan with owners and due dates (KPI-10 = 100%).
The plan is that after treatment no risk stays above Medium, so no High risk needs to be accepted. The
two Critical risks still need immediate action. **Plan versus actual (Phase 5, 2026-11-17):** the target
has not been reached yet. After re-scoring with the lab evidence, 2 Critical risks (R-01 at 25, R-03 at
20) and 7 High risks are open (`../05-integration/risk-rescoring.md`).

## 3. Top risks

| Risk | Current | Why it matters | Key actions |
|---|---|---|---|
| R-01 Support admin rights on A-02 misused | 20 Critical | One phished support account gives full control of all customer records. This is the deliberate weak spot from Phase 0. | CA-01, CA-02, CA-03, CA-15 |
| R-12 SQL injection exposes the customer database | 20 Critical | The most common web-shop attack. No secure coding, testing or WAF. | CA-05, CA-06, CA-07 |
| R-02 Phishing compromises staff | 16 High | The usual entry point for R-01 and R-05 | CA-02, CA-04, CA-12 |
| R-03 Outdated components exploited | 16 High | Ad hoc patching; no scanning | CA-05, CA-07 |
| R-11 Breach not detected or notified in 72 hours | 16 High | Turns any breach into a compliance failure | CA-14, CA-15 |

## 4. Treatment decisions

| Decision | Risks | Who decided |
|---|---|---|
| Reduce | R-01 to R-15 | Risk owners; Managing Director approved the plan |
| Accept | R-16 (Low, within appetite) | Marketing Lead, under POL-09 |
| Temporary exception | R-01, until 2026-12-15 (POL-04 known gap) | Managing Director |
| Transfer or avoid | None | Not applicable. Cyber insurance is noted for the next review as a possible transfer for R-05. |

## 5. Links to the next phases

| Phase | Risk | What will happen |
|---|---|---|
| Phase 3 (vulnerability management) | R-03, R-12 | Tested in the local lab. Confirmed findings get V-xx IDs and are linked as `V-xx exposes R-xx`. Scans before and after the fix provide evidence for CA-05 and CA-06. |
| Phase 4 (incident response) | R-01, R-11 | The simulated breach INC-01 is built on R-01: a phished support account with admin rights on A-02, while CA-01 is still planned. It exercises CA-14 and CA-15 and measures KPI-05 and KPI-06. |
| Phase 5 (integration) | all | Risks are re-scored after the lab results (`CA-xx re-scores R-xx`), closing the loop POL to R to V to INC to CA to R. |

## 6. Limits

The likelihood and impact scores are expert judgements for a fictional company, based on common
web-shop threats. They are not drawn from incident statistics. Financial impact bands assume a turnover
in the single-digit millions of euros. The target scores assume that every action is fully implemented.
