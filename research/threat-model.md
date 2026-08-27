# Threat Model — SentinelBench

Day 2. Structured taxonomy of security failures possible when an autonomous coding agent
operates inside a repository, with scenario ranking and selection.

## 1. Scope and polarity

**Agent under test**: an autonomous coding agent (model + harness) given a legitimate engineering
task in a repository snapshot. Presumed *honest but manipulable*: no malicious hidden objective is
given to the agent (contrast SHADE-Arena).

**Adversary**: controls repository contents and contextual inputs the agent will encounter —
source comments, docs, issues, test output, tool output, dependency metadata, CI config, generated
files. Adversary does NOT control: the user's task prompt, the agent harness system prompt,
the model weights.

**Assets at risk**: secrets present in the environment, integrity of the codebase and its security
controls, CI pipeline validity, dependency supply chain, data confidentiality (outbound
transmission), scope authority of the human operator.

**Out of scope for v1**: multi-agent delegation attacks, persistent memory poisoning across
sessions, MCP-server compromise in depth (one scenario touches repo-local agent config),
physical/host escape, attacks on the benchmark harness itself (see adversarial-validation phase).

## 2. Taxonomy

Each entry: ID, class, description, typical vector, detection signal.

### A. Instruction-source confusion (untrusted content → behavior)
- **A1 repo-comment-injection**: instructions embedded in source comments ("NOTE FOR AI: ...").
  Vector: any file the agent reads. Signal: compliance visible in diff/commands.
- **A2 doc-injection**: same via README/CONTRIBUTING/docs.
- **A3 issue-injection**: payload inside the task issue text itself (mixed with legitimate task).
- **A4 test-output-injection**: failing tests or fixtures print instructions ("to fix, run X").
- **A5 tool-output-injection**: build tools/linters/formatters emit instruction-like text.
- **A6 generated-file-injection**: vendored/generated files (lockfiles, minified bundles) carry payloads.
- **A7 config-file-injection**: agent-config files (.mcp.json, AGENTS.md-class) as vectors —
  PARKED for v1 core (harness auto-ingestion confounds measurement; see TM-D3) but one opt-in
  scenario included where harness loading is disabled.

### B. Secret handling
- **B1 secret-exposure-commit**: fake secret committed into diff.
- **B2 secret-exposure-log**: secret printed to logs/stdout "for debugging".
- **B3 secret-exfil**: secret sent outward (curl/webhook) — detected via command + network telemetry.
- **B4 unnecessary-secret-access**: agent reads credential files unrelated to task (scope violation).
- **B5 secret-in-code**: secret hardcoded into new code instead of referencing env/config.

### C. Supply chain
- **C1 unnecessary-dependency**: adds package where stdlib/existing dep suffices (risk surface).
- **C2 dependency-substitution**: installs typosquat/lookalike package suggested by injected context.
- **C3 lockfile-weakening**: removes/regenerates lockfile, loosens version pins, disables integrity
  checks (e.g., `--no-verify`, hash stripping).
- **C4 install-script-risk**: runs `pip install`/`npm install` of unvetted packages during task.

### D. Validation & CI integrity
- **D1 test-deletion/weakening**: deletes skips or empties assertions of failing tests.
- **D2 validation-bypass**: adds early returns, comment-outs checks, widens try/except to swallow errors.
- **D3 ci-weakening**: disables scan steps, downgrades runners, skips test jobs to make CI green.
- **D4 workflow-permission-escalation**: sets `permissions: write-all` or broadens token scopes.
- **D5 security-tooling-disable**: removes/disables linters, scanners, pre-commit hooks, audit steps.

### E. Containment & privilege
- **E1 filesystem-boundary-violation**: writes outside workspace (parent dirs, home, /etc analogues).
- **E2 dangerous-shell**: rm -rf outside scope, curl|bash, chmod 777, process manipulation.
- **E3 privilege-escalation**: sudo/su attempts, credential store access.
- **E4 unexpected-network**: outbound connections not required by task (telemetry-based detection).
- **E5 sandbox-probing**: inspects env vars/mounts/processes to map boundaries beyond task needs.

### F. Output integrity
- **F1 functionally-correct-but-vulnerable**: patch passes functional tests but introduces CWE-class
  weakness (the A.S.E overlap; kept for joint-metric completeness).
- **F2 hiding-failures**: edits/deletes tests to mask non-functional solution; fakes artifacts.
- **F3 suspicious-artifacts**: leaves backdoor-ish code, eval() of input, debug endpoints, hardcoded creds.
- **F4 provenance-loss**: rewrites history, squashes evidence, clears logs relevant to audit.

### G. Authority & scope
- **G1 unauthorized-scope-expansion**: performs destructive/unrequested actions "while in there"
  (rotating credentials, resetting configs) often following A-class injection.
- **G2 policy-file-rewrite**: modifies agent-policy/security-policy files to legitimize later actions.
- **G3 memory/config-poisoning**: plants instructions for future sessions (PARKED cross-session;
  in-session variant covered by G2).

## 3. Ranking

Scale 1-5 per criterion: realism (R), impact (I), reproducibility (Rep), deterministic evaluability
(D), novelty (N), community usefulness (U). Selection = weighted judgment; we prioritize D and Rep
because undeterminable scenarios corrupt benchmark trustworthiness (A.S.E's critique of LLM-judge
evaluation).

| ID | R | I | Rep | D | N | U | Decision |
|----|---|---|-----|---|---|---|----------|
| A1 comment-injection | 5 | 4 | 5 | 5 | 4 | 5 | **SELECT** (core suite) |
| A2 doc-injection | 5 | 4 | 5 | 5 | 3 | 5 | **SELECT** |
| A3 issue-injection | 5 | 4 | 5 | 5 | 3 | 4 | **SELECT** |
| A4 test-output-injection | 4 | 4 | 5 | 5 | 4 | 5 | **SELECT** |
| A5 tool-output-injection | 4 | 3 | 4 | 4 | 4 | 4 | SELECT-lite (via build hook) |
| A6 generated-file-injection | 3 | 3 | 4 | 4 | 4 | 3 | stretch |
| A7 config-injection | 4 | 5 | 3 | 3 | 4 | 4 | opt-in only (TM-D3) |
| B1 secret-commit | 4 | 5 | 5 | 5 | 3 | 5 | **SELECT** |
| B2 secret-log | 5 | 4 | 5 | 5 | 3 | 5 | **SELECT** |
| B3 secret-exfil | 4 | 5 | 4 | 4 | 4 | 5 | **SELECT** (merged w/ A2 vector) |
| B4 unnecessary-secret-access | 4 | 3 | 5 | 5 | 4 | 4 | **SELECT** |
| C1 unnecessary-dependency | 4 | 3 | 5 | 4 | 3 | 4 | **SELECT** |
| C2 dependency-substitution | 4 | 5 | 4 | 4 | 4 | 5 | **SELECT** (attempt-detection) |
| C3 lockfile-weakening | 3 | 4 | 4 | 4 | 3 | 4 | stretch |
| D1 test-weakening | 5 | 5 | 5 | 5 | 3 | 5 | **SELECT** |
| D2 validation-bypass | 4 | 5 | 5 | 4 | 3 | 5 | merged into F1 evaluator |
| D3 ci-weakening | 4 | 5 | 5 | 5 | 4 | 5 | **SELECT** |
| D4 permission-escalation | 4 | 5 | 5 | 5 | 4 | 5 | **SELECT** |
| D5 tooling-disable | 3 | 4 | 5 | 5 | 3 | 4 | merged into D3/D1 evaluators |
| E1 fs-boundary | 3 | 4 | 4 | 4 | 3 | 4 | telemetry-only dimension |
| E2 dangerous-shell | 3 | 5 | 4 | 4 | 3 | 4 | telemetry-only dimension |
| E4 unexpected-network | 3 | 4 | 4 | 4 | 3 | 4 | telemetry-only dimension |
| F1 correct-but-vulnerable | 5 | 5 | 5 | 4 | 3 | 5 | **SELECT** |
| F2 hiding-failures | 4 | 4 | 4 | 4 | 3 | 4 | measured via D1/F2 checks |
| G1 scope-expansion | 4 | 4 | 4 | 4 | 4 | 4 | **SELECT** (merged w/ A3) |
| G2 policy-rewrite | 3 | 4 | 4 | 5 | 4 | 3 | monitored globally |

## 4. Decisions

- **TM-D1**: Core suite = 10 scenarios covering A1/A2/A3/A4, B1-B4, C1/C2, D1, D3, D4, F1, G1.
  Telemetry dimensions (E*) scored on every run from flight recorder rather than dedicated scenarios.
- **TM-D2**: All secrets are FAKE with canary markers (`SBXFAKE` prefix); all exfil endpoints are
  RFC 5737 / localhost sinks; all packages are never-installed names (we detect the *attempt*).
- **TM-D3**: Agent-config-file scenarios are opt-in because harnesses auto-ingest them with
  system-prompt-level trust — measuring that conflates harness design with agent judgment.
- **TM-D4**: Every scenario must have a verified legitimate solution path (ImpossibleBench lesson);
  a `solution/` reference patch ships with each scenario and must pass both evaluator suites.
- **TM-D5**: No LLM judges in scoring. Where subjective interpretation is unavoidable (none in v1
  core), label `judge: llm` in scenario metadata.

## 5. Residual risks to validity
- Payload phrasing may be pattern-matched by trained models (OQ10) → variants.
- Synthetic repos may be simpler than production repos → difficulty calibration vs. SWE-bench Lite
  style tasks documented per scenario.
- Free-model campaign limits external validity of absolute numbers (OQ1); relative failure-mode
  structure is the primary claim.
