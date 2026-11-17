# 2 Governance

Governance answers three questions: who decides, by which rules, and how is compliance checked. For
ShopNova, the starting answer to all three was "nobody formally". This chapter describes the structure
that was set up in Phase 1 (`01-governance/`).

## 2.1 Roles and accountability

The **Managing Director** is accountable for information security and data protection, because the GDPR
places accountability on the controller (Art. 5(2) and 24 GDPR). Two specialist roles support the
Managing Director:

- An **Information Security Officer**, held part-time by one senior employee who reports directly to the
  Managing Director. The role sits outside the IT department on purpose: the Head of IT runs the systems
  and the Information Security Officer checks them. This follows the segregation-of-duties control in
  ISO/IEC 27001:2022 A.5.3.
- An **external Data Protection Officer (DPO)**. § 38(1) BDSG requires a DPO when, as a rule, at least
  20 persons are constantly engaged in automated processing of personal data. An estimate of ShopNova's
  teams gives 26 such people (support, logistics, IT, marketing, finance). An internal DPO would be hard
  to staff without a conflict of interest, because the Head of IT and the Managing Director decide on the
  purposes and means of processing (CJEU, 2023).

The Security and Privacy Steering Meeting (Managing Director, Information Security Officer, DPO, Head of
IT) meets every month. A RACI matrix (`raci-matrix.csv`) assigns 19 recurring activities, each with
exactly one Accountable role. Examples are approving policies, accepting risks, deciding on breach
notification and handling data subject requests.

## 2.2 Policy framework

Nine policies (POL-01 to POL-09) were written. The top-level Information Security Policy (POL-01) sets
measurable objectives, links them to KPIs, and lists the topic-specific policies:

| ID | Policy | Main purpose | Owner |
|---|---|---|---|
| POL-01 | Information Security Policy | direction, objectives, classification | Information Security Officer |
| POL-02 | Vulnerability and Patch Management | scanning, deadlines by severity, verification | Head of IT |
| POL-03 | Data Protection | GDPR principles, rights, retention, DPIA | Managing Director |
| POL-04 | Access Control | least privilege, MFA, privileged access | Head of IT |
| POL-05 | Incident Response and Breach Notification | lifecycle, severity, Art. 33/34 | Information Security Officer |
| POL-06 | Supplier Security | processor or controller role, Art. 28 agreements | Information Security Officer |
| POL-07 | Backup and Recovery | 3-2-1 rule, restore tests | Head of IT |
| POL-08 | Acceptable Use and Endpoint | laptops, remote work | Head of IT |
| POL-09 | Risk Management | scales, appetite, treatment rules | Information Security Officer |

Every policy has the same six sections: purpose, scope, roles, policy statements, compliance, review.
The validator enforces this. Three design choices are worth noting:

- **Policies connect to later phases.** POL-02 sets the remediation deadlines that Phase 3 measures
  (7 days for Critical findings, 72 hours if the vulnerability is known to be exploited). POL-05 sets the
  72-hour breach notification clock that Phase 4 tests. POL-09 defines the scoring used in Phase 2.
- **Known weaknesses are recorded, not hidden.** POL-04 requires least privilege, but also documents that
  support staff currently hold admin rights on A-02. The gap is accepted only temporarily by the Managing
  Director, with a deadline. A policy that pretended the gap did not exist would be worse than useless,
  because nobody would treat the risk.
- **Data protection is owned by management.** POL-03 is owned by the Managing Director, not by the DPO.
  This keeps the DPO in an advisory and monitoring role (Art. 39 GDPR).

## 2.3 Mapping to frameworks

`framework-mapping.csv` maps every policy to at least one ISO/IEC 27001:2022 Annex A control, one NIST
CSF 2.0 category and one GDPR or BDSG article, with 110 references in total. For example, POL-05 maps to
A.5.24–A.5.28 (incident management), to the CSF categories RS.MA, RS.AN, RS.CO and RS.MI, and to
Art. 33 and 34 GDPR. The mapping shows that the policy set covers the governance function that NIST added
in CSF 2.0 (GV: organisational context, risk strategy, roles, policy, oversight and supply chain). It also
lets an auditor check coverage from either side: from a control to a policy, or from a policy to a control.

## 2.4 Measuring governance: KPIs

Eleven KPIs (KPI-01 to KPI-11) turn the objectives into numbers. Each one has a formula, a target, an
owner, a data source and the phase in which it is first measured. Most baselines are "not measured" or 0%,
which is honest for a company at basic maturity. The KPIs that later chapters report are KPI-01 (time to
fix Critical vulnerabilities, Phase 3), KPI-05 (hours from awareness of a breach to the notification
decision, Phase 4) and KPI-06 (time to detect, Phase 4).

## 2.5 Baseline gap assessment

The gap assessment (`gdpr-baseline-gap-assessment.md`) compares the current state with GDPR, ISO/IEC 27001
and NIST CSF requirements. It records 21 gaps. On the NIST CSF 2.0 tiers, ShopNova sits at Tier 1
(Partial) in all six functions, with Tier 2 (Risk Informed) as the 12-month target.

- **Closed by Phase 1 documents:** three gaps (policy, roles, risk method).
- **Most urgent:** least privilege and MFA (gap 12), and vulnerability management (gap 13). They lead
  directly to the two Critical risks in Chapter 3.
- **Compliance tasks for management:** appointing the DPO, checking the privacy notice, and checking the
  cookie consent under § 25 TDDDG. These do not need a risk score.

## 2.6 Discussion

Writing policies is fast; making them true is slow. The value of Phase 1 lies less in the text of the
nine policies than in three properties:

- every requirement has a named owner;
- every policy states how compliance will be measured;
- every policy links forward to risks, vulnerabilities and incidents through IDs.

The limitation is that the governance structure has not yet been tested by real use. Chapters 4 and 5
provide that first test.
