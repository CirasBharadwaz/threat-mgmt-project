# Scope statement

## Case
ShopNova GmbH (fictional): Berlin-based online shop for consumer electronics accessories.
About 50 employees, about 20,000 registered EU customers, cloud-hosted customer database
(EU region), external payment provider, 40 laptops, nightly backups, some staff working remotely.

## In scope
- Public web shop and its hosting (A-01)
- Customer database and backups (A-02, A-03)
- Staff laptops and IT administrators with privileged access (A-04, A-07)
- Integrations with the payment provider, delivery partner and email provider (A-05, A-08, A-06)
- Processes: governance, risk management, vulnerability management, incident response

## Out of scope
- Physical security of buildings
- Internal systems of third-party providers
- The employee HR and payroll system

## Assumptions
- All data and all attacks are synthetic and run only in an isolated lab on machines I own.
- GDPR applies. The competent supervisory authority is the Berlin Commissioner for Data Protection.
- Current security maturity is basic: no formal policies, ad hoc patching, no tested incident response plan.

## Objectives
1. Establish governance for security and privacy
2. Identify and prioritise risks to personal data
3. Run a vulnerability management cycle on the web shop
4. Prepare for, simulate and review a personal data breach
5. Show how the four layers feed into one another

## Success criteria for the project
- Every asset and personal data category has an ID and an owner
- Every later document links back to these IDs via `traceability.csv`
- Every report claim can be traced to an artefact in this repository
