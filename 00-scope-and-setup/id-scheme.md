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

## Example chain
```
POL-02 governs R-12
V-07 exposes R-12
V-07 triggers INC-01
INC-01 resolved-by CA-02
CA-02 re-scores R-12
```
