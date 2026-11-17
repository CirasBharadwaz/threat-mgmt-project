# POL-01 Information Security Policy

| Field | Value |
|---|---|
| Policy ID | POL-01 |
| Owner | Information Security Officer |
| Approved by | Managing Director |
| Version | 1.0 |
| Approved on | 2026-11-16 |
| Next review | 2027-11-16 |
| Classification | Internal |
| Applies to | A-01, A-02, A-03, A-04, A-05, A-06, A-07, A-08 |
| Framework references | ISO/IEC 27001:2022 clause 5.2, A.5.1, A.5.2, A.5.4, A.5.9, A.5.12, A.5.31, A.6.3; NIST CSF 2.0 GV.PO, GV.RR, GV.OC, GV.OV, ID.AM, PR.AT; GDPR Art. 24, 32 (full list in `../framework-mapping.csv`) |

## Purpose

ShopNova GmbH runs an online shop that holds personal data of about 20,000 EU customers. This policy is
management's statement of direction for protecting that data and the systems that process it. It sets the
security objectives, commits the resources needed, and is the parent of the topic-specific policies
POL-02 to POL-09.

ShopNova protects information so that:

- customer personal data stays confidential and is used only for the purposes recorded in the data inventory;
- orders, payments and customer records stay accurate and complete (integrity);
- the web shop and customer database are available when customers and staff need them (availability);
- ShopNova meets its legal duties under the GDPR, the BDSG and German commercial and tax law, and its contractual duties to customers and partners.

## Scope

This policy applies to:

- all assets in the asset register: the web shop (A-01), customer database (A-02), backups (A-03), staff laptops (A-04), the payment, email and delivery integrations (A-05, A-06, A-08) and the IT administrators (A-07);
- all personal data categories in the data inventory (D-01 to D-05);
- all employees, temporary staff and contractors, and suppliers that handle ShopNova information under contract.

Out of scope, as set in the scope statement: physical security of buildings, the internal systems of
third-party providers, and the HR and payroll system.

## Roles

| Role | Responsibility under this policy |
|---|---|
| Managing Director | Accountable for information security. Approves this policy and all POL-xx, provides budget and staff, chairs the Security and Privacy Steering Meeting, accepts risks above appetite. |
| Information Security Officer | Owns this policy. Runs the security programme, maintains the policy set, reports KPIs, coordinates risk assessment and incident response. |
| Data Protection Officer | Advises on data protection aspects of all policies and monitors compliance with the GDPR. |
| Head of IT | Implements technical controls and owns the assets assigned in the asset register. |
| Asset owners (Finance Lead, Marketing Lead, Logistics Lead) | Make sure their assets and supplier relationships meet this policy. |
| All staff | Follow this policy and the topic-specific policies, complete training, report incidents. |

Full role definitions are in `../governance-structure.md`, and task assignments in `../raci-matrix.csv`.

## Policy statements

1. **Management commitment.** The Managing Director approves the security objectives, makes sure they fit
   ShopNova's business goals, and provides the resources to meet them. Security is a standing item in the
   monthly Security and Privacy Steering Meeting.

2. **Security objectives.** ShopNova sets measurable objectives and tracks them through the KPI register:
   - 100% of privileged and remote accounts use multi-factor authentication by 2026-12-31 (KPI-03);
   - critical vulnerabilities are fixed within 7 days (KPI-01), and at least 95% of critical and high findings within the POL-02 deadlines (KPI-02);
   - every suspected personal data breach gets a notification decision within 72 hours of awareness (KPI-05);
   - at least 95% of staff complete security and privacy training each year (KPI-07).

3. **Risk-based approach.** Controls are chosen on the basis of assessed risk, using the method in POL-09.
   Every significant risk has an ID (R-xx), an owner and a treatment decision.

4. **Asset management and classification.** Every asset has an ID and a named owner in the asset register.
   Information is classified by the sensitivity recorded in the data inventory:

   | Classification | Data inventory sensitivity | Examples | Minimum handling |
   |---|---|---|---|
   | Public | not applicable | product catalogue | none |
   | Internal | Low | D-05 newsletter consent | access limited to staff |
   | Confidential | Medium | D-01 identity, D-02 address | need-to-know access, encrypted in transit |
   | Strictly confidential | High | D-03 payment reference, D-04 credentials | need-to-know access, encrypted in transit and at rest, access logged |

5. **Topic-specific policies.** The following policies implement this policy and have the same authority:
   POL-02 Vulnerability and Patch Management, POL-03 Data Protection, POL-04 Access Control,
   POL-05 Incident Response and Breach Notification, POL-06 Supplier Security, POL-07 Backup and Recovery,
   POL-08 Acceptable Use and Endpoint, POL-09 Risk Management.

6. **Legal and contractual requirements.** ShopNova identifies and meets the requirements of the GDPR, the
   BDSG, the TDDDG (cookies and tracking), § 257 HGB and § 147 AO (retention), and its contracts. Card data
   is handled only by the payment provider (A-05) through tokenisation, which keeps ShopNova's PCI DSS
   duties to a minimum. The exact level is to be confirmed with the provider.

7. **Secure operations.** Changes to production systems follow a documented change process. Systems are
   kept patched (POL-02), protected against malware, and send security logs to central monitoring (POL-05).
   Personal data is encrypted in transit (TLS 1.2 or higher) and, for Strictly confidential data, at rest.

8. **People.** Staff sign a confidentiality commitment before getting access to personal data. All staff
   complete security and privacy training at onboarding and every year after. Leavers lose access on their
   last working day (POL-04).

9. **Suppliers.** Suppliers that process ShopNova data are assessed and bound by contract (POL-06).

10. **Incidents.** Everyone reports suspected security incidents and personal data breaches at once. They
    are handled under POL-05.

11. **Continuity.** Critical data is backed up and restores are tested (POL-07).

12. **Continual improvement.** Lessons from incidents, audits, vulnerability scans and KPI trends lead to
    corrective actions (CA-xx). The steering meeting reviews the security programme as a whole at least once a year.

## Compliance

- **Monitoring:** the Information Security Officer checks compliance through the KPIs in `../kpi-register.csv`, the
  vulnerability and access reviews, and the annual policy review. The DPO checks the data protection aspects.
- **Exceptions:** an exception to any POL-xx must be requested in writing, risk-assessed under POL-09,
  limited in time (at most 12 months), approved by the Information Security Officer (or by the Managing
  Director for High or Critical risks), and recorded in the risk register.
- **Violations:** breaches of this policy are handled under employment law and the applicable disciplinary
  process. Deliberate or grossly negligent breaches can lead to termination of contract.

## Review

The Information Security Officer reviews this policy every year, and also after a SEV-1 or SEV-2 incident, a
significant change to the shop or its suppliers, or a change in the law. The Managing Director approves
every new version.
