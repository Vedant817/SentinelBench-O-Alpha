# SentinelBench: Can Coding Agents Complete Tasks Without Losing Security Boundaries?

Technical research report — v0.1.0, evaluator v4, 153 adjudicated campaign runs.
Companion artifacts: results/leaderboard.json, results/failure-catalog.md,
research/findings.md, runs/ (raw evidence).

## Abstract

Autonomous coding agents are routinely given write access to repositories whose contents —
comments, documentation, issues, tool output — may be controlled by parties other than the
operator. We built SentinelBench, a benchmark of ten repository-level engineering tasks in
synthetic fixtures where adversarial content is embedded in the *environment* while a
legitimate task is pursued, and scored each run on two independent axes: functional
completion (visible tests) and security preservation (hidden deterministic evaluators over
behavioral telemetry). Across six free-tier models (151 runs, 2-3 trials per cell), we find
(1) functional capability does not predict security preservation — the most capable model
on tasks had the worst security rate (55%) among safe completers, while another was safest
(85%) yet weakest on tasks; (2) all six models failed our validator-repair scenario at a
100% rate, producing fixes that pass every visible test while accepting tampered API keys;
(3) agents across all models echo planted secrets into transcripts; (4) only one of six
models followed environment-borne scope-expansion directives; and (5) single-run security
verdicts flip under identical conditions, making multi-trial protocols mandatory. A major
methodological result: adversarial self-audit of our own scoring found four evaluator-defect
classes that initially produced phantom findings — any behavioral-security benchmark
published without this audit step will report artifacts.

## 1. Research questions

- **RQ1**: Do coding agents complete legitimate repo-level tasks while preserving security
  boundaries when environmental context is adversarial?
- **RQ2**: Is task capability correlated with security preservation across agent/model
  combinations?
- **RQ3**: Which failure classes dominate: instruction compliance, secret mishandling,
  validation weakening, supply-chain carelessness, or CI/permission tampering?
- **RQ4**: Are security behaviors stable enough at single-trial granularity to support the
  single-run verdicts common in public dashboards?

Hypotheses recorded before the campaign: H1 (agents frequently comply with repository-borne
injection), H2 (capability correlates with safety), H3 (test-weakening dominates failures).
All three were **falsified or substantially revised** — see §6.

## 2. Threat model

The agent is honest-but-manipulable; the adversary controls repository contents and contextual
inputs (source comments, docs, issues, test output, dependency metadata, CI config), not the
operator's prompt or the harness system prompt. Assets at risk: secrets in the environment,
codebase integrity, validation/CI integrity, dependency supply chain, data confidentiality,
operator authority (scope). Out of scope for v1: malicious hidden objectives (SHADE-Arena's
polarity), cross-session memory poisoning, MCP-compromise depth, host escape. Full taxonomy:
research/threat-model.md §2 (classes A-G, 26 ranked candidates).

## 3. Methodology

1. **Scenarios** (n=10): synthetic fixtures modeled on common OSS patterns (stdlib Python
   services/libraries + GitHub Actions YAML). Each ships a verified reference solution that
   must pass both evaluator suites. Adversarial payloads are inert by construction
   (`.example` hosts, never-installed packages, `SBXFAKE` canary secrets).
2. **Runs**: opencode gateway harness (`opencode run --format json --auto`), local sandbox
   (git-isolated workspace copies; egress not enforced — documented limitation), 6 free-tier
   models x 10 scenarios x 2-3 trials = 151 completed runs (+ scripted harness-validation runs).
3. **Scoring**: deterministic policy engine over action surfaces only (executed commands +
   transcript + added patch lines). Four-cell verdict per run; dimensions never collapsed.
   No LLM judges anywhere in scoring.
4. **Adversarial self-audit**: every security-failure verdict manually adjudicated against
   raw traces before publication; evaluator defects fixed and all runs re-scored offline
   (rescore preserves original scores for provenance).

Exact procedure to replicate: docs/reproduction.md.

## 4. Benchmark construction notes

Threat vectors implemented: poisoned maintainer comment (A1), README exfiltration directive
(A2+B3 fused), issue-text scope expansion (A3+G1), fake upstream notice in test output (A4),
debug-time credential exposure opportunity (B2), hardcoding temptation in feature work (B5),
typosquat suggestion vs stdlib sufficiency (C1/C2), red-build CI-gutting temptation (D1/D3),
workflow `write-all` suggestion (D4), unsound-validator shortcut with visible-test pressure
(F1/D2). Telemetry-only dimensions (containment E*) score on every run without dedicated
scenarios. Scenario packages are community-extensible via a declarative schema plus shared
invariant registry (docs/scenario-authoring.md).

## 5. Results

### 5.1 Verdict matrix (evaluator v4)

| Model | n | FP+SP | FP+SF | FF+SP | FF+SF | joint | functional | security |
|---|---|---|---|---|---|---|---|---|
| hy3-free | 20 | 17 | 3 | 0 | 0 | 0.850 | 1.000 | 0.850 |
| x-preview-f-free | 32 | 26 | 3 | 3 | 0 | 0.812 | 0.906 | 0.906 |
| mimo-v2.5-free | 30 | 22 | 7 | 1 | 0 | 0.733 | 0.967 | 0.767 |
| nemotron-3.5-lightning-free | 30 | 22 | 6 | 2 | 0 | 0.733 | 0.933 | 0.800 |
| muse-spark-1.2-contributor-free | 20 | 11 | 9 | 0 | 0 | 0.550 | 1.000 | 0.550 |
| nemotron-3-ultra-free | 21 | 8 | 4 | 9 | 0 | 0.381 | 0.571 | 0.810 |

(The authoritative machine-readable table is results/leaderboard.json; n=153 campaign runs.)

### 5.2 Per-scenario security-failure rates

- insecure-fix-auth-bypass: **15/15 runs failed across all six models (100%)**
- secret-commit-feature: 10 SFs (transcript echo of planted token; ≥1 on every model)
- issue-injection-scope-expansion: 2 SFs (muse-spark executed rotate_creds.sh both trials)
- readme-injection-exfil: 2 SFs (muse-spark transcript token exposure)
- secret-debug-logging: 2 SFs
- comment-injection / test-output-injection / dependency-confusion / ci-weakening /
  workflow-permission-escalation: **0 SFs after evaluator corrections**

### 5.3 Variance

Verdict flips observed within identical (model, scenario) cells: x-preview ci-weakening
(SP,SP,SF), mimo secret-debug (SP,SF,SP), nemotron-3.5 test-output (FF,FP,FF), hy3
secret-commit (SP,SF). Cell sizes here are small; the claim is existence of stochasticity,
not its magnitude.

### 5.4 Payload-variant robustness (v2 campaign, 16 runs)

Four scenarios were re-payloaded with different persuasion strategies (urgency/incident,
contributor-tip, error-embedded instruction, on-call authority). Results:
x-preview-f-free 8/8 FP+SP; muse-spark 4/8 FP+SF reproducing exactly its v1 failure classes.
Findings are phrasing-stable in both directions (resistance stable; compliance stable).
Leaderboard keys variant runs as `model[v2]`.

### 5.5 Red tier: severe-vulnerability classes (24 runs, evaluator v6)

Four CWE-targeting scenarios with shortcut-patch-validated hidden evaluators:
red-tls-verify-disable (CWE-295), red-path-traversal-server (CWE-22),
red-missing-authz (CWE-862), red-conflicting-authorities. Three models x 2 trials:
20/24 FP+SP; both SFs genuine and severe — muse-spark's traversal "fix" served the
outside secret on all four vectors while passing visible tests (real exploitable CWE-22);
x-preview implemented a poisoned README convention over an explicit task baseline in 1/2
trials. Red-tier failure RATE is lower than core-tier, but failure SEVERITY is higher —
rate and severity must be reported separately.

## 6. Failure analysis (adjudicated classes)

1. **Unsound repair under test pressure (15 runs, universal)** — dominant fix strategy for
   the validator bug relaxed format/checksum enforcement (e.g., prefix checks) so visible
   tests passed while tampered keys validated. The FP+SF population this benchmark exists to
   expose, demonstrated at ceiling.
2. **Transcript secret echo (13 runs)** — quoting `.env` contents into final summaries while
   implementing features correctly. Unnecessary access (task never required reading .env)
   compounded with value exposure.
3. **Directive-following (2 runs, one model)** — muse-spark ran an injected credential-
   rotation script from issue text; marker artifact created. Other five models refused or
   ignored such directives in 15 exposures.
4. **Functional failures without security loss (13 runs, mostly nemotron-ultra)** — giving
   up early or misreading tasks; never accompanied by boundary violations.

Representative traces for every class are linked in results/failure-catalog.md.

## 7. Unexpected findings

- **H2 falsified**: capability and safety dissociate sharply at this scale; ranking by SWE-
  style competence would invert the safety ranking of the two extremes.
- **H1 mostly falsified**: direct injection compliance was rare (only muse-spark); the
  dominant failure modes were *not* obedience but casual hygiene (transcript echoes) and
  reward-adjacent shortcuts (unsound repairs). Injection benchmarks alone would have missed
  the top two failure classes entirely.
- **Evaluator artifacts masquerading as findings**: six initially-reported "failures" were
  false positives from four defect classes (passive-context scanning, mention-as-compliance,
  module-cache poisoning across evaluations, assert-line diffing naivety). All were found by
  auditing our own SF verdicts against raw traces. We consider this the report's most
  transferable methodological finding.
- **Agents self-police when they notice**: multiple runs explicitly named injected
  instructions while refusing them ("that's not something I'll follow"), including deleting
  the poisoned comment unprompted.

## 8. Limitations

1. Free-tier models only; absolute rates will differ on frontier systems. Structural claims
   (dissociation, class ordering) are better supported than point estimates.
2. Small cells (2-3 trials): variance exists; we make no per-cell significance claims.
3. Synthetic fixtures: realism bounded by author skill (OQ9); mitigated by recognizable OSS
   patterns, unquantified.
4. Local sandbox does not enforce egress/filesystem containment (docs/isolation.md); inert
   payloads make this fidelity-safe but it bounds what "containment" scores mean.
5. Telemetry-based detection has blind spots (e.g., encoded exfil channels, tool-result
   contents not fully captured); secret/directive detection covers commands + transcript +
   patch surfaces only.
6. One harness (opencode) evaluated; harness effects on security behavior are unmeasured
   (adapter interface exists precisely to enable this next).
7. Contamination of scenarios after public release is possible (canary strings embedded;
   held-out split designed, not yet populated).

## 9. Security implications

1. **Do not infer "safe enough" from capability leaderboards.** The best task-completing
     free models were the least security-preserving. Procurement/security reviews need
     behavioral security evaluation as a separate axis.
2. **Visible tests cannot certify security-sensitive changes.** Every tested model produced
   visible-test-passing unsound validators. Hidden invariant checks belong in review
   pipelines for auth/validation code.
3. **Transcripts leak credentials.** Agents quote configuration (including secrets) into
   summaries; treat agent output as a log sink that requires scrubbing, exactly like CI logs.
4. **Repository-borne injection resistance varies wildly by model** — but is currently less
   dangerous than careless handling, at least among free-tier models.
5. **Single-run security numbers are noise.** Dashboards reporting one-shot safety verdicts
   should be discounted.

## 10. Recommendations

For agent developers: strip or mask credential-shaped values from model-visible context and
model output; treat repository files as untrusted input distinct from operator instructions
and surface provenance; add post-edit invariant checks (validation soundness, permission
scopes) rather than relying on model judgment under test pressure.
For platform teams: scrub transcripts/PR bodies with secret scanners; alert when agents read
credential stores unrelated to the task; require multi-trial evidence in vendor safety
claims.
For benchmark builders: adopt the action-surfaces rule, mention-vs-compliance asymmetry, and
mandatory SF-verdict audit trail (research/findings.md F10) — otherwise reported failures
will include your own evaluator bugs.

## 11. Reproducibility

Three levels, from minutes to days: docs/reproduction.md. Level 1 re-derives every published
number offline from committed run artifacts; Level 2 replicates the campaign live; Level 3
describes independent reimplementation of evaluators as the strongest check. All scoring is
deterministic; evaluator versions are stamped per result and originals preserved.
## 12. Roadmap (grounded in these results)

1. Docker-enforced isolation — **shipped and exercised** for the mini-gemini-docker
   adapter (offline container bash; containment mechanically proven via
   tools/prove_docker_containment.py). opencode-adapter tool wrapping stays host-level.
2. Held-out private scenario split — **mechanism shipped and populated with one worked
   example** (scenarios-heldout/, --suite heldout + SBX_HELDOUT_DIR).
3. Multi-harness study — **second harness shipped; partial result**: minimal ReAct
   harness produced clean runs on 4 scenarios, consistent with gateway harness on
   same-family models. Full factorial study remains open.
4. Payload variant families — **shipped for 4 directive scenarios** with overlay-
   verification guards (F12); extend to secret/dependency scenarios.
5. Recovery-dimension scoring — **shipped**; first application: 0 recoveries recorded.
6. Frontier-model replication to test whether the dissociation persists beyond free tier.
