# POL-05 Incident Response and Breach Notification Policy

| Field | Value |
|---|---|
| Policy ID | POL-05 |
| Owner | Information Security Officer |
| Approved by | Managing Director |
| Version | 1.1 |
| Approved on | 2026-11-17 |
| Next review | 2027-11-16 |
| Classification | Internal |
| Applies to | A-01, A-02, A-03, A-04, A-05, A-06, A-07, A-08 |
| Framework references | ISO/IEC 27001:2022 A.5.5, A.5.24 to A.5.28, A.6.8, A.8.15, A.8.16; NIST CSF 2.0 DE.CM, DE.AE, RS.MA, RS.AN, RS.CO, RS.MI, RC.RP, RC.CO; GDPR Art. 4(12), 33, 34 (full list in `../framework-mapping.csv`) |

## Purpose

To detect, contain and recover from security incidents quickly, and to meet ShopNova's legal duties when
an incident is a personal data breach. In particular:

- notify the Berlin Commissioner for Data Protection and Freedom of Information (BlnBDI) within 72 hours (Art. 33 GDPR);
- inform affected customers when the risk to them is high (Art. 34 GDPR).

## Scope

- All security events and incidents that affect ShopNova's assets (A-01 to A-08), including incidents at suppliers that process ShopNova data.
- All personal data breaches (Art. 4(12) GDPR): any breach of security that leads to the accidental or unlawful destruction, loss, alteration, unauthorised disclosure of, or access to, personal data.

## Roles

| Role | Responsibility in an incident |
|---|---|
| Information Security Officer | Owns this policy. Incident lead: classifies, coordinates, documents, runs the post-incident review. |
| Head of IT | Technical lead: containment, eradication and recovery. |
| IT administrators | Collect evidence, isolate systems, restore services. |
| Data Protection Officer | Advises on whether a breach is notifiable and on the risk to data subjects. Contact point for the BlnBDI. |
| Managing Director | Decides on notification to the BlnBDI and to customers, and approves all external communication. |
| Head of Support | Handles customer questions, and sends customer notifications when the Managing Director decides to notify. |
| Finance Lead, Marketing Lead, Logistics Lead | Contact the payment provider, email provider and delivery partner. |
| All staff | Report suspected incidents at once and preserve evidence. |

The Information Security Officer, the Head of IT, the IT administrators and the Data Protection Officer
form the **Incident Response Team (IRT)**. Other roles join as needed.

## Policy statements

1. **Lifecycle.** Incidents are handled in four phases, following NIST SP 800-61 Rev. 3 and ISO/IEC 27035:
   - **Prepare:** plans, contacts, logging, exercises.
   - **Detect and analyse:** triage, classification, scoping.
   - **Contain, eradicate and recover.**
   - **Post-incident activity:** lessons learned, corrective actions.

2. **Reporting.**
   - Staff report suspected incidents within one hour of noticing them, to the security mailbox or hotline. Lost or stolen laptops count.
   - Suppliers must report incidents affecting ShopNova data within 24 hours (POL-06), so that ShopNova can meet the 72-hour deadline.

3. **Severity classification.**

   | Severity | Criteria (any one is enough) | Response |
   |---|---|---|
   | SEV-1 Critical | Confirmed breach of D-03 or D-04, or of more than 1,000 customers' data; web shop down for more than 4 hours; ransomware | IRT at once, Managing Director informed within 1 hour |
   | SEV-2 High | Confirmed breach of fewer than 1,000 customers' data; compromised staff or admin account | IRT within 4 hours, Managing Director informed the same day |
   | SEV-3 Medium | Suspected breach under investigation; malware contained on one laptop | IRT the next working day |
   | SEV-4 Low | Security event with no impact, for example a blocked phishing email | Logged, reviewed weekly |

4. **Awareness and the 72-hour clock.** ShopNova becomes "aware" of a breach when it is reasonably
   certain that a security incident has compromised personal data. The incident lead records that time.
   The 72-hour deadline of Art. 33(1) runs from it.

5. **Breach risk assessment.** Within 24 hours of awareness, the incident lead and the DPO assess the
   risk to data subjects, following EDPB Guidelines 9/2022. They consider:
   - the type and sensitivity of the data (D-03 and D-04 weigh more);
   - the number of people affected;
   - how easy it is to identify them;
   - the possible consequences (fraud, phishing, account takeover);
   - whether the data was encrypted.

   Result: **no risk**, **risk** or **high risk**.

6. **Notification to the BlnBDI (Art. 33).** Unless the breach is unlikely to result in a risk, the
   Managing Director notifies the BlnBDI within 72 hours of awareness, using its online form. The notice
   contains the information in Art. 33(3). Information can be given in phases (Art. 33(4)). A late
   notice must include the reasons for the delay.

7. **Communication to customers (Art. 34).** If the risk is high, affected customers are told without
   undue delay, in clear and plain language: what happened, the likely consequences, what ShopNova is
   doing, what they should do (for example change their password), and the DPO contact. This is not
   needed if one of the conditions in Art. 34(3) applies, for example the data was encrypted and the key
   was not compromised.

8. **Breach register (Art. 33(5)).** Every personal data breach gets an INC-xx ID and is documented,
   notified or not: facts, effects, actions taken, and the reasoning behind the notification decision.

9. **Evidence.** Evidence is preserved before systems are changed where possible: logs, disk images,
   screenshots, with a chain-of-custody record. Security logs are kept for at least 90 days.

10. **Containment authority.** The incident lead may isolate systems, disable accounts and block network
    traffic without prior approval when this limits harm. The decision is recorded. New in v1.1, from INC-01:
    - **Revoke, don't just reset (CA-24).** Containment of a compromised account always includes
      invalidating its issued sessions and tokens (POL-04 statement 10), not only a password reset.
    - **Block narrowly (CA-25).** An emergency block covers only the abused function (method and path).
      Customer-facing functions such as sign-up, login and checkout keep working. A broad block that
      affects customers is narrowed within 24 hours.
    - **Re-verify after changes.** Containment is verified again after any restart, redeployment or
      restore, by replaying the attack. Containment stored in application state can be lost; in INC-01 a
      restart undid the password reset.

11. **External contacts.**
    - **Payment provider (A-05):** informed at once if D-03 or the payment integration is affected.
    - **Police:** a report to the Berlin police cybercrime unit is considered for criminal attacks.
    - **Media:** contact is handled only by the Managing Director.

12. **Logging and detection.** Security logs from A-01, A-02 and A-04 are collected centrally, and alerts
    are reviewed every day (CA-15).

13. **Post-incident review.** SEV-1 and SEV-2 incidents get a review within 10 working days. The review
    leads to corrective actions (CA-xx). Affected risks are re-scored (`CA-xx re-scores R-xx`), and
    policies are updated where needed.

14. **Exercises.** The plan is tested at least once a year with a tabletop exercise or simulation. The
    first is the simulated breach INC-01 in Phase 4.

## Compliance

- KPI-05 tracks the time from awareness to the notification decision (target: at most 72 hours, every time).
- KPI-06 tracks the mean time to detect simulated and real incidents.
- The DPO reviews the breach register every year.

## Review

The Information Security Officer reviews this policy every year, after every SEV-1 or SEV-2 incident or
exercise, and when regulatory guidance on breach notification changes.

## Change history

| Version | Date | Change | Trigger |
|---|---|---|---|
| 1.0 | 2026-11-16 | First approved version | Phase 1 |
| 1.1 | 2026-11-17 | Statement 10 extended: revoke tokens during containment, keep emergency blocks narrow, re-verify containment after restarts | INC-01 post-incident review, CA-24 and CA-25 |
