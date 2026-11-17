# ID scheme (used in every document)

| Prefix | Meaning | Format | Example |
|---|---|---|---|
| A- | Asset | A-01 | A-02 customer database |
| D- | Data category | D-01 | D-02 delivery address |
| POL- | Policy | POL-01 | POL-01 Information Security Policy |
| R- | Risk | R-01 | R-12 SQL injection exposes customer data |
| V- | Vulnerability | V-01 | V-07 outdated web framework |
| INC- | Incident | INC-01 | INC-01 simulated data breach |
| CA- | Corrective action | CA-01 | CA-02 add WAF rule |
| KPI- | Metric | KPI-01 | KPI-01 time to patch criticals |

## Rules
1. Never reuse or renumber an ID, even if the item is deleted. Mark it "withdrawn" instead.
2. Use the ID in every document that mentions the item, in text, tables and diagrams.
3. Record every link in `../traceability.csv` as `from_id,relation,to_id,note`.
4. Suggested relations: `governs`, `exposes`, `mitigates`, `triggers`, `resolved-by`, `re-scores`.
   Added in Phases 1 and 2: `applies-to` (POL to A, a policy covers an asset) and
   `treated-by` (R to CA, a planned risk treatment action).
   Added in Phase 5: `re-scores` from a CA, V or INC to the risk whose score it changed
   (`rescore_drivers` in the risk register), and `updates` (CA to POL, a corrective action that
   changed a policy; `changed_by` in the policy register).
5. CA- IDs cover both planned risk treatment actions (from Phase 2) and corrective
   actions raised by incidents (from Phase 4). They share one sequence; the treatment
   plan's `source` column says which kind each one is.
6. The example chain below is illustrative. POL-02 and R-12 were numbered so that its
   first line holds in this project; V, INC and CA numbers are set by later phases.

## Example chain
```
POL-02 governs R-12
V-07 exposes R-12
V-07 triggers INC-01
INC-01 resolved-by CA-02
CA-02 re-scores R-12
```
