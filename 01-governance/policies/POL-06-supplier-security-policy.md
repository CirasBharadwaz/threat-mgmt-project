# POL-06 Supplier Security Policy

| Field | Value |
|---|---|
| Policy ID | POL-06 |
| Owner | Information Security Officer |
| Approved by | Managing Director |
| Version | 1.0 |
| Approved on | 2026-11-16 |
| Next review | 2027-11-16 |
| Classification | Internal |
| Applies to | A-05, A-06, A-08 |
| Framework references | ISO/IEC 27001:2022 A.5.19 to A.5.23; NIST CSF 2.0 GV.SC; GDPR Art. 28, 44 to 46 (full list in `../framework-mapping.csv`) |

## Purpose

To make sure that suppliers who receive ShopNova's customer data protect it as well as ShopNova must, and
that each data-sharing relationship has the right legal basis and contract.

## Scope

- The payment provider (A-05), the email and newsletter provider (A-06) and the delivery partner (A-08).
- The cloud hosting provider that runs A-01, A-02 and A-03. It is a processor even though the asset register lists it only through those assets.
- Every new supplier that would receive personal data.

## Roles

| Role | Responsibility |
|---|---|
| Information Security Officer | Owns this policy. Runs supplier assessments and keeps the supplier list. |
| Data Protection Officer | Advises on each supplier's role (processor or controller) and on contract terms. |
| Contract owners (Finance Lead for A-05, Marketing Lead for A-06, Logistics Lead for A-08, Head of IT for hosting) | Make sure their supplier meets this policy, and sign contracts. |
| Managing Director | Signs data processing agreements and accepts remaining supplier risks. |

## Policy statements

1. **Role first.** Before data is shared, the DPO and the contract owner decide each supplier's GDPR role:

   | Supplier | Expected role | Consequence |
   |---|---|---|
   | A-06 email provider | Processor | Art. 28 data processing agreement required |
   | Cloud hosting provider | Processor | Art. 28 data processing agreement required |
   | A-05 payment provider | Usually an independent controller for payment processing, because of its own regulatory duties | Data sharing based on the contract with the customer, and named in the privacy notice |
   | A-08 delivery partner | Parcel carriers are usually independent controllers for the delivery itself | Data sharing based on the contract with the customer, and named in the privacy notice. Data processing agreement only if the partner acts on ShopNova's instructions |

   Each role decision is recorded with its reasoning (CA-13).

2. **Due diligence.** Before signing, the supplier answers a security questionnaire, or shows an ISO/IEC
   27001 certificate or a SOC 2 Type II report. Its data location and sub-processors are checked.

3. **Contract terms.** Data processing agreements contain everything required by Art. 28(3) GDPR. All
   supplier contracts that involve personal data also require:
   - notice of security incidents within 24 hours;
   - a right to audit, or access to audit reports;
   - approval of new sub-processors;
   - return or deletion of the data when the contract ends.

4. **Data minimisation.** Suppliers get only the data they need. The delivery partner gets name, address
   and, only where needed for delivery notices, phone number. It does not get email addresses unless it
   sends tracking messages under its own terms.

5. **Transfers.** Data stays in the EU/EEA, or is transferred only under Chapter V GDPR (adequacy decision
   or standard contractual clauses with a transfer assessment).

6. **Review.** Suppliers with access to Strictly confidential data (D-03, D-04) are reviewed every year,
   all others every two years, and every supplier after a security incident.

## Compliance

KPI-09 tracks the share of suppliers that hold personal data and have a role decision, a contract
and a current assessment (target: 100%). Supplier findings are recorded as risks under POL-09.

## Review

The Information Security Officer reviews this policy every year, and also when a supplier changes or after a supplier incident.
