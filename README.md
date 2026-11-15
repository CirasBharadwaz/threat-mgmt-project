# Cyber Threat Management: Governance, Risk, Vulnerability and Incident Response

Data and privacy semester project. Case company: **ShopNova GmbH** (fictional, Berlin web shop).
All data in this repository is synthetic. No real personal data, no real credentials.

## How we work

The project is built phase by phase. Each phase adds files to this folder, and each
phase ends with a validation run so nothing is left half-finished.

| Phase | Folder | Status |
|---|---|---|
| 0 Scope and setup | `00-scope-and-setup/` | Built, you fill in the requirements and review the registers |
| 1 Governance | `01-governance/` | Not started |
| 2 Risk management | `02-risk/` | Not started |
| 3 Vulnerability management | `03-vulnerability/` | Not started |
| 4 Incident response | `04-incident/` | Not started |
| 5 Integration | `05-integration/` | Not started |
| 6 Report and finalise | `06-report/` | Not started |

Supporting folders: `appendices/` (long tables, raw outputs), `evidence/` (screenshots, logs),
`tools/` (helper scripts).

## Run order (Phase 0)

Run all commands from the project root (the folder that contains this README).
On Windows, use `python` instead of `python3` (there `python3` usually opens the
Microsoft Store), and run the `.sh` script from Git Bash.

1. Check your machine:
   ```bash
   bash tools/check_tools.sh
   ```
2. Fill in `00-scope-and-setup/requirements-checklist.md` from your assignment brief.
3. Read and adjust `scope-statement.md`, `asset-register.csv`, `data-inventory.csv`
   in `00-scope-and-setup/`. Log every change in `decision-log.md`.
4. Validate everything:
   ```bash
   python3 tools/validate_phase0.py
   ```
   Fix every `[FAIL]`. `[TODO]` lines are the things only you can fill in.
5. Preview the data flow diagram: paste `00-scope-and-setup/data-flow.mmd`
   into https://mermaid.live
6. Put the project under version control:
   ```bash
   git init
   git add .
   git commit -m "Phase 0: project scaffold"
   ```

## The traceability thread

Every item has a permanent ID (see `00-scope-and-setup/id-scheme.md`) and links are
recorded in `traceability.csv`:

`POL (policy) -> R (risk) -> V (vulnerability) -> INC (incident) -> CA (corrective action) -> R (re-scored)`

This is what turns four separate topics into one managed process.
