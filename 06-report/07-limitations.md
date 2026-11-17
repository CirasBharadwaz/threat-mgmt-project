# 7 Limitations

The results of this project must be read with the following limits in mind.

**Synthetic case and data.** ShopNova GmbH, its staff numbers, customers, risk scores and financial bands
are fictional. All personal data in the repository is synthetic: the 24 lab accounts are Juice Shop's
built-in test users, and the scale of about 20,000 customers is a scenario assumption.

**Lab only.** The vulnerability and incident work ran against OWASP Juice Shop, a deliberately vulnerable
training application, in a local Docker lab. It did not run against a real shop. The findings show how the
process works, not what ShopNova's real exposure is. Specific limits:

- **Scan coverage:** the ZAP active scan covered only the login request.
- **Dependencies:** Trivy reports known CVEs in libraries without checking whether each one can be reached.
- **Fixes:** the fixes were made in containers, without change management or code review.

**Compressed time.** The incident timeline is a compressed lab simulation. The attack, detection,
containment and decisions took about three minutes. KPI-01, KPI-05 and KPI-06 are therefore lab values,
not estimates of production performance.

**Simulated sign-offs and DPO advice.** Management approvals, the DPO's advice, the notification to the
BlnBDI and the customer notice are simulated and marked "(simulated)" in the documents. Nothing was sent
to any authority or person.

**Greenbone.** The network vulnerability scanner Greenbone Community Edition was installed as containers,
attached to the lab network, and its admin password was changed. Its first feed synchronisation takes
hours.

- At 18:31 and 18:44 local time, the vulnerability tests were not yet loaded, and three feeds were still
  syncing.
- Docker Desktop stopped between the two sessions of the project and was restarted at 18:04 UTC
  (19:04 local), which restarted the feed loading.
- **Status at the agreed cutoff of 20:30 local time: no usable Greenbone result.** After the restart, the scanner failed to load its tests, so run 1 (18:22 UTC) finished empty. After one scanner restart, run 3 (18:29–18:30 UTC) reached the host by ICMP, but did not detect or test the web service on port 3000. No further runs were made before the cutoff.

The vulnerability findings in Chapter 4 therefore rest on Nmap, Trivy, ZAP and manual checks. Greenbone's
network-level checks are missing, which mainly affects findings on the operating system and services.

**Two legal points are not verified.** They should be confirmed with the lecturer or a lawyer:

1. **Processor or independent controller.** POL-06 assumes that the payment provider (A-05) and the
   delivery partner (A-08) act as independent controllers, not as processors on ShopNova's behalf. This
   is the usual view for payment service providers and parcel carriers, but it depends on the actual
   contracts. If either one is a processor, an Art. 28 agreement is required.
2. **NIS2.** The project assumes that NIS2, as implemented in the German BSIG, does not apply, because
   ShopNova sells its own goods and is not an online marketplace, search engine or cloud provider.

**No assignment brief.** The requirements checklist, the choice of frameworks (ISO/IEC 27001:2022, NIST
CSF 2.0, GDPR/BDSG) and the citation style are assumptions, recorded in the decision log.

**Times.** All times in this report and the evidence are UTC. Berlin local time in November is UTC+1, so
for example the attack at 17:37 UTC took place at 18:37 in Berlin.
