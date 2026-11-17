# INC-01 notification to the supervisory authority (Art. 33 GDPR)

**To:** Berliner Beauftragte für Datenschutz und Informationsfreiheit (BlnBDI), through the online breach notification form
**From:** ShopNova GmbH, Berlin (controller)
**Status:** simulated submission (lab exercise). Initial notification under Art. 33(4); further information will follow in phases.
**Awareness:** 2026-11-17, 17:39 UTC. **Deadline:** 2026-11-20, 17:39 UTC. Submitted well within 72 hours, so no reasons for delay are needed.

---

**1. Nature of the breach (Art. 33(3)(a))**

On 17 November 2026, between 17:37:37 and 17:37:41 UTC, an unauthorised person logged in to our web
shop with the stolen password of a shared customer-support account. That account had administrator
rights. Using them, the person downloaded the list of all customer accounts. This is a breach of
confidentiality. We have found no change or deletion of data.

- **Categories of data subjects:** registered customers of the web shop.
- **Approximate number of data subjects:** about 20,000.
- **Categories of personal data:** name or username, email address, account role, IP address of the last login, account creation and change dates.
- **Not affected:** passwords (the system does not return them), two-factor secrets, delivery addresses, payment data (we hold only tokenised references; card data is processed by our payment provider), and special categories of data.
- **Approximate number of records:** one record per customer account, about 20,000.

**2. Contact point (Art. 33(3)(b))**

Data Protection Officer of ShopNova GmbH (external DPO), [name], [email], [phone]. Contact details as
published in our privacy notice.

**3. Likely consequences (Art. 33(3)(c))**

The main risk is targeted phishing. Someone who knows that a person is a ShopNova customer, and knows their
email address, can send convincing fake emails in our name, for example fake order or payment messages. Spam
is also likely. IP addresses could allow a rough location estimate. Because no passwords or payment data were
taken, we do not expect direct financial loss or account takeover from this data alone.

**4. Measures taken and proposed (Art. 33(3)(d))**

Taken:
- Within one minute of the detection alerts, the password of the support account was reset and the
  affected administrative functions were blocked at the shop's entry point. We verified that the stolen
  password and the existing access token no longer work.
- Logs and evidence have been preserved.
- Customers are being informed by email and on the shop website, with a warning about phishing and
  advice on how to recognise genuine messages from us.

Proposed:
- Removing administrator rights from the support role and replacing the shared support account with
  personal accounts (planned by 15 December 2026, brought forward after this incident).
- Multi-factor authentication for all staff accounts (planned by 15 December 2026).
- Revocation of access tokens on password change.
- Continued monitoring of logs for further misuse.

A post-incident review is under way, and we will send an update with its results.

**5. Cross-border processing**

The affected customers live mainly in Germany, with some in other EU member states. ShopNova has its only
establishment in Berlin. The BlnBDI is therefore the competent (lead) authority.

---

*Prepared by the incident lead (Information Security Officer), reviewed by the DPO. Submission approved by
the Managing Director. All simulated, 2026-11-17.*
