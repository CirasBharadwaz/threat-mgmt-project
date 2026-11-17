# Decision log

Record every decision that changes scope, method or content. Examiners value a visible reasoning trail.

| Date | Decision | Reason |
|---|---|---|
| 2026-11-15 | Fictional case company (ShopNova GmbH) | Safe lab, publishable portfolio, full control of synthetic data |
| 2026-11-15 | Work phase by phase, validate at the end of each phase | Keeps scope under control and catches errors early |
| 2026-11-15 | A-05 Payment provider now lists D-03 in `data_held` | The provider stores the tokenised payment references, and D-03 already listed A-05 as storage; the two registers must agree |
| 2026-11-15 | Defer installing nmap (Phase 3) and pandoc (Phase 6) | Not needed until those phases; installation requires an administrator PowerShell |
| 2026-11-16 | Assumption: reference frameworks are ISO/IEC 27001:2022, NIST CSF 2.0 and GDPR/BDSG | No assignment brief is available; to be confirmed with the lecturer |
| 2026-11-16 | Item 1: A-01 added to `storage` for D-01 to D-04; `validate_phase0.py` now checks asset and data links in both directions | A-01 processes this data, and a breach of A-01 (Phase 4) must show which data was exposed. The old check only ran one way and missed the mismatch |
| 2026-11-16 | Item 2: D-03 retention set to "8 years (accounting vouchers, § 257 HGB, § 147 AO, as amended by BEG IV, effective 1 Jan 2025)" | BEG IV cut the retention period for accounting vouchers from 10 to 8 years; verified against the IHK Konstanz page |
| 2026-11-16 | Item 3: A-04 widened to "Staff laptops (about 40)"; owner changed from Head of Support to Head of IT | The scope statement counts 40 laptops but the register only covered support laptops. The asset now covers all staff laptops, which IT manages; support stays a user group |
| 2026-11-16 | Item 4: support staff keep admin rights on A-02 as a deliberate weak spot; diagram flow relabelled "support (admin) access" | Realistic for a company at basic maturity. POL-04 records it as a known gap, Phase 2 tracks it as R-01 (Critical), and CA-01 is planned but not done before the Phase 4 incident |
| 2026-11-16 | Item 5: README commands switched to `py` and PowerShell; Git Bash called by full path | On Windows `python3` opens the Microsoft Store, and in PowerShell `bash` starts WSL instead of Git Bash |
| 2026-11-16 | Requirements checklist filled in with the known deadline; all other fields "not specified (no brief)" | Only the deadline (2026-11-17) is known; open points listed as questions for the lecturer |
| 2026-11-16 | Schedule compressed to 2026-11-16 and 2026-11-17, with no buffer | 2026-11-17 is the final deadline and the full scope (Phases 1 to 6) is kept |
| 2026-11-16 | Phases 1 and 2 built in one pass without an approval stop in between | Instruction: stop only before installing software, starting containers, scanning, committing or pushing |
| 2026-11-16 | Policy numbering: POL-02 is the Vulnerability and Patch Management Policy and R-12 is the SQL injection risk | Makes the example chain in `id-scheme.md` (POL-02 governs R-12) hold literally in this project |
| 2026-11-16 | New relations `applies-to` (POL to A) and `treated-by` (R to CA); CA- IDs shared by risk treatment and incident corrective actions | Policies need asset links before risks exist; a separate treatment-action prefix would break the chain INC resolved-by CA re-scores R. The `source` column tells the two kinds apart |
| 2026-11-16 | Information Security Officer placed outside IT, reporting to the Managing Director; external DPO | Separates doing from checking (ISO/IEC 27001 A.5.3). A DPO is required (§ 38 BDSG, 26 people process data daily), and an internal one would face a conflict of interest |
| 2026-11-16 | Risk method: 5 x 5 likelihood and impact, bands Low 1-4, Medium 5-9, High 10-16, Critical 20-25; current and target scores | Simple, common method that examiners recognise (ISO/IEC 27005); target scores show the value of the treatment plan |
| 2026-11-16 | DPIA carried out for customer data processing | Two WP248 criteria met or arguably met (highly personal data, large scale); also good practice under Art. 5(2) and 24 GDPR |
| 2026-11-16 | Policy sizing: POL-01, 02, 03, 05, 09 full; POL-04, 06 concise; POL-07, 08 one page | Instruction; the Phase 1 validator warns if a policy falls outside its size range |
| 2026-11-17 | Lab tools run as throwaway Docker containers (Nmap, Trivy, ZAP, ModSecurity CRS, Greenbone CE); nothing installed on Windows | Approved by the user; no admin rights needed; containers removed after use |
| 2026-11-17 | Lab isolation: internal Docker network `tm-lab` (no internet, no host); the shop is published only on 127.0.0.1:3000; every scan targets only the lab shop | Scope rule from the user; checked by the isolation probe and by `validate_phase3.py` on the run logs |
| 2026-11-17 | ZAP: a baseline scan plus a targeted active scan of the login request only | A baseline scan is passive and cannot find SQL injection; scanning one request keeps the active scan short and in scope |
| 2026-11-17 | V-01 fixed by the patched login route (bound parameters, CA-06); the ModSecurity WAF (CA-07) kept as a tested compensating layer | Both blocked both injection variants; only the code fix removes the flaw, while WAF rules can be bypassed (`03-vulnerability/fix-options.md`) |
| 2026-11-17 | Data inventory: new category D-06 "Server access logs" (IP addresses), stored on A-01 | Phase 3 found the access logs publicly readable (V-04); logs are personal data that Phase 0 had missed. Changes a Phase 0 file |
| 2026-11-17 | New risk R-17 (web shop misconfiguration) and actions CA-19 to CA-21 (source "Vulnerability management") | Scan findings that no Phase 2 risk covered; shows the feedback loop from vulnerability management to risk management |
| 2026-11-17 | Business priority = CVSS severity, raised by at most one level for context (POL-02 statement 3); deadlines from POL-02 statement 4 | Makes the CVSS-to-business link explicit and checkable by the validator |
| 2026-11-17 | Phase 4 detection uses the proxy and application logs, not Wazuh | User decision (time and RAM); CA-15 stays "In progress" |
| 2026-11-17 | INC-01 scenario: phished shared support account with admin rights (R-01), not SQL injection | Matches the Phase 2 plan; V-01 was already fixed, so an attacker needs a real password |
| 2026-11-17 | INC-01: notify the BlnBDI (Art. 33); inform customers voluntarily (not high risk under Art. 34) | Breach assessment: malicious actor and large volume, but no passwords, payment or sensitive data |
| 2026-11-17 | CA-01 and CA-02 brought forward to 2026-11-24; V-06 (P1, 3-day deadline) needs a POL-02 exception until then | Post-incident review: the temporary exception for R-01 materialised as INC-01 |
| 2026-11-17 | Greenbone: scan only if the feed is ready by 20:30 local time; otherwise record the limitation | User instruction; the first feed sync takes hours |
| 2026-11-17 | Phase 5 re-scoring kept in separate `rescored_*` columns; the Phase 2 scores stay as the "before" state | Shows the effect of the evidence; the heat map now has before, after and target grids |
| 2026-11-17 | R-03 re-scored up to 20 (Critical), not down: V-05 (116 CVEs, 7 Critical) is open until CA-21 (2026-11-24) | Honesty rule: a risk with an open vulnerability is not scored as fixed; checked by `validate_phase5.py` |
| 2026-11-17 | R-01 re-scored up to 25: the risk materialised (INC-01) and its root causes remain | Evidence beats judgement; exception shortened to 2026-11-24 |
| 2026-11-17 | KPI values labelled "measured in the lab", "simulated", "derived from the register" or "not measured" | Lab values are compressed and must not be read as production performance |
| 2026-11-17 | POL-04 v1.1 (token invalidation on a password reset; false compensating control corrected) and POL-05 v1.1 (revoke tokens, narrow blocks, re-verify after restarts) | INC-01 post-incident review; traceable as INC-01 resolved-by CA-24/CA-25 updates POL-04/POL-05 |
| 2026-11-17 | CA-25 implemented in the lab (block narrowed to non-POST); CA-23 reset re-applied after the Docker restart undid it | The CA-25 test found the lost reset; tested evidence in `evidence/phase5/` |
| 2026-11-17 | Art. 34: "not high risk" kept, with the full EDPB 9/2022 reasoning and the note that another assessor could decide differently | Transparency about a judgement call; customers receive the same notice either way |
| 2026-11-17 | Report built without pandoc: own Markdown-to-HTML step, PDF printed by Microsoft Edge (headless), DOCX saved by Microsoft Word | pandoc is not installed and nothing may be installed; Edge and Word are already on the machine |
