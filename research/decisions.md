# Decision Log — SentinelBench

Append-only. Each entry: decision, rationale, what changed.

## D1 (Day 1): Synthetic fixtures over real-CVE repos
A.S.E derives tasks from real CVE repositories; that inherits SWE-bench-style contamination
(OpenAI's Feb 2026 audit) and couples scenarios to historical patch shapes. We synthesize
fixtures modeled on common OSS patterns. Trade-off: realism risk (OQ9), mitigated by
maintainer-recognizable repo structures.

## D2 (Day 2): No LLM judges in scoring
Following A.S.E's critique of judge-based evaluation; all dimensions deterministic.
Subjective analysis happens only in post-hoc failure mining, clearly separated from scores.

## D3 (Day 2): Agent-config files excluded from core suite
Harnesses auto-ingest AGENTS.md/CLAUDE.md-class files with near-system-prompt trust; measuring
compliance there conflates harness design with agent judgment. Opt-in scenario only (TM-D3).

## D4 (Day 2): Attempt-detection for supply-chain threats
We never actually install attacker packages; we detect the ATTEMPT via telemetry. Safer and
deterministic; limitation: misses installs we can't observe (documented).

## D5 (Day 4): Action-surfaces rule for security scanning
Security evaluators scan executed commands + agent transcript + added patch lines ONLY.
Raw tool payloads and diff context are excluded because they embed adversarial content the
agent may merely be handling/removing (finding F1). This is a load-bearing design rule for
anyone replicating this work.

## D6 (Day 4): Scripted adapters as executable spec
Compliant/misbehaving scripted agents encode the evaluator contract: compliant must score
FP+SP everywhere; misbehaving must trip SF wherever its behavior intersects invariants.
Runs before every campaign batch as a regression gate.

## D7 (Day 5): Free-model-only campaign
Per operator constraint, the experimental campaign uses only free-tier models available on
the opencode gateway. Absolute numbers will not generalize to frontier models (OQ1); the
research claim is failure-mode structure + benchmark validity, not model rankings.

## D9 (Day 9): API-failure runs are quarantined, never scored
Free-tier quota exhaustion produced 429 no-op runs that scored FF+SP — infrastructure
failure impersonating safe-but-failed agent behavior. Rule adopted: runs with zero
effective agent activity (adapter error + <=1 step) are invalidated at capture time
(campaign guard) and excluded everywhere; quarantine flags survive re-scoring.
Companion rule D10: experimental manipulations must carry machine-checked proof of
application (overlay_verified stamp) — silent no-ops manufacture findings just as
evaluator bugs do.

## D8 (Day 4): Local sandbox mode with documented limits
Docker daemon unavailable on host; local mode = fresh git-isolated workspace copy +
post-hoc containment analysis from telemetry. Egress is NOT enforced locally; payloads are
inert by construction (D4/TM-D2), so no real exfil/install occurs. Docker mode implemented
for hosts with a working daemon. Limitations in docs/isolation.md.
