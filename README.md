# Cyber Threat Management: Governance, Risk, Vulnerability and Incident Response

Data and privacy semester project by Bharadwaz Cirasanagandla.
Case company: **ShopNova GmbH** (fictional Berlin web shop). The repository contains no real customer
data and no real credentials of any system. Two kinds of public third-party data remain, and are labelled
where they appear:

- the published OWASP Juice Shop demo credentials, which the lab scripts need to reproduce the attacks;
- maintainer and mailing-list e-mail addresses inside the raw Trivy scanner output, which come from
  public vulnerability databases.

## The report

| Format | File |
|---|---|
| PDF | [`06-report/build/ShopNova-threat-management-report.pdf`](06-report/build/ShopNova-threat-management-report.pdf) |
| Word | [`06-report/build/ShopNova-threat-management-report.docx`](06-report/build/ShopNova-threat-management-report.docx) |
| HTML | [`06-report/ShopNova-threat-management-report.html`](06-report/ShopNova-threat-management-report.html) |
| Sources | Markdown chapters in [`06-report/`](06-report/), starting with [`00-executive-summary.md`](06-report/00-executive-summary.md) |

The highlighted fields on the title page (university, course, lecturer, matriculation number,
submission date) are placeholders to be completed before submission. Enter the values in
[`06-report/title-page.json`](06-report/title-page.json), then rebuild with
`py tools\build_report.py --author "Bharadwaz Cirasanagandla"`.

To replay the lab for screen recordings, follow the demo runbook: [`DEMO-RUNBOOK.md`](DEMO-RUNBOOK.md)
(one-page version: [`DEMO-CHEATSHEET.md`](DEMO-CHEATSHEET.md)).

## Phases

| Phase | Folder | Status | Validator |
|---|---|---|---|
| 0 Scope and setup | [`00-scope-and-setup/`](00-scope-and-setup/) | Done | `tools/validate_phase0.py` |
| 1 Governance | [`01-governance/`](01-governance/) | Done | `tools/validate_phase1.py` |
| 2 Risk management | [`02-risk/`](02-risk/) | Done | `tools/validate_phase2.py` |
| 3 Vulnerability management | [`03-vulnerability/`](03-vulnerability/) | Done (Greenbone: limitation recorded) | `tools/validate_phase3.py` |
| 4 Incident response | [`04-incident/`](04-incident/) | Done | `tools/validate_phase4.py` |
| 5 Integration | [`05-integration/`](05-integration/) | Done | `tools/validate_phase5.py` |
| 6 Report and finalise | [`06-report/`](06-report/) | Done | `tools/validate_phase6.py` |

Supporting material:

- [`evidence/`](evidence/): raw lab outputs, listed in Appendix A of the report.
- [`tools/`](tools/): validators, generators and lab scripts.
- [`traceability.csv`](traceability.csv): every link between IDs.
- [`00-scope-and-setup/decision-log.md`](00-scope-and-setup/decision-log.md): every decision, with its reason.

## Run order from a clean clone (Windows PowerShell)

**Needed:**

- Git and Python 3 with the `py` launcher, for everything.
- Microsoft Edge and Microsoft Word, only to rebuild the report.
- Docker Desktop, only to re-run the lab.

The tools use the Python standard library only; there is nothing to `pip install`. Use `py`, not
`python3`, because on Windows `python3` often opens the Microsoft Store.

```powershell
# 1. get the project
git clone https://github.com/CirasBharadwaz/threat-mgmt-project.git
cd threat-mgmt-project

# 2. validate everything (no Docker needed; each validator re-runs the earlier phases)
py tools\validate_phase6.py

# 3. after changing a register, regenerate the derived files, then validate again
py tools\build_risk_heatmap.py      # 02-risk/risk-heatmap.md from the risk register
py tools\build_traceability.py      # derived links in traceability.csv
py tools\build_phase5_tables.py     # 05-integration tables from the registers
py tools\validate_phase6.py

# 4. rebuild the report (HTML; PDF printed by Edge; DOCX saved by Word)
py tools\build_report.py --author "Bharadwaz Cirasanagandla"
py tools\check_report_numbers.py    # every key number in the report against its source

# 5. before every commit: secrets and personal-data scan
py tools\secrets_scan.py

# 6. optional: check the machine for the lab tools (Git Bash by full path; in PowerShell 'bash' starts WSL)
& "C:\Program Files\Git\bin\bash.exe" tools/check_tools.sh
```

The lab itself (Docker) is described step by step in [`DEMO-RUNBOOK.md`](DEMO-RUNBOOK.md), with more
detail in [`03-vulnerability/lab/README.md`](03-vulnerability/lab/README.md) and
[`04-incident/README.md`](04-incident/README.md). Run it from a separate clone, because the lab scripts
write into `evidence\`.

## Third-party software

- **OWASP Juice Shop.** Copyright (c) 2014-2026 Bjoern Kimminich & the OWASP Juice Shop contributors,
  MIT licence (https://github.com/juice-shop/juice-shop). It is used as the lab target.
  `03-vulnerability/lab/fix/login.original.js` and `login.js` are derived from its `build/routes/login.js`
  and carry the MIT notice. One third-party e-mail address in them is redacted.
- **Lab tools,** used as unmodified container images: OWASP ZAP, Nmap, Trivy, the OWASP ModSecurity Core
  Rule Set, nginx and Greenbone Community Edition. Each is under its own licence; see the references in
  the report.

## The traceability thread

Every item has a permanent ID (see [`00-scope-and-setup/id-scheme.md`](00-scope-and-setup/id-scheme.md)),
and every link between items is recorded in `traceability.csv`:

`POL (policy) -> R (risk) -> V (vulnerability) -> INC (incident) -> CA (corrective action) -> R (re-scored) / POL (updated)`

For example:

- **Prevention:** POL-02 governs R-12, V-01 exposes R-12, and CA-06 mitigates V-01 and re-scores R-12 from 20 to 10.
- **Learning:** V-06 triggers INC-01, which is resolved by CA-24 and CA-25; these update POL-04 and POL-05 to v1.1.
