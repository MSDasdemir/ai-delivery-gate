# Validation evidence

Validated on 23 October 2026 using Python 3.12 and Streamlit 1.63.0.

## Automated checks

`python -m unittest discover -s tests -v`

- 25 tests passed.
- Core coverage includes deterministic verdicts, critical-control blocking, advisory warnings, risk-dependent review, invalid evidence, exact-version approval, approval invalidation, exports and AI-output validation.
- Interface coverage exercises the complete approval flow, change invalidation and a failed-test blocker.
- The local-model adapter test confirms loopback-only access and an explicit offline failure.

Raw output: [test-results.txt](test-results.txt).

## Interface review

The application was opened locally at `127.0.0.1:8505` and checked at a desktop viewport. The change identity, workflow, four tabs, default brief and synthetic-demo disclosure render without an application exception. Streamlit interaction tests provide the repeatable approval and blocking checks.

## Accepted behavior

- The complete default packet is **REVIEW REQUIRED**, not automatically ready.
- One failed automated test changes the result to **BLOCKED** and disables approval.
- A current human approval changes the result to **READY** and unlocks exports.
- Editing the business outcome after approval invalidates it.
- Optional AI failure does not interrupt the deterministic gate.

## Remaining production validation

No identity provider, CI service, source repository, scanner, policy registry, audit database, deployment platform or monitoring system is connected. Those integrations require contract, authorization, concurrency, retention, tamper-resistance and recovery testing before production use.
