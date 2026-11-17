# POL-09 Risk Management Policy

| Field | Value |
|---|---|
| Policy ID | POL-09 |
| Owner | Information Security Officer |
| Approved by | Managing Director |
| Version | 1.0 |
| Approved on | 2026-11-16 |
| Next review | 2027-11-16 |
| Classification | Internal |
| Applies to | A-01, A-02, A-03, A-04, A-05, A-06, A-07, A-08 |
| Framework references | ISO/IEC 27001:2022 clauses 6.1.2, 6.1.3, 8.2, 8.3; ISO/IEC 27005:2022; NIST CSF 2.0 GV.RM, ID.RA; GDPR Art. 24, 32(2), 35 (full list in `../framework-mapping.csv`) |

## Purpose

To identify, analyse, evaluate and treat information security and privacy risks in the same way every
time, so that ShopNova spends its limited security budget where it matters most. The policy defines the
scales, the scoring, the risk appetite and the treatment rules used in `02-risk/`.

## Scope

- Risks to the confidentiality, integrity and availability of all assets (A-01 to A-08) and personal data (D-01 to D-05).
- Risks to the rights and freedoms of data subjects, which are assessed in more depth in the DPIA.
- Compliance risks under the GDPR and the BDSG.

## Roles

| Role | Responsibility |
|---|---|
| Managing Director | Sets the risk appetite. Accepts any High or Critical risk that is not fully treated. Approves the treatment plan. |
| Information Security Officer | Owns this policy. Runs the process, maintains the risk register, reports to the steering meeting. |
| Risk owners (the role named per risk, usually the asset owner) | Agree the score, choose the treatment, deliver their corrective actions. |
| Data Protection Officer | Advises on risks to data subjects and on whether a DPIA is needed. |

## Policy statements

1. **Process.** Risk management follows ISO/IEC 27001:2022 clauses 6.1.2 and 6.1.3 and ISO/IEC 27005:2022:
   1. Establish the context (scope statement, asset register, data inventory).
   2. Identify risks.
   3. Analyse them (likelihood and impact).
   4. Evaluate them against the appetite.
   5. Treat them.
   6. Monitor and review.

2. **Risk identification.** Risks are identified per asset and per data category. Each one is written as
   **"threat exploits weakness in asset, leading to consequence"**. Every risk gets a permanent R-xx ID,
   a risk owner, and links to the assets (A-xx), data (D-xx) and governing policies (POL-xx).

3. **Likelihood scale.**

   | Score | Level | Meaning for ShopNova |
   |---|---|---|
   | 1 | Rare | Less than once in 5 years; needs an unusual combination of failures |
   | 2 | Unlikely | Once in 2 to 5 years; known attack, but strong controls exist |
   | 3 | Possible | About once a year; known attack, controls partly in place |
   | 4 | Likely | Several times a year; common attack against web shops, weak or no controls |
   | 5 | Almost certain | Monthly or more often, or already happening |

4. **Impact scale.** The highest-scoring dimension sets the impact.

   | Score | Level | Personal data and data subjects | Financial | Legal and regulatory | Operations | Reputation |
   |---|---|---|---|---|---|---|
   | 1 | Negligible | No personal data affected | < EUR 10k | None | Outage < 1 hour | No external attention |
   | 2 | Minor | < 100 customers, Low or Medium data only | EUR 10k to 50k | Internal breach record only | Outage < 4 hours | A few complaints |
   | 3 | Moderate | 100 to 1,000 customers, or a few D-03 or D-04 records | EUR 50k to 250k | BlnBDI notification likely | Outage < 1 day | Local or social media |
   | 4 | Major | 1,000 to 10,000 customers | EUR 250k to 1M | Notification to the BlnBDI and to customers; fine possible | Outage 1 to 3 days | National media |
   | 5 | Severe | > 10,000 customers, or D-03 or D-04 at scale | > EUR 1M | High-risk breach, significant fine (Art. 83) | Outage > 3 days | Lasting loss of trust |

5. **Score and level.** Risk score = likelihood × impact.

   | Score | Level |
   |---|---|
   | 1 to 4 | Low |
   | 5 to 9 | Medium |
   | 10 to 16 | High |
   | 20 to 25 | Critical |

6. **Risk appetite and acceptance.**

   | Level | Appetite | Who may accept | Treatment deadline |
   |---|---|---|---|
   | Low | Within appetite | Risk owner | none; review every year |
   | Medium | Tolerable | Risk owner, with Information Security Officer sign-off | treat where cost-effective; review every 6 months |
   | High | Outside appetite | Managing Director only, in writing, for at most 6 months | treatment plan within 30 days, done within 90 days |
   | Critical | Outside appetite | Managing Director only, as a temporary exception with a deadline of at most 60 days | start at once; Managing Director informed within 1 working day |

   A risk that could cause **high risk to data subjects** cannot be accepted without the DPO's advice. If
   it stays high after treatment, prior consultation with the BlnBDI is considered (Art. 36 GDPR).

7. **Treatment options.**
   - **Reduce** with controls.
   - **Transfer** through contracts or insurance. Accountability under the GDPR cannot be transferred.
   - **Avoid** by stopping the activity.
   - **Accept** within the appetite rules above.

8. **Treatment plan.** Every risk that is reduced, transferred or avoided has at least one action (CA-xx)
   with an owner, a due date, a status and the ISO/IEC 27001:2022 Annex A controls it implements. The
   plan is `02-risk/risk-treatment-plan.csv`, and each link is recorded as `R-xx treated-by CA-xx`.

9. **Current and target risk.** Each risk is scored twice:
   - **current:** with the controls that exist today;
   - **target:** expected once the planned actions are done.

   When an action is finished, or after an incident, the risk is re-scored and the link
   `CA-xx re-scores R-xx` is recorded.

10. **Visualisation.** Current and target risks are shown on a 5 × 5 heat map
    (`02-risk/risk-heatmap.md`), generated from the register so that the two never disagree.

11. **Monitoring and review.** The register is reviewed every quarter at the steering meeting, and also
    after any SEV-1 or SEV-2 incident, a new vulnerability rated Critical, or a significant change. KPI-10
    tracks the share of High and Critical risks with an approved treatment plan.

12. **Link to the DPIA.** Risks that involve personal data are also assessed from the data subject's
    point of view in the DPIA (`02-risk/dpia.md`), which uses the same R-xx IDs.

## Compliance

The DPO and the Information Security Officer check every quarter that every risk follows the scales and
appetite rules. `tools/validate_phase2.py` checks the register automatically: scores, levels, owners and
links. Overdue treatment actions are escalated to the Managing Director.

## Review

The Information Security Officer reviews this policy every year. The Managing Director re-confirms the
risk appetite every year and after any SEV-1 incident.
