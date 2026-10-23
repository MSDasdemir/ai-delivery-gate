# Product brief

## Problem

AI-assisted coding can reduce implementation time while making it easier to produce a large change before the business outcome, evidence and operational safeguards are clear. Teams need a small, reviewable checkpoint that separates generated output from release authority.

## User

A technical product or project manager, engineering lead or release reviewer coordinating AI-assisted delivery.

## Job to be done

Before a change is released, collect the brief and evidence in one place, expose blocking gaps, record approval for one exact version and export a review artifact.

## Acceptance criteria

1. The same brief and evidence always produce the same gate result.
2. Any failed critical control blocks approval regardless of the readiness score.
3. A passing packet remains **REVIEW REQUIRED** until a reviewer explicitly approves it.
4. Changing any brief or evidence field invalidates the previous approval.
5. Exports unlock only for the currently approved version.
6. Optional AI suggestions cannot alter controls, evidence or approval.
7. The product never claims that a deployment occurred.

## Non-goals

- Verifying that uploaded evidence is genuine.
- Replacing CI, security review, identity, change management or deployment tooling.
- Calculating a universal release-risk score.
- Allowing a language model to approve or deploy a change.

## Production gaps

Authenticated reviewers, immutable audit retention, policy ownership, exception workflows, repository and CI adapters, scanner verification, deployment integration, secrets management, access controls and operational monitoring.
