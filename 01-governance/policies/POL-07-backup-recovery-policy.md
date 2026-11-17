# POL-07 Backup and Recovery Policy

| Field | Value |
|---|---|
| Policy ID | POL-07 |
| Owner | Head of IT |
| Approved by | Managing Director |
| Version | 1.0 |
| Approved on | 2026-11-16 |
| Next review | 2027-11-16 |
| Classification | Internal |
| Applies to | A-02, A-03 |
| Framework references | ISO/IEC 27001:2022 A.5.29, A.5.30, A.8.13, A.8.14; NIST CSF 2.0 PR.DS, RC.RP; GDPR Art. 32(1)(b), 32(1)(c) |

## Purpose

To make sure that customer data in the database (A-02) can be restored quickly and completely after
failure, error or attack, including ransomware.

## Scope

The customer database (A-02), its nightly backups (A-03), and the configuration needed to rebuild the web shop.

## Roles

The **Head of IT** owns this policy and is accountable for backups and restore tests. **IT administrators**
run and monitor backups and restores. The **Information Security Officer** checks the restore test records every quarter.

## Policy statements

1. **Frequency and targets.** A-02 is backed up every night. The targets are a recovery point
   objective (RPO) of 24 hours and a recovery time objective (RTO) of 8 hours.
2. **3-2-1 rule.** There are at least three copies, on two different storage types. One copy is
   **immutable and kept in a separate cloud account**, so that an attacker with admin access cannot delete it.
3. **Encryption and access.** Backups are encrypted at rest, and the keys are kept apart from the backups.
   Only IT administrators with MFA can reach them.
4. **Retention.** Daily backups are kept for 30 days and monthly backups for 12 months. Deleted customer
   data expires through this rotation, and deletions are re-applied after any restore (POL-03).
5. **Restore tests.** A full restore of A-02 is tested every quarter, and its result and duration are recorded.

## Compliance

KPI-08 tracks the share of quarterly restore tests that succeed within the RTO (target: 100%).

## Review

The Head of IT reviews this policy every year, and after any failed restore or data-loss incident.
