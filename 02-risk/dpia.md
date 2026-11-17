# Data protection impact assessment (DPIA): customer data processing in the web shop

ShopNova GmbH, version 1.0, 2026-11-16. Prepared by: Information Security Officer. Advice: Data
Protection Officer. Decision: Managing Director. Method: Art. 35 GDPR, EDPB/WP29 Guidelines WP248 rev.01.
The risk IDs (R-xx) and actions (CA-xx) are the same as in `risk-register.csv` and `risk-treatment-plan.csv`.

## 1. Screening: is a DPIA required?

WP248 rev.01 lists nine criteria. Processing that meets two or more of them is likely to need a DPIA.

| # | WP248 criterion | Met? | Reason |
|---|---|---|---|
| 1 | Evaluation or scoring, including profiling | No | No profiling or scoring of customers; the newsletter is not personalised by behaviour |
| 2 | Automated decisions with legal or similar effect | No | No automated decisions about customers |
| 3 | Systematic monitoring | No | No tracking of customers beyond the shop session (non-essential cookies need consent, POL-03) |
| 4 | Sensitive data or data of a highly personal nature | **Partly** | No special categories (Art. 9), but payment references (D-03) and credentials (D-04) are data whose breach enables fraud and account takeover, which WP248 treats as highly personal |
| 5 | Data processed on a large scale | **Yes** | About 20,000 data subjects, kept for up to 8 years, in a database open to the internet through the shop |
| 6 | Matching or combining datasets | No | No combining with other sources |
| 7 | Vulnerable data subjects | No | Adult consumers |
| 8 | Innovative technology | No | Standard web shop technology |
| 9 | Prevents data subjects from using a service or contract | No | Not applicable |

**Result:** Two criteria are met, or arguably met (4 and 5). Customer data processing in a web shop is
not on the German supervisory authorities' mandatory DPIA list as far as known. ShopNova carries out
the DPIA because of the WP248 two-criteria rule and as good practice under its accountability duty
(Art. 5(2) and 24 GDPR). The DPO agrees with this decision (see section 7).

## 2. Description of the processing (Art. 35(7)(a))

| Element | Description |
|---|---|
| Controller | ShopNova GmbH, Berlin. External DPO designated (see `../01-governance/governance-structure.md`) |
| Purposes | Customer accounts, order fulfilment, shipping, payment, customer support, newsletter (with consent) |
| Data subjects | About 20,000 registered customers in the EU |
| Data categories | D-01 identity (name, email, phone), D-02 delivery address, D-03 payment reference (tokenised), D-04 account credentials (email, password hash), D-05 newsletter consent |
| Systems | A-01 web shop, A-02 customer database, A-03 nightly backups, A-04 staff laptops (support access to A-02) |
| Recipients | A-05 payment provider (D-03), A-08 delivery partner (D-01, D-02), A-06 email provider (D-05), cloud hosting provider (processor) |
| Retention | D-01 and D-02: 6 years after last order. D-03: 8 years (§ 257 HGB, § 147 AO as amended by BEG IV). D-04: until account deletion. D-05: until consent is withdrawn |
| Data flow | `../00-scope-and-setup/data-flow.mmd` |
| Access | Support (with admin rights on A-02, see R-01), IT administrators (A-07), Finance, Marketing, Logistics |

## 3. Necessity and proportionality (Art. 35(7)(b))

| Check | Assessment |
|---|---|
| Legal basis | Contract (Art. 6(1)(b)) for accounts, orders, shipping and payment; legal obligation (Art. 6(1)(c)) for accounting retention; consent (Art. 6(1)(a)) for the newsletter |
| Purpose limitation | Purposes fixed in the data inventory; no secondary use |
| Data minimisation | Card data never reaches ShopNova (tokenised by A-05). **Gap:** the delivery partner also gets email addresses (R-09, fixed by CA-13). **Gap:** support has more rights than needed (R-01, fixed by CA-01) |
| Storage limitation | Periods defined. **Gap:** no deletion routine (R-14, fixed by CA-17) |
| Accuracy | Customers can correct their own account data |
| Transparency | Privacy notice exists. To verify against the inventory (gap 6 in the gap assessment) |
| Data subject rights | **Gap:** no procedure or log (R-15, fixed by CA-18) |
| Processors and transfers | **Gap:** missing Art. 28 agreements; supplier roles not assessed (R-10, fixed by CA-13) |

The processing itself is necessary for running the shop and proportionate in scope. The gaps are about
how it is done, not whether it should be done. Each gap has a risk and an action.

## 4. Risks to the rights and freedoms of data subjects (Art. 35(7)(c))

This section looks at harm to **customers**, not to ShopNova. Severity and likelihood use the four-level
scale common in DPIA practice: negligible, limited, significant, maximum.

| Data subject risk | Linked risks | Possible harm to customers | Likelihood (current) | Severity | Risk to data subjects (current) |
|---|---|---|---|---|---|
| Illegitimate access to customer data at scale | R-01, R-03, R-04, R-06, R-12 | Identity fraud, targeted phishing in ShopNova's name, password reuse attacks on other services | Significant | Significant | **High** |
| Account takeover of individual customers | R-02, R-07 | Fraudulent orders, exposure of address and order history | Significant | Limited | Medium |
| Theft of payment and identity data at checkout | R-13 | Card fraud, financial loss | Limited | Significant | Medium |
| Disclosure through laptops, suppliers or misconfiguration | R-08, R-09, R-17 | Exposure of names and addresses; unwanted contact; IP addresses in public access logs (R-17, added in Phase 3) | Limited | Limited | Medium |
| Loss of availability or integrity of customer data | R-05 | Orders lost or delayed, account data lost | Limited | Limited | Medium |
| Customers not told about a breach in time | R-11 | No chance to protect themselves (change passwords, watch for fraud) | Significant | Significant | **High** |
| Loss of control over own data | R-10, R-14, R-15, R-16 | Data kept too long, shared without proper safeguards, rights not honoured, consent not provable | Significant | Limited | Medium |

## 5. Measures to address the risks (Art. 35(7)(d))

| Data subject risk | Measures (CA-xx) | Effect |
|---|---|---|
| Illegitimate access at scale | CA-01 role-based support access, CA-02 MFA, CA-05 scanning, CA-06 injection fixes, CA-07 WAF, CA-08 admin accounts, CA-10 cloud baseline, CA-15 logging | Removes the main entry routes; limits what one compromised account can reach |
| Account takeover | CA-02, CA-04 training, CA-11 login protection, CA-12 laptop security | Makes stolen passwords far less useful |
| Theft at checkout | CA-16 CSP, SRI, script monitoring | Blocks or detects injected scripts |
| Disclosure through laptops, suppliers or misconfiguration | CA-12 disk encryption, CA-13 supplier contracts and minimisation, CA-19 and CA-20 shop hardening | Encrypted laptops fall under Art. 34(3)(a); suppliers get less data; logs and files no longer public |
| Loss of availability or integrity | CA-09 immutable backups and restore tests | Recovery within the 8-hour target |
| Late breach notification | CA-14 incident response plan and breach procedure, CA-15 SIEM | Detection within 24 hours (KPI-06); decision within 72 hours (KPI-05) |
| Loss of control | CA-13, CA-17 deletion, CA-18 request procedure | Storage limitation and rights handled on time |

## 6. Residual risk and conclusion

With all measures in place, every data subject risk falls to **Medium or lower**. This matches the
target column of the risk register, where no risk stays High or Critical.

Until the measures are done, two data subject risks stay **High**: illegitimate access at scale, and late
notification. The key actions are CA-01, CA-02, CA-06 and CA-07 (due 2026-12-15) and CA-14 and CA-15
(in progress in Phase 4).

**Conclusion:**

1. Processing continues. The listed measures are mandatory and carry the due dates in the treatment plan.
2. Prior consultation with the BlnBDI (Art. 36) is **not** required now, because measures that reduce the
   residual risk have been identified and scheduled.
3. If CA-01, CA-02, CA-06 or CA-07 is not done by 2026-12-15, the DPIA is reopened and the DPO advises
   whether prior consultation becomes necessary.

## 7. DPO advice (Art. 35(2))

The DPO was consulted on 2026-11-16 (simulated) and advises:

- (a) A DPIA is appropriate.
- (b) Support staff's admin rights (R-01) are the most serious gap and should be removed before any other optional project.
- (c) Supplier roles must be decided before the next contract renewal.
- (d) The views of data subjects (Art. 35(9)) are not sought, because the processing is a standard web shop and the effort would be disproportionate. This reasoning is recorded here.

## 8. Sign-off and review

| Role | Decision | Date |
|---|---|---|
| Managing Director | Accepts the conclusion in section 6 and the measures in the treatment plan | 2026-11-16 (simulated) |
| Data Protection Officer | Advice given as in section 7 | 2026-11-16 (simulated) |

Next review: 2026-12-15, when the key actions are due, or earlier after any incident involving customer data (for example INC-01 in Phase 4).
