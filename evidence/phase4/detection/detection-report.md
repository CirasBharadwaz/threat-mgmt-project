# Detection report

Detection run: 2026-11-17T17:37:55Z. Source: nginx access log of `shop-proxy` (30 requests parsed) and the Juice Shop application log (`evidence/phase4/logs/`).

| Rule | Severity | Alert | Client | First event (UTC) | Last event (UTC) | Count |
|---|---|---|---|---|---|---|
| 1 | High | Admin user-data endpoints accessed | 172.24.0.1 | 2026-11-17T17:37:38Z | 2026-11-17T17:37:41Z | 26 |
| 2 | High | Enumeration burst (>= 20 API requests in 60 s) | 172.24.0.1 | 2026-11-17T17:37:38Z | 2026-11-17T17:37:41Z | 28 |
| 3 | High | Login followed by admin user-data access within 5 minutes (possible account takeover) | 172.24.0.1 | 2026-11-17T17:37:38Z | 2026-11-17T17:37:41Z | 26 |
