# POL-03 Data Protection Policy

| Field | Value |
|---|---|
| Policy ID | POL-03 |
| Owner | Managing Director |
| Approved by | Managing Director |
| Version | 1.0 |
| Approved on | 2026-11-16 |
| Next review | 2027-11-16 |
| Classification | Internal |
| Applies to | A-01, A-02, A-03, A-04, A-05, A-06, A-08 |
| Framework references | GDPR Art. 5, 6, 7, 12 to 22, 25, 28, 30, 35, 37 to 39; BDSG § 38; TDDDG § 25; ISO/IEC 27001:2022 A.5.31, A.5.33, A.5.34, A.8.10; NIST CSF 2.0 GV.OC, PR.DS (full list in `../framework-mapping.csv`) |

## Purpose

ShopNova is the controller for the personal data of its customers. This policy sets out how ShopNova
meets the GDPR and the BDSG: which principles apply, how data subjects' rights are handled, how long data
is kept, and how data protection is built into systems and contracts. The Managing Director owns this
policy because the controller's accountability (Art. 5(2) and Art. 24 GDPR) lies with executive
management. The Data Protection Officer advises on it but does not own it, to stay independent.

## Scope

- All processing of customer personal data recorded in the data inventory: D-01 identity, D-02 delivery address, D-03 payment reference, D-04 account credentials, D-05 marketing consent.
- All assets that store or process that data (A-01 to A-06, A-08), and all staff and suppliers that handle it.
- Employee data is handled under the same principles, but the HR and payroll system is outside this project's scope.

## Roles

| Role | Responsibility |
|---|---|
| Managing Director | Owns this policy and is accountable for compliance as controller. Decides on DPIAs and breach notifications. |
| Data Protection Officer | Informs and advises, monitors compliance, advises on DPIAs, is the contact point for the BlnBDI and for data subjects (Art. 38 and 39 GDPR). |
| Information Security Officer | Maintains the records of processing with the data owners. Coordinates DPIAs and security measures (Art. 32). |
| Head of Support | Runs the process for data subject requests. |
| Head of IT | Carries out deletion, export and correction of data in the systems. Builds privacy by design into the systems. |
| Marketing Lead | Makes sure newsletter consent is valid and recorded (D-05). |
| All staff | Process personal data only as instructed and for the recorded purpose, and keep it confidential. |

## Policy statements

1. **Principles (Art. 5 GDPR).** ShopNova processes personal data:
   - lawfully, fairly and transparently, with a legal basis recorded for every purpose in the data inventory and a clear privacy notice on the shop (Art. 13);
   - only for the purposes recorded in the data inventory (purpose limitation);
   - limited to what is needed, for example only name, address and, where needed for delivery notices, phone number go to the delivery partner (data minimisation);
   - accurately, with customers able to correct their own account data;
   - no longer than the retention periods in statement 6 (storage limitation);
   - securely, under POL-01, POL-04 and the other security policies (integrity and confidentiality).

   ShopNova documents how it meets each principle, so that it can show compliance (accountability, Art. 5(2)).

2. **Legal bases (Art. 6 and 7).**
   - Order fulfilment, shipping, payment and customer accounts rely on the contract with the customer (Art. 6(1)(b)).
   - Retention of accounting records relies on a legal obligation (Art. 6(1)(c) with § 257 HGB and § 147 AO).
   - The newsletter relies on consent (Art. 6(1)(a)), collected by double opt-in, with time and wording recorded (D-05). Withdrawing consent is as easy as giving it.
   - ShopNova does not use the existing-customer exception of § 7(3) UWG for email advertising.

3. **Records of processing (Art. 30).** The data inventory is the basis of the records of processing. The
   Information Security Officer completes it with the remaining Art. 30(1) fields (controller and DPO
   contact details, transfers to third countries, a general description of security measures) and keeps
   it current.

4. **Transparency (Art. 12 to 14).** The privacy notice on the shop names the controller, the DPO, the
   purposes, legal bases, recipients (payment provider, delivery partner, email provider, hosting
   provider), retention periods and data subject rights. It is reviewed whenever the data inventory changes.

5. **Data subject rights (Art. 15 to 22).** Requests for access, correction, deletion, restriction,
   portability and objection are:
   - accepted through any channel, logged by the Head of Support, and answered within one month (Art. 12(3));
   - extended by up to two more months only for complex requests, with the customer told why within the first month;
   - answered only after a proportionate check of the requester's identity;
   - free of charge, unless a request is manifestly unfounded or excessive.

6. **Retention and deletion.**

   | Data | Retention | Basis |
   |---|---|---|
   | D-01, D-02 | 6 years after the last order | commercial correspondence, § 257 HGB |
   | D-03 | 8 years | accounting vouchers, § 257 HGB and § 147 AO as amended by BEG IV, effective 1 Jan 2025 |
   | D-04 | until the account is deleted | contract |
   | D-05 | until consent is withdrawn | consent, Art. 6(1)(a) GDPR |

   How long proof of a withdrawn consent may be kept, to defend against claims (Art. 7(1) and
   Art. 17(3)(e) GDPR), is an open point in `../gdpr-baseline-gap-assessment.md`.

   Data is deleted or anonymised when the period ends. Data in backups (A-03) expires through backup
   rotation, and deletions are re-applied after any restore.

7. **Privacy by design and by default (Art. 25).** New features and changes to A-01 are checked for data
   protection impact before release. Defaults collect the least data, for example the newsletter box is
   unticked and guest checkout is available.

8. **Processors and transfers.** Processors are bound by an Art. 28 contract (POL-06). Personal data stays
   in the EU/EEA, or is transferred only with an adequacy decision or standard contractual clauses (Chapter V GDPR).

9. **Security of processing (Art. 32).** Security measures follow POL-01, POL-02, POL-04, POL-07 and POL-08, and are chosen on the basis of the risk assessment (POL-09).

10. **Data protection impact assessment (Art. 35).** New or significantly changed processing is screened
    against the EDPB criteria (WP248 rev.01). A DPIA is carried out where high risk is likely, and the DPO's
    advice is always sought. The current DPIA for customer data processing is `02-risk/dpia.md`.

11. **Personal data breaches (Art. 33 and 34).** Breaches are handled under POL-05, including notification
    to the BlnBDI within 72 hours and communication to customers where the risk is high.

12. **Cookies and tracking.** Non-essential cookies and similar technologies are used only with prior consent (§ 25 TDDDG).

13. **Confidentiality and training.** Staff commit in writing to confidentiality before they get access to
    personal data. They receive data protection training at onboarding and every year after.

## Compliance

- The DPO audits compliance with this policy at least once a year and reports to the Managing Director.
- KPI-11 tracks the share of data subject requests answered within one month. KPI-09 tracks supplier contracts.
- Violations can lead to fines for ShopNova of up to EUR 20 million or 4% of worldwide annual turnover
  (Art. 83(5) GDPR), and are handled under the disciplinary process for staff.

## Review

The Managing Director, advised by the DPO, reviews this policy every year, and also when the processing
changes, after a personal data breach, or when the law or regulatory guidance changes.
