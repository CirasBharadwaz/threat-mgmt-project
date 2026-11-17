# 3 Risk management

This chapter applies the method of POL-09 to ShopNova (`02-risk/`). It identifies the risks to customer
data, scores them, chooses treatments, and looks at the same risks from the customers' side in a data
protection impact assessment (DPIA).

## 3.1 Method

The method follows ISO/IEC 27001:2022 clauses 6.1.2 and 6.1.3 and the process of ISO/IEC 27005:2022:
establish the context, identify, analyse, evaluate, treat, then monitor and review.

- **Identification.** Risks were identified per asset and per data category. Each one is written as
  "threat exploits weakness in asset, leading to consequence".
- **Scoring.** Likelihood and impact use 5-point scales, and the score is likelihood × impact. Impact is
  set by the worst of five dimensions: harm to data subjects, financial loss, legal and regulatory
  consequences, operational disruption and reputation.

| Score | Level | Appetite |
|---|---|---|
| 1–4 | Low | within appetite; risk owner may accept |
| 5–9 | Medium | tolerable; accepted with Information Security Officer sign-off |
| 10–16 | High | outside appetite; treat within 90 days or Managing Director accepts in writing |
| 20–25 | Critical | outside appetite; treat at once; only a temporary exception of at most 60 days |

Every risk is scored twice: a **current** score with today's controls, and a **target** score once the
planned actions are done. The difference shows the value of the treatment plan.

## 3.2 Results

Sixteen risks were identified (R-01 to R-16). The heat map (`risk-heatmap.md`) is generated from the
register by a script, so the two cannot drift apart.

| Level | Current | Target |
|---|---|---|
| Critical | 2 | 0 |
| High | 8 | 0 |
| Medium | 5 | 9 |
| Low | 1 | 7 |

The two Critical risks share a pattern: one technical failure exposes the whole customer base of about
20,000 people.

- **R-01: support admin rights on the customer database are misused** (likelihood 4, impact 5). A single
  phished support account would give full control of all customer records. This is the deliberate weakness
  of the case. It is governed by POL-04 and accepted only temporarily, until 2026-12-15.
- **R-12: SQL injection in the web shop exposes the customer database** (likelihood 4, impact 5). It is
  the most common attack on web shops (OWASP, 2021), and ShopNova had no secure coding rules, no security
  testing and no web application firewall. It is numbered R-12 so that the example chain in the ID scheme
  ("POL-02 governs R-12") holds literally.

The High risks are:

- R-02: phishing;
- R-03: outdated components;
- R-04: compromise of an admin account;
- R-05: ransomware;
- R-06: cloud misconfiguration;
- R-07: credential stuffing;
- R-10: missing processor agreements;
- R-11: a breach that is not detected or notified within 72 hours.

R-11 is unusual: it does not cause a breach, but it turns any breach into a compliance failure.

The vulnerability scans in Chapter 4 later found a misconfiguration that none of the 16 risks covered:
exposed files, public access logs and a wildcard CORS header. It was added as R-17 (High), which brings
the register to 17 risks. This is the feedback loop between the layers working as intended.

## 3.3 Treatment

Fifteen risks are reduced. R-16 (loss of consent records at the email provider) is Low and was accepted by
its owner. The treatment plan (`risk-treatment-plan.csv`) has 18 actions (CA-01 to CA-18). Each one has an
owner, a due date, a status and the ISO/IEC 27001:2022 Annex A controls it implements. Several actions
treat more than one risk:

- **MFA (CA-02)** lowers the likelihood of R-01, R-02, R-04 and R-05.
- **Central logging (CA-15)** supports R-01, R-04 and R-11.

All ten High and Critical risks have a treatment plan (KPI-10 = 100%). The plan's target is that, once
every action is done, no risk stays above Medium (0 Critical, 0 High). This was the Phase 2 plan, not the
outcome. After testing, Chapter 6 shows 2 Critical risks (R-01 at 25, R-03 at 20) and 7 High risks still
open on 17 November 2026. Two actions are already running in this project:

- CA-05, vulnerability scanning, carried out in Chapter 4;
- CA-14 and CA-15, the incident response plan and log-based detection, exercised in Chapter 5.

CA-01, removing support staff's admin rights, is deliberately still "Planned". This keeps the weakness
open for the incident simulation.

## 3.4 Data protection impact assessment

Risk to ShopNova and risk to its customers are not the same thing. A DPIA (Art. 35 GDPR) therefore looks
at the same risks from the data subjects' point of view.

- **Screening.** The EDPB-endorsed criteria (WP29, 2017) were applied. Two criteria are met or arguably
  met: data of a highly personal nature (payment references and credentials enable fraud) and large-scale
  processing (about 20,000 people). Two criteria usually mean a DPIA is needed. The processing is not on
  the German authorities' mandatory list as far as known, so the DPIA is also justified by good practice
  and accountability.
- **Assessment.** The DPIA describes the processing (Art. 35(7)(a)) and checks necessity and
  proportionality (b). It groups the 16 risks into seven harms to data subjects (c), such as identity
  fraud after a mass disclosure, account takeover, and loss of control over one's own data. Two harms are
  currently **high**:
  - illegitimate access to data at scale (R-01, R-03, R-04, R-06, R-12);
  - customers not being told about a breach in time (R-11).

  The measures (d) are the same CA actions as in the treatment plan.
- **Conclusion.** The plan is that, once the measures are in place, every harm falls to Medium or lower.
  On 17 November 2026 that is not yet the case. The key measures against illegitimate access at scale
  (CA-01, CA-02, CA-21) are still open, so that harm remains high. Prior consultation with the BlnBDI
  (Art. 36) was judged unnecessary because the measures are scheduled. The DPIA is reopened if the key
  actions miss their deadline, which INC-01 brought forward from 2026-12-15 to 2026-11-24. The DPO's
  advice is recorded (Art. 35(2)).

## 3.5 Discussion

The method is simple on purpose. A 5 × 5 matrix is easy to explain to management and to repeat. Its known
weaknesses are that the scores are ordinal (a 20 is not "twice as bad" as a 10) and that the experts
judging the scores are not calibrated. Two things reduce these weaknesses:

- **Written definitions.** Every scale point has a written definition with concrete thresholds (number of
  customers affected, euros, outage hours), so scores can be challenged and repeated.
- **Testing.** Chapters 4 and 5 test two scores directly. R-12 is tested by attacking the lab shop, and
  R-01 and R-11 by the incident simulation. Chapter 6 then re-scores them with evidence instead of
  judgement.
