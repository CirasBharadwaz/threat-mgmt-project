# 8 Conclusion

This project set out to show that governance, risk management, vulnerability management and incident
response work better as one process than as four separate activities. The case of ShopNova GmbH supports
that claim, within the limits set out in Chapter 7.

- **Governance** set the rules that the later phases were measured against:
  - nine policies, each with owners;
  - a RACI matrix;
  - eleven KPIs;
  - a framework mapping with 110 references.

  POL-02 set the remediation deadlines used in Chapter 4, POL-05 the 72-hour clock used in Chapter 5, and
  POL-09 the scoring used throughout.
- **Risk management** found 16 risks on paper, including the two that the later phases tested directly:
  the support staff's admin rights (R-01) and SQL injection (R-12).
- **Vulnerability management** confirmed and fixed the SQL injection, and verified the fix with the same
  attack before and after. It compared a WAF with a code fix and chose the code fix for the root cause.
  It also found a risk (R-17) and a category of personal data (D-06) that the desk-based work had missed.
- **Incident response** turned the accepted risk R-01 into a realistic breach, INC-01:
  - detected it in 18 seconds and contained it in 50 seconds;
  - decided on notification with a documented, openly debatable Art. 34 judgement;
  - turned the lessons into new versions of two policies.

**The integration step is what makes the difference.** Without it, the incident would have been a
standalone report. With it:

- the risk register now holds evidence instead of judgement (R-01 up to 25, R-12 down to 10, R-03 up to
  20 because V-05 is still open);
- the policies changed because of what actually happened;
- every claim can be traced through 143 links in `traceability.csv`, from a policy to a risk, a
  vulnerability, an incident, a corrective action, and back to a re-scored risk or an updated policy.

**Current risk state (17 November 2026).** The register shows 2 Critical, 7 High, 6 Medium and 2 Low
risks. The Phase 2 treatment plan aimed at 0 Critical and 0 High. **That target has not been reached.**
The two Critical risks are worse than in Phase 2: R-01 went from 20 to 25, and R-03 from 16 to 20. The
plan describes where ShopNova wants to be; the register describes where it is.

**What remains open is stated plainly:**

- two Critical risks (R-01, R-03) under short exceptions until 2026-11-24;
- the library upgrades (CA-21);
- the removal of support admin rights and MFA (CA-01, CA-02);
- token revocation (CA-24);
- the KPIs the lab could not measure.

For a company at ShopNova's level of maturity, the next step is not more documents. It is doing those
four actions on time, and then running this loop again.
