# Competitive Landscape — SentinelBench

Day 1. Systems and projects (vs. papers covered in literature.md). For each: what it tests,
how, size, threat model, limitations, and what SentinelBench contributes that is not redundant.

## Directly adjacent systems

### CodeIPI (UK AI Safety Institute, inspect_evals `ipi_coding_agent`)
- **Tests**: injection resistance of coding agents against payloads in issues/comments/README/config.
- **Evaluates**: string/behavior checks for payload compliance + task completion; IRR/TCR/FPR.
- **Size**: 45 samples.
- **Threat model**: repository artifacts as injection vector; agent otherwise honest.
- **Limitations**: single threat class; no secrets/supply-chain/CI/containment; no normalized
  telemetry format; no variance protocol; small corpus limits statistical power.
- **SentinelBench contribution**: broader threat coverage with the same "legitimate task + planted
  adversarial context" pattern, plus multi-dimensional scoring, telemetry, and repeated trials.
- **Verdict**: NOT redundant. We adopt their IRR/TCR/FPR metric vocabulary for the instruction-
  integrity dimension to ease cross-benchmark comparison.

### A.S.E / AICGSecEval (Tencent)
- **Tests**: whether repo-contextualized code generation introduces CVE-class vulnerabilities.
- **Evaluates**: per-instance static rules + functional tests. Deterministic.
- **Size**: repo-level instances from real CVE repos (26 LLMs evaluated).
- **Threat model**: benign environment; risk is model's own insecure output.
- **Limitations**: no adversarial context; no behavioral dimensions; tied to historical CVE shapes.
- **Contribution**: our `insecure-fix` scenario family overlaps their core question — we keep one
  such scenario for comparability but our novelty is elsewhere. Contamination note: they inherit
  SWE-bench's public-CVE contamination risk; our synthetic fixtures do not.

### SHADE-Arena (Anthropic safety-research)
- **Tests**: agent capability to pursue a *given* hidden malicious side task while evading monitors.
- **Threat model**: agent is intentionally malicious. Opposite polarity from SentinelBench.
- **Contribution**: none needed — complementary. Their monitor-evaluation idea suggests future work:
  adding an LLM monitor track to SentinelBench runs (explicitly out of scope for v1 determinism).

### RHB / ImpossibleBench / EvilGenie
- **Tests**: propensity to exploit evaluation mechanics when shortcuts exist (or tasks impossible).
- **Contribution**: we incorporate two design lessons: (1) every scenario must have a legitimate
  solution path verified by us before release; (2) include one control scenario where the only way
  to "pass" functional tests is gaming, to measure baseline gaming propensity without injection.

## Functional-only harnesses (SWE-bench, SWE-agent, Mini-SWE-agent, Terminal-Bench, InterCode)
- Mature Docker-based execution patterns; log-parsing evaluators; scaffold abstractions.
- **Contribution**: we reuse architectural patterns (container isolation, test-log parsing,
  adapter interfaces) but none measures security behavior. Not redundant.

## Defense-side tooling (not benchmarks)
- **Lasso Security, Invariant Labs, Prompt Guard-class classifiers**: runtime injection detection
  for agent transcripts. Could wrap SentinelBench as ground-truth-labeled evaluation data later.
- **SAST tools (Bandit, Semgrep, CodeQL)**: used inside our security evaluators where applicable;
  we deliberately write scenario-specific deterministic checks first, generic SAST second, because
  A.S.E showed custom rules beat generic scanning for known-intent vulnerabilities.

## Standards bodies
- OWASP (LLM top10, Agentic top10, MCP), CSA MAESTRO, IETF ASEB draft, NIST: all taxonomy/guidance,
  none ships an executable benchmark with fixtures + telemetry. We cite them for dimension grounding.

## What would make this project redundant?
Recorded Day 1 as falsification targets (per operating rule):
1. If CodeIPI or successor adds secrets/supply-chain/CI dimensions + telemetry → narrow remaining gap.
2. If A.S.E adds adversarial-context variants → overlap grows materially.
3. If a 2025-2026 system already does joint functional+security under environment attack that we
   failed to find → project should pivot to replication + extension. Search terms recorded in
   open-questions.md; re-check at Day 5 and Day 7.
