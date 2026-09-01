# Responsible Disclosure Policy

## Our commitments

1. **Inert adversarial content.** All attack payloads in scenarios are non-functional by
   construction (reserved domains, non-existent packages, marked fake secrets). We will not
   publish scenarios that execute against live targets.
2. **No live-target testing.** The safety boundary of this project forbids probing,
   exploiting, or accessing external systems. Model-provider APIs are used only through
   their official interfaces.
3. **Artifact transparency.** Every published number links to raw run artifacts; evaluator
   versions are recorded and original scores preserved when evaluators change.
4. **Failure reporting over marketing.** Negative results, evaluator false positives we
   discover in our own scoring, and replication disagreements are documented, not hidden
   (research/findings.md F10 is an example).

## Reporting model-security concerns

If benchmark runs reveal behavior that looks like a genuine vulnerability in a specific
agent product or model (e.g., systematic compliance with repository-borne injection), the
right channel is that vendor's security disclosure process — not this repository's issue
tracker. SentinelBench will:

- publish aggregate statistics and failure-class descriptions;
- withhold or gate detailed exploit traces for affected vendors on request;
- include takedown/contact information with each scenario release.

## Using SentinelBench results

Results describe *harness+model combinations under synthetic conditions*. Quoting single-run
numbers as model rankings misrepresents the methodology (multi-trial protocol, free-tier
roster, local sandbox). Follow docs/reproduction.md Level 1-2 before drawing conclusions.
