# POL-04 Access Control Policy

| Field | Value |
|---|---|
| Policy ID | POL-04 |
| Owner | Head of IT |
| Approved by | Managing Director |
| Version | 1.1 |
| Approved on | 2026-11-17 |
| Next review | 2027-11-16 |
| Classification | Internal |
| Applies to | A-01, A-02, A-03, A-04, A-07 |
| Framework references | ISO/IEC 27001:2022 A.5.3, A.5.15, A.5.16, A.5.17, A.5.18, A.8.2, A.8.3, A.8.5; NIST CSF 2.0 PR.AA; GDPR Art. 5(1)(f), 25(2), 32 (full list in `../framework-mapping.csv`) |

## Purpose

To make sure that only the right people get access to ShopNova's systems and customer data, with only the
rights they need, and that access is removed when it is no longer needed.

## Scope

Staff, administrator, service and customer accounts on the web shop (A-01), customer database (A-02),
backups (A-03), staff laptops (A-04) and cloud management consoles, including the privileged access held
by the IT administrators (A-07).

## Roles

| Role | Responsibility |
|---|---|
| Head of IT | Owns this policy. Approves role definitions and privileged access. |
| IT administrators | Create, change and remove accounts. Carry out reviews. |
| Head of Support | Confirms which support staff need which access, and reviews them every quarter. |
| Information Security Officer | Monitors compliance and reports KPI-03 and KPI-04. |
| All staff | Keep their credentials secret and use multi-factor authentication. |

## Policy statements

1. **Least privilege and need to know.** Access is granted by role. Each role gets only the rights its
   tasks need. Support staff need to read and update orders and customer contact data. They do not need
   database administration, bulk export or access to D-04 credentials.
2. **Unique accounts.** Every person has their own account. Shared or generic accounts are forbidden,
   except for documented service accounts with a named owner.
3. **Joiners, movers and leavers.** Access is granted on an approved request, changed on the day of a role
   change, and removed on a leaver's last working day.
4. **Multi-factor authentication (MFA).** MFA is mandatory for remote access, email, cloud consoles, every
   administrator account, and every account that can reach A-02.
5. **Privileged access.** Administrators use a separate admin account for admin tasks only, through a
   managed jump host. Privileged sessions are logged. Privileged rights are reviewed every quarter.
6. **Passwords.** At least 12 characters for users and 16 for administrators. Passwords are checked
   against lists of known breached passwords. There is no forced periodic change, only a change on
   suspected compromise.
7. **Access reviews.** Owners review privileged access every quarter and all other access every six months.
   Unneeded rights are removed within 5 working days.
8. **Customer accounts (A-01).** Customer passwords are stored only as salted hashes made with a modern
   algorithm (Argon2id or bcrypt). Login attempts are rate-limited, breached passwords are rejected, and
   customers can turn on two-factor authentication.
9. **Logging.** Access to Strictly confidential data and all privileged actions are logged and sent to
   central monitoring (POL-05).
10. **Sessions and tokens (new in v1.1, CA-24).** When a password is reset, an account is disabled, or a
    compromise is suspected, every session and login token issued to that account is invalidated at once.
    A password change alone is not enough. Login tokens for staff and administrator accounts are valid for
    at most 1 hour.

### Known gap: support staff hold admin rights on A-02

Support staff currently hold **administrator rights on the customer database (A-02)**. This breaks
statements 1, 4 and 5. It is kept deliberately as a realistic finding for a company at basic security maturity:

- **Risk:** recorded as R-01 in `02-risk/risk-register.csv`. It was Critical in Phase 2, and is Critical
  (25) after re-scoring, because the risk materialised as INC-01.
- **Treatment:** CA-01 (replace the admin rights with a role-based support view, and the shared support
  account with personal accounts) and CA-02 (MFA). Both were brought forward to 2026-11-24 after INC-01.
- **Interim:** temporary exception accepted by the Managing Director until 2026-11-24 (shortened from
  2026-12-15). **Correction in v1.1:** version 1.0 named "support accounts are named, not shared" as the
  compensating control. INC-01 showed this was wrong: the account used was the shared
  `support@` account, which also breaks statement 2. Until CA-01 is done, the compensating controls are:
  - the proxy rule CA-22/CA-25, which blocks reading user data through the shop;
  - the reset support password (CA-23).

## Compliance

KPI-03 (MFA coverage of privileged and remote accounts) and KPI-04 (access reviews done on time) are
reported every month. Breaches of this policy are handled under POL-01.

## Review

The Head of IT reviews this policy every year, and also after any incident involving misuse of access.
The known gap is reviewed on 2026-11-24.

## Change history

| Version | Date | Change | Trigger |
|---|---|---|---|
| 1.0 | 2026-11-16 | First approved version | Phase 1 |
| 1.1 | 2026-11-17 | New statement 10 (invalidate tokens on password reset; 1-hour staff tokens); known gap updated: exception shortened to 2026-11-24, false compensating control corrected | INC-01 post-incident review, CA-24 |
