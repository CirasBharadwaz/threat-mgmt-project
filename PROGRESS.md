# Progress tracker

Tick items when done. Phase exit lists are also checked by the validation scripts in `tools/`.

## Phase 0: Scope and setup
- [x] Requirements checklist filled in (`00-scope-and-setup/requirements-checklist.md`; no brief, open points listed for the lecturer)
- [x] Case and scope confirmed (`scope-statement.md`)
- [x] Asset register reviewed (`asset-register.csv`; A-04 widened to all staff laptops)
- [x] Personal data inventory reviewed (`data-inventory.csv`; A-01 added to storage, D-03 retention 8 years)
- [ ] Data flow diagram renders on mermaid.live (`data-flow.mmd`; label changed, re-check)
- [x] ID scheme read and understood (`id-scheme.md`; relations `applies-to` and `treated-by` added)
- [x] Schedule dates filled in (`schedule.md`; 2026-11-16 to 2026-11-17)
- [x] Tool check run, gaps known (nmap and pandoc missing, deferred to Phase 3 / 6)
- [x] `py tools\validate_phase0.py` shows no `[FAIL]` and no `[TODO]`
- [x] First git commit made (pushed to https://github.com/CirasBharadwaz/threat-mgmt-project)

## Phase 1: Governance
- [x] Governance structure, roles and DPO assessment (`01-governance/governance-structure.md`)
- [x] RACI matrix (`raci-matrix.csv`)
- [x] Policy register and nine policies POL-01 to POL-09 (`policy-register.csv`, `policies/`)
- [x] Framework mapping to ISO/IEC 27001:2022, NIST CSF 2.0 and GDPR/BDSG (`framework-mapping.csv`)
- [x] KPI register KPI-01 to KPI-11 (`kpi-register.csv`)
- [x] GDPR and security baseline gap assessment (`gdpr-baseline-gap-assessment.md`)
- [x] `POL applies-to A` links in `traceability.csv`
- [x] `py tools\validate_phase1.py` shows no `[FAIL]`
- [ ] Frameworks confirmed with the lecturer (assumption in decision log)

## Phase 2: Risk management
- [x] Risk register R-01 to R-16 (`02-risk/risk-register.csv`)
- [x] Treatment plan CA-01 to CA-18 (`risk-treatment-plan.csv`)
- [x] Heat map generated (`risk-heatmap.md`)
- [x] DPIA (`dpia.md`)
- [x] Risk assessment summary (`risk-assessment-summary.md`)
- [x] `POL governs R` and `R treated-by CA` links in `traceability.csv`
- [x] `py tools\validate_phase2.py` shows no `[FAIL]`

## Phase 3: Vulnerability management
- [x] Lab: Juice Shop on 127.0.0.1 and internal network tm-lab; isolation verified (`03-vulnerability/lab/`)
- [x] Evidence before the fix: Nmap, Trivy, ZAP baseline, ZAP active, live SQL injection (`evidence/phase3/before/`)
- [x] Vulnerability register V-01 to V-06 with CVSS and business priority (`03-vulnerability/vulnerability-register.csv`)
- [x] Fix options for R-12 tested; 4 findings fixed (`fix-options.md`)
- [x] Rescan after the fix; same attack fails (`evidence/phase3/after/`)
- [x] Feedback: R-17, D-06, CA-19 to CA-21; `V exposes R` and `CA mitigates V` links
- [x] Greenbone scan or limitation recorded (`phase3-summary.md` section 6)
- [x] `py tools\validate_phase3.py` shows no `[FAIL]`

## Phase 4: Incident response
- [x] Attack simulation INC-01 (`tools/phase4_attack.py`)
- [x] Log-based detection (`tools/phase4_detect.py`), containment verified
- [x] Timeline, breach assessment, Art. 33 and Art. 34 texts, post-incident review (`04-incident/`)
- [x] Breach register and `tools/breach_clock.py`; KPI-05 and KPI-06 measured
- [x] `py tools\validate_phase4.py` shows no `[FAIL]`

## Phase 5: Integration
- [x] All 17 risks re-scored with evidence; heat map before / after / target (`05-integration/risk-rescoring.md`)
- [x] KPI register filled with lab values, each labelled (`05-integration/kpi-results.md`)
- [x] POL-04 and POL-05 v1.1; INC-01 -> CA-24/CA-25 -> POL in `traceability.csv`
- [x] CA-25 implemented and tested in the lab (`evidence/phase5/`)
- [x] Art. 34 reasoning added to the breach assessment
- [x] `py tools\validate_phase5.py` shows no `[FAIL]`

## Phase 6: Report and finalise
- [x] Chapters 1 to 8, Appendix A (evidence), references, contents (`06-report/`)
- [x] Figures 1 to 4 generated from the data (`06-report/figures/`)
- [x] HTML, PDF (Edge) and DOCX (Word) built with `py tools\build_report.py` (no pandoc)
- [x] Numbers cross-checked with `py tools\check_report_numbers.py`
- [x] `py tools\validate_phase6.py` shows no `[FAIL]`
- [ ] Author name and assignment details confirmed
