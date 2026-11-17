# References

Citation style: author–date. No style was specified, so this one is an assumption.

## Law and case law

- Regulation (EU) 2016/679 of the European Parliament and of the Council of 27 April 2016 (General Data Protection Regulation, GDPR). OJ L 119, 4.5.2016.
- Bundesdatenschutzgesetz (BDSG) of 30 June 2017, in particular § 38 (data protection officers of private bodies).
- Telekommunikation-Digitale-Dienste-Datenschutz-Gesetz (TDDDG), § 25 (consent for access to terminal equipment).
- Handelsgesetzbuch (HGB) § 257 and Abgabenordnung (AO) § 147, as amended by the Viertes Bürokratieentlastungsgesetz (BEG IV), retention of accounting vouchers 8 years, effective 1 January 2025.
- CJEU (2023). Judgment of 9 February 2023, *X-FAB Dresden*, C-453/21, ECLI:EU:C:2023:79.

## Guidelines and standards

- EDPB (2022). *Guidelines 01/2021 on examples regarding personal data breach notification*, version 2.0.
- EDPB (2023). *Guidelines 9/2022 on personal data breach notification under GDPR*, version 2.0.
- ENISA (2013). *Recommendations for a methodology of the assessment of severity of personal data breaches*.
- FIRST (2019). *Common Vulnerability Scoring System v3.1: Specification Document*.
- ISO/IEC (2022a). *ISO/IEC 27001:2022 Information security, cybersecurity and privacy protection: Information security management systems: Requirements*.
- ISO/IEC (2022b). *ISO/IEC 27005:2022 Information security, cybersecurity and privacy protection: Guidance on managing information security risks*.
- ISO/IEC (2023). *ISO/IEC 27035-1:2023 Information security incident management: Principles and process*.
- NIST (2024). *The NIST Cybersecurity Framework (CSF) 2.0*. NIST CSWP 29.
- NIST (2025). *Incident Response Recommendations and Considerations for Cybersecurity Risk Management* (SP 800-61 Rev. 3).
- OWASP (2021). *OWASP Top 10:2021*, A03 Injection.
- OWASP (2021b). *Application Security Verification Standard (ASVS)* 4.0.3.
- WP29 / EDPB (2017). *Guidelines on Data Protection Impact Assessment (DPIA) and determining whether processing is "likely to result in a high risk"*, WP248 rev.01.

## Tools used in the lab

- Aqua Security (2026). *Trivy*, vulnerability scanner, container image `aquasec/trivy:latest` (version recorded in `evidence/phase3/before/trivy-version.txt`).
- Greenbone (2026). *Greenbone Community Edition*, container deployment (`docker-compose.yml` from greenbone.github.io).
- Kimminich, B. (2026). *OWASP Juice Shop*, version 20.4.0-SNAPSHOT, container image `bkimminich/juice-shop`.
- Lyon, G. (2009). *Nmap Network Scanning*. Nmap Project. Container image `instrumentisto/nmap`.
- OWASP ModSecurity Core Rule Set (2026). Container image `owasp/modsecurity-crs:nginx`.
- ZAP (2026). *Zed Attack Proxy*, version 2.17.0, container image `zaproxy/zap-stable`.
