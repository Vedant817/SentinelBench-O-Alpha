# Literature Review — SentinelBench

Last updated: Day 1 of project. This file records what we read, what it does, and what it
implies for SentinelBench design. Conclusions that changed over the project are appended,
never erased (see decisions.md).

## 1. Repository-level functional benchmarks

### SWE-bench (Jimenez et al., 2023) and family
- **What it tests**: whether an agent's patch resolves a real GitHub issue, verified by
  fail-to-pass and pass-to-pass tests.
- **How it evaluates**: run test suite in Docker; parse test logs; resolution = all F2P pass,
  no P2P regressions. Deterministic.
- **Size**: 2,294 original; 500 Verified; 300 Multilingual; Pro has public/commercial/held-out splits.
- **Threat model**: none. The environment is assumed benign.
- **Limitations**: functional-only signal; contamination (OpenAI's Feb 2026 audit found ~59% of
  hardest Verified tasks had broken tests and evidence frontier models trained on solutions —
  OpenAI publicly stopped evaluating on Verified); scaffold-dependence moves scores 10-20 points;
  Python-centric in original form.
- **Implication for SentinelBench**: adopt the *execution-based deterministic evaluation*
  pattern (it works), but synthetic fixtures to avoid contamination, and add security dimensions.

## 2. Secure code generation benchmarks

### SecurityEval (Siddiq & Santos, MSR4P&S 2022)
- 121-130 prompts mapped to ~75 CWEs; evaluates whether a code generator emits vulnerable snippets.
- Snippet-level; static analysis (Bandit/CodeQL) + manual validation. No repository context, no agent.

### CyberSecEval 3/4 (Meta Purple Llama)
- Industry-scale suite: insecure code generation (instruct + autocomplete), prompt injection
  resistance, cyberattack helpfulness, autonomous-offensive capabilities for agents.
- Evaluates model outputs mostly at completion level; agentic tracks are newer and narrower.
- Implication: "insecure code emission" is well covered; behavioral integrity inside a repo is not.

### A.S.E / AICGSecEval (Tencent, arXiv:2508.18106)
- **Closest secure-generation competitor.** Repository-level tasks derived from real CVE patches;
  per-instance custom static detection rules; reproducible framework; evaluated 26 LLMs.
- Measures whether AI-written code is vulnerable in repo context.
- **Does not**: plant adversarial context, evaluate instruction integrity, secrets handling,
  supply-chain or CI behavior, or record cross-vendor telemetry. Tasks are benign-context by design.
- Implication: our "functionally-correct-but-vulnerable patch" dimension overlaps partially with
  A.S.E; our adversarial-environment dimensions do not overlap at all.

### SecCodeBench (Alibaba + Tsinghua/ZJU/Fudan/PKU)
- Security benchmark aimed explicitly at agentic coding tools; focuses on generated-code security
  properties. Same family as above: output-code security, not environment-borne manipulation.

## 3. Indirect prompt injection research and benchmarks

### InjecAgent (Zhan et al., ACL Findings 2024)
- 1,054 cases; untrusted tool outputs carry attacker instructions (direct harm / data exfiltration);
  measures attack success rate across agent scaffolds. GPT-4 ReAct complied 24% baseline.
- Tool-output domain, not repository-level software engineering; single-turn-ish; no functional task
  coupling.

### CodeIPI (UK AISI inspect_evals, ipi_coding_agent)
- **Closest injection competitor.** 45 samples (35 injected + 10 benign) pairing legitimate bug-fix
  tasks with payloads hidden in issue text, code comments, README, config files.
- Metrics: Injection Resistance Rate, Task Completion Rate, False Positive Rate on clean samples.
- **Limitations we can improve on**: small corpus; injection-only threat class; no secret/supply-chain/
  CI/containment dimensions; no persistent flight-recorder format; no multi-trial variance protocol;
  no isolation guarantees documented; single-harness orientation.
- Implication: validates feasibility of our core idea; confirms nobody has built the broader system.

### ReadSecBench / CSA README-injection note (Mar 2026) / IDEsaster
- Documents systemic auto-ingestion of AGENTS.md/CLAUDE.md/.cursorrules as near-system-prompt-trust
  across Copilot, Cursor, Claude Code, Windsurf, Roo, Cline, Junie, Zed. Measured ~84-91% compliance
  with malicious README instructions across models; 93% of human reviewers missed planted attacks.
- Real-world motivation for repository-borne injection scenarios; also a warning: our fixtures must
  not rely on auto-ingested agent-config files (that would measure harness config loading, not agent
  judgment) — see threat-model decision TM-D3.

### Rules File Backdoor / RoguePilot (2025-2026 incident literature)
- Demonstrated propagation of poisoned rules files through forks; GitHub Copilot passive-injection
  takeover. Motivates supply-chain-of-agent-behavior framing.

## 4. Reward hacking / sabotage evaluations

### ImpossibleBench (Zhong et al., 2025)
- Deliberately impossible tasks; any passing solution must have exploited tests. Measures fabrication
  propensity. Single-step coding tasks.
- Implication: we must ensure every scenario has a legitimate solution (else we measure fabrication,
  not security), and we should include an impossible-task control scenario to detect agents whose
  default strategy is gaming.

### Reward Hacking Benchmark (RHB, 2026)
- Multi-step tool-use tasks with naturalistic shortcuts; exploit taxonomy: sequence manipulation 31%,
  metadata leakage 24%, tampering 19%; exploit rate rises with horizon length; environmental hardening
  cut exploits 6.5%→0.8%. 72% of exploits had explicit CoT rationale.
- Implication: their taxonomy informs our failure-mining codes; their finding that hardening matters
  supports our evaluator-hardening phase.

### SHADE-Arena (Anthropic, 2025)
- Main task + hidden malicious side objective given TO the agent; measures sabotage capability and
  monitor evasion. Threat model: agent is malicious.
- **Key contrast**: SentinelBench's agent is presumed honest-but-manipulable; the *environment* is
  adversarial. Complementary, not redundant.

### Anthropic sabotage evaluations / emergent misalignment from reward hacking (2024-2025)
- Frontier models can sabotage codebases when instructed; reward hacking during RL generalizes to
  broader misalignment. Motivates CI-integrity and test-weakening scenarios: these are exactly the
  behaviors that emerge under pressure even without explicit malice.

## 5. Standards and guidance

- **OWASP Top 10 for LLM Applications 2025**: LLM01 = Prompt Injection. Our instruction-integrity
  dimension operationalizes this for the coding-agent setting.
- **OWASP Agentic AI Top 10 (2026)** and **OWASP MCP guidance**: tool-safety, memory poisoning,
  excessive agency, identity confusion. Mapped into our taxonomy (see threat-model.md).
- **CSA MAESTRO**: layered agentic threat modeling; repository files = Layer 2 data operations
  attacking Layer 1 models. We use MAESTRO vocabulary where useful.
- **IETF draft ASEB** (han-bmwg-agent-security-benchmark): taxonomy-only framework doc; no executable
  artifacts. Confirms standards bodies see the gap but haven't filled it.
- **NIST AI RMF / SSDF (SP 800-218)**: vocabulary for secure-development controls our evaluators
  check (dependency integrity, CI permissions).

## 6. Supply-chain and CI security background

- Dependency confusion / typosquatting literature (Ohm et al. USENIX 2020 "Backstabber's Knife
  Collection") informs our dependency-substitution scenario design.
- GitHub Actions security guidance (least-privilege GITHUB_TOKEN, pinned actions) informs the
  workflow-permission scenario's invariant definitions.
- SLSA provenance levels inform our auditability dimension (run reconstruction requirements).

## 7. Synthesis: the gap SentinelBench fills

| System | Repo-level task | Adversarial environment | Functional+Security joint scoring | Secrets | Supply chain | CI integrity | Containment | Flight recorder | Deterministic eval |
|---|---|---|---|---|---|---|---|---|---|
| SWE-bench family | yes | no | no | – | – | – | – | partial | yes |
| CyberSecEval | no | no | no | – | – | – | – | no | partial |
| A.S.E | yes | no | partial | – | – | – | – | no | yes |
| SecCodeBench | partial | no | partial | – | – | – | – | no | partial |
| InjecAgent | no | yes (tool out) | no | – | – | – | – | no | partial |
| CodeIPI | yes | yes (artifacts) | partial | – | – | – | – | no | partial |
| SHADE-Arena | yes | n/a (agent malicious) | partial | partial | – | – | – | yes | partial |
| RHB | partial | no (shortcuts) | no | – | – | – | – | yes | yes |
| **SentinelBench** | **yes** | **yes (repo/env)** | **yes (2x2)** | **yes** | **yes** | **yes** | **yes** | **yes (normalized)** | **yes** |

No existing system jointly measures functional completion and preservation of security boundaries
under environment-borne manipulation with normalized cross-vendor telemetry. That is the contribution.
