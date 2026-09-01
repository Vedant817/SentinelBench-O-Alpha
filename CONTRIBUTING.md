# Contributing to SentinelBench

Thanks for considering a contribution. This project optimizes for **credible evidence**,
not scenario count or code volume.

## Ways to contribute (in impact order)

1. **Adversarial findings against the benchmark** — scenarios that can be gamed, evaluator
   false positives/negatives with run-id evidence, unrealistic fixtures. These are first-class
   contributions; several of our own headline "failures" were evaluator artifacts we caught
   this way (research/findings.md F10).
2. **New failure classes** — a scenario demonstrating a security-failure mode not in
   research/threat-model.md §2.
3. **Adapters** — additional agent harnesses behind the Adapter contract.
4. **Replication runs** — other models/hardware; PRs updating results/ must include raw
   run directories.
5. Documentation fixes.

## Ground rules

- No LLM judges in scoring. Deterministic evaluators only; subjective analysis goes in
  research notes, clearly separated from scores.
- Every scenario needs a verified legitimate solution and inert payloads (see
  docs/scenario-authoring.md hard rules).
- Multi-trial minimum: claims about model behavior need >=3 trials per cell.
- Preserve history: findings and decisions are append-only; superseded conclusions stay
  recorded with what-changed-and-why.

## Process

1. Open an issue describing the finding/scenario before large PRs.
2. PR checklist: `python -m unittest discover -s tests` green;
   `python -m sentinelbench validate` green; scripted validation matrix unchanged;
   new scenarios include reference solutions + both scripted-agent checks.
3. Keep runtime deps stdlib-only for harness and scenarios.

## What we will not merge

- Scenarios requiring network access, real secrets, or live vulnerable targets.
- Evaluators keyed to one vendor's output format without normalization.
- Leaderboard updates without raw run artifacts.
