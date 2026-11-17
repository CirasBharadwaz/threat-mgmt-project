# Executive summary

**Purpose.** This report shows how governance, risk management, vulnerability management and incident
response can work as one managed process for a small company that holds personal data of EU customers.
The case company is ShopNova GmbH, a fictional Berlin web shop with about 20,000 customers. All data is
synthetic, and the technical work ran in a local lab against OWASP Juice Shop.

**What was done.**

- **Governance.** Nine policies were written, with named owners, a RACI matrix and eleven KPIs. The
  policies are mapped to ISO/IEC 27001:2022, NIST CSF 2.0 and GDPR/BDSG. An external DPO is required
  under § 38 BDSG.
- **Risk management.** 16 risks were identified, with a treatment plan and a DPIA. A 17th risk (R-17)
  was later found by scanning.
- **Vulnerability management.** 6 vulnerabilities were recorded: 5 from the lab scans and 1 from the
  incident investigation. Four were fixed and verified, and the same SQL injection login bypass that
  worked before the fix failed after it.
- **Incident response.** A simulated breach, INC-01, used a phished support account with admin rights.
  It was detected in 18 seconds and contained in 50 seconds. It was notified to the authority, and
  customers were informed voluntarily.
- **Integration.** All evidence was fed back. Risks were re-scored, KPIs measured, and two policies
  updated to version 1.1.

**Current risk state (17 November 2026).**

| Level | Phase 2 assessment | Now (re-scored with evidence) | Plan target |
|---|---|---|---|
| Critical | 2 | 2 | 0 |
| High | 9 | 7 | 0 |
| Medium | 5 | 6 | 9 |
| Low | 1 | 2 | 8 |

**The plan target of 0 Critical and 0 High has not been reached.** Two Critical risks are open, and both
are worse than in Phase 2:

- **R-01, support staff with admin rights: 25.** It materialised as INC-01. Its root fixes, CA-01
  (remove the admin rights) and CA-02 (MFA), are due 2026-11-24.
- **R-03, vulnerable libraries: 20.** V-05 (116 known CVEs, 7 Critical) stays open until the library
  upgrade CA-21, also due 2026-11-24. It is deliberately not scored as fixed.

Both risks run under temporary exceptions by the Managing Director until 2026-11-24. One risk improved
markedly: R-12 (SQL injection) went from 20 to 10 after the verified fix.

**Key judgements.**

- The breach was notified under Art. 33 GDPR. It was rated "not high risk" under Art. 34, because no
  passwords or payment data were exposed. Another assessor could reasonably decide differently, which is
  why customers were informed anyway.
- Lab times are compressed, and management decisions were simulated. The KPI values show that the
  process works, not how fast ShopNova really is.

**Limitations.** These include synthetic data, a lab-only test, simulated sign-offs and no usable
Greenbone result. Two legal points are also unverified: whether the payment and delivery providers act
as processors or as independent controllers, and whether NIS2 applies. Chapter 7 covers them in full.
