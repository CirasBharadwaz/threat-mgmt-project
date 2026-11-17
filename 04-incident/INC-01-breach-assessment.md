# INC-01 breach risk assessment (POL-05 statement 5)

Prepared by: incident lead (Information Security Officer role), with the DPO (simulated). Method: EDPB
Guidelines 9/2022 on personal data breach notification, with the ENISA (2013) severity method as a
structured cross-check. Awareness: 2026-11-17 17:39:18 UTC (`evidence/phase4/response/exercise-log.txt`).

## 1. What happened

On 2026-11-17, between 17:37:37 and 17:37:41 UTC, a client logged in to the shop with the password of
the shared support account `support@juice-sh.op`. In the scenario, the password had been phished. The
account holds **admin rights** (R-01, the known gap in POL-04). Within four seconds the client downloaded
the full user list (`GET /api/Users`), the authentication details of all accounts
(`GET /rest/user/authentication-details/`), and each account one by one (24 requests). The log-based
detection raised three High alerts 18 seconds after the first request. The account was contained
45 seconds later.

This is a **confidentiality breach** (unauthorised access to and disclosure of personal data), not an
integrity or availability breach. No write requests were made (`attack-log.json` contains GET requests
and the login only).

## 2. Data and people affected

| Item | Lab evidence (`exfiltration-summary.json`) | ShopNova scenario |
|---|---|---|
| Accounts | 24 (all accounts in the lab shop) | all registered customer accounts, about 20,000 |
| Data categories | email, username, role, last login IP address, account timestamps, profile image path | D-01 customer identity (name and email) and D-06 IP addresses |
| Password hashes (D-04) | **not exposed**: the application masks the field with asterisks | not exposed |
| Two-factor secrets | not exposed (masked or empty) | not exposed |
| Delivery addresses (D-02), payment references (D-03) | not requested, not exposed | not exposed |
| Special categories (Art. 9) | none | none |

The lab holds 24 synthetic accounts. The assessment uses the ShopNova scale (about 20,000 customers),
because the same requests would return every customer account.

## 3. Risk to data subjects

| Factor (EDPB 9/2022) | Assessment |
|---|---|
| Type and sensitivity of data | Contact data and IP addresses; no financial data, no passwords, no special categories |
| Ease of identification | High: email addresses identify people directly |
| Severity of consequences | Targeted phishing that uses the ShopNova name and the fact that the person is a customer; spam; possible location inference from IP addresses. No direct financial loss, because no payment or password data was taken |
| Number of people | Large: about 20,000 |
| Special characteristics | No vulnerable groups; adult consumers |
| Malicious intent | Yes: deliberate phishing and data download (not an accidental disclosure) |
| Mitigating factors | Passwords and 2FA secrets masked; access contained within 1 minute; no evidence of further use yet |

**ENISA (2013) severity cross-check.** Severity = data processing context × ease of identification +
circumstances of the breach.

| Element | Value | Reason |
|---|---|---|
| Data processing context (DPC) | 1 | simple contact data |
| Ease of identification (EI) | 1 | full: email addresses identify people |
| Circumstances (CB) | +0.5 | loss of confidentiality to a known malicious party |
| **Severity** | **1.5, "Low"** | ENISA bands: below 2 Low, 2 to 3 Medium, 3 to 4 High, 4 and above Very high |

The volume of about 20,000 people is not part of the ENISA formula, so it is weighed separately below.

## 4. Conclusion

| Question | Decision | Reason |
|---|---|---|
| Is it a personal data breach (Art. 4(12))? | **Yes** | Unauthorised access to personal data of all customers |
| Notify the BlnBDI (Art. 33)? | **Yes, within 72 hours** | A risk to data subjects cannot be ruled out: malicious actor, large volume, data usable for phishing |
| Is it a high risk to data subjects (Art. 34)? | **No, not high risk** | No passwords, payment data or sensitive data. The main harm is phishing, which customers can guard against. ENISA severity Low |
| Inform customers anyway? | **Yes, voluntarily** | The phishing risk is real and customers can only protect themselves if they know. The notice follows the content of Art. 34(2). The Managing Director decided this, with the DPO's advice |
| Severity under POL-05 | **SEV-1** | Confirmed breach of more than 1,000 customers' data |
| Record in the breach register (Art. 33(5)) | **Yes** | `breach-register.csv`, INC-01 |

The assessment is reopened if:
- evidence shows the data being misused, for example a phishing wave;
- the password field turns out to be exposed elsewhere.

In either case, Art. 34 communication then becomes mandatory.

## 5. Art. 34 reasoning: why "not high risk", and its limits

Art. 34(1) GDPR requires telling data subjects when a breach is "likely to result in a **high** risk to
their rights and freedoms". EDPB Guidelines 9/2022 (section on assessing risk) list the factors that
decide this. Applied to INC-01:

| Factor (EDPB 9/2022) | INC-01 facts | Effect on the risk |
|---|---|---|
| Type of data | Name or username, email address, account role, last login IP address, account dates (D-01, D-06). No special categories, no financial data, no ID documents | Lowers it: contact data mainly enables phishing and spam, not direct fraud |
| Secrets | Password field and two-factor secrets were **masked by the application** (asterisks only, `exfiltration-summary.json`); payment data is never stored (tokenised by A-05) | Lowers it strongly: no account takeover or card fraud from this data alone |
| Number of people | 24 lab accounts; **about 20,000** customers in the ShopNova scenario, the whole customer base | Raises it: more people means more phishing victims, even at a low rate per person |
| Ease of identification | High: email addresses identify people directly, and the data links each person to ShopNova | Raises it: makes targeted phishing in ShopNova's name credible |
| Severity of consequences | Phishing, spam, possible rough location from IP addresses; no immediate financial loss | Limited and avoidable with care |
| Malicious intent | Yes: phished credentials, deliberate download | Raises it: the data is likely to be used |
| Mitigation | Contained within a minute; data subjects can protect themselves by ignoring suspicious messages | Lowers it |

**ShopNova's conclusion:** a risk, but **not a high risk**. Notification to the BlnBDI under Art. 33 is
required; communication to customers under Art. 34 is not. ShopNova informs customers anyway, with the
content Art. 34(2) prescribes, because the main harm (phishing) can only be avoided by customers who
know about it.

**Another assessor could decide differently.** A reasonable assessor could weigh the scale (about 20,000
people), the malicious intent and the credibility of targeted phishing more heavily, rate the risk as
high, and make Art. 34 communication mandatory. Because ShopNova sends the same notice voluntarily,
customers receive the same information under either view. The difference is legal, not practical: under
the stricter view, a later failure to notify customers would be a breach of Art. 34. The DPO's advice
and the Managing Director's decision are recorded in the timeline and the breach register.

## 6. References

- EDPB (2023). *Guidelines 9/2022 on personal data breach notification under GDPR*, version 2.0.
- EDPB (2022). *Guidelines 01/2021 on examples regarding personal data breach notification*.
- ENISA (2013). *Recommendations for a methodology of the assessment of severity of personal data breaches*.
