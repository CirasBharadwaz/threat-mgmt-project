# Schedule

The report deadline is recorded in `requirements-checklist.md`: Thursday 2026-11-19, exact time to be
confirmed. It was moved from 2026-11-17 (see decision log). Dates use YYYY-MM-DD.

Phases 0 to 6 were completed by 2026-11-17, as planned for the original deadline. The two extra days,
2026-11-18 and 2026-11-19, are buffer, used as follows:

- screen recordings (`DEMO-RUNBOOK.md`);
- title page details;
- the questions for the lecturer;
- a final check before submission.

| Phase | Name | Start | End | Effort |
|---|---|---|---|---|
| 0 | Scope and setup | 2026-11-15 | 2026-11-16 | 5% |
| 1 | Governance | 2026-11-16 | 2026-11-16 | 15% |
| 2 | Risk management | 2026-11-16 | 2026-11-16 | 15% |
| 3 | Vulnerability management | 2026-11-16 | 2026-11-17 | 25% |
| 4 | Incident response | 2026-11-17 | 2026-11-17 | 20% |
| 5 | Integration | 2026-11-17 | 2026-11-17 | 10% |
| 6 | Report and finalise | 2026-11-17 | 2026-11-17 | 10% |

## Notes
- Write each report section right after finishing its phase.
- Phases 3 and 4 involve the lab. Start the lab setup early, because tools and downloads take longer than expected.
- Greenbone's first feed sync can take several hours. Start it on 2026-11-16 (after approval), while Phase 2 documents are reviewed.
- Greenbone (Phase 3) and Wazuh (Phase 4) run one after the other, never together (about 15 GB RAM, about 50 GB free disk).
- If the lab is delayed, Phases 5 and 6 are still written on 2026-11-17 with whatever lab evidence exists, and the gap is stated in the report.
- 2026-11-18: screen recordings; title page; send the open questions to the lecturer.
- 2026-11-19: final rebuild and validation (`py tools\validate_phase6.py`), then submission once the time is confirmed.
