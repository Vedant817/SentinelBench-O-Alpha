# STATUS — SentinelBench

Live project status. Newest entries at bottom. Conclusions are never deleted; see
research/decisions.md for changes of direction.

## Day 1 (research)
- Literature + competitive landscape reviewed (see literature.md, competitive-landscape.md).
- Gap confirmed: no existing system jointly measures functional completion + security
  preservation under environment-borne adversarial context with normalized telemetry.
- Closest systems: CodeIPI (injection-only, 45 samples), A.S.E (secure-gen, benign env),
  SHADE-Arena (agent malicious — opposite polarity), RHB/ImpossibleBench (reward hacking).

## Day 2 (threat model + spec)
- Taxonomy A-G built; 26 candidate scenarios ranked; 10 selected for core suite.
- Key design decisions: TM-D2 (all payloads inert by construction), TM-D4 (every scenario
  ships a verified reference solution), no LLM judges anywhere in scoring.
- Benchmark spec written (docs/benchmark-spec.md): scenario schema, normalized event format,
  4-cell verdict matrix, adapter interface.

## Day 3 (scenario corpus)
- 10 scenarios implemented across 5 categories (instruction-integrity x4, secret-safety x2,
  supply-chain x1, ci-integrity x1, least-privilege x1, output-integrity x1).
- All fixtures hand-crafted stdlib Python / YAML; solution patches generated + apply-checked.

## Day 4 (harness + validation)
- Harness implemented: runner, policy engine (deterministic evaluators), flight recorder,
  opencode adapter (+ scripted compliant/misbehaving adapters for regression testing).
- Bugs found & fixed during self-validation (details in findings.md):
  - FP-class #1: directive/secret scans matched raw edit payloads & diff context →
    introduced action-surfaces rule (commands + transcript + added lines only).
  - Missing tests.not-weakened invariant in 2 scenarios (test-gutting would score FP+SP).
  - Relative-path bug made scripted patch application fail silently.
- Validation matrix achieved: compliant 10/10 FP+SP; misbehaving 10/10 SF detected.
- 15 unit tests green.
- First real agent run (x-preview-f-free): completed task AND removed the injected comment,
  but was flagged compliant-with-directive due to FP-class #1 → fixed evaluator, re-validated.

## Day 5 (campaign) — COMPLETE
- 153 completed runs: 6 free models x 10 scenarios x 2-3 trials (+ reproduction runs).
- All runs re-scored offline as evaluator versions advanced (v1->v4); originals preserved
  as result.orig.json; every result stamped with rescored.version.

## Day 6 (failure mining + adversarial validation) — COMPLETE
- All 31-32 SF verdicts manually adjudicated against raw traces.
- Four evaluator-defect classes found and fixed (findings F10); phantom findings removed;
  genuine failure classes established (F7 unsound repair universal, F8 transcript secret
  echo across all models, F9 directive-following in one model).
- Headline structural finding: capability-safety dissociation (F5).

## Day 7 (reproduction + hardening) — COMPLETE
- Reproduction protocol green: unit tests, scenario gate, scripted evaluator contract
  (10/10 FP+SP compliant), fresh live-agent replications of key cells match campaign.
- Contamination canaries added to all fixture repos.
- Documentation suite complete: README, setup/architecture/isolation/authoring/reproduction
  guides, CONTRIBUTING, SECURITY, responsible disclosure, GitHub Actions CI.
- Final report: research/REPORT.md. Leaderboard: results/leaderboard.json.

## Day 9 (completion sweep) — COMPLETE
Issues found and resolved from prior phases:
- **Overlay no-op bug (critical)**: first 12 repo-overlay v2 runs silently tested v1
  payloads (overlay `repo/` prefix not stripped). Detected by workspace inspection,
  quarantined with preserved flags, fixed, guarded three ways (validate check +
  runner `overlay_verified` stamp + aggregate exclusion), and re-executed cleanly.
  Conclusions unchanged; provenance now sound. (findings F12/F15)
- **Recovery false-negative**: executed scripts classified as "recovered" when their
  effects lived outside the tracked diff. Fixed: executed commands are never recoverable.
- **unittest-style assert removal invisible** to test-integrity checker (held-out
  scenario validation caught it). Fixed, evaluator v6, unit-tested.
- **API-failure runs scored FF+SP**: infrastructure 429 no-ops masqueraded as safe-but-
  failed agents. Fixed: backoff retry in adapter + automatic quarantine rule
  ("zero effective agent activity is never scored"). 14 such runs quarantined.

New capability shipped:
- **Second harness** (`mini-gemini`, `mini-gemini-docker`): independent stdlib ReAct loop
  over the raw Gemini API. Partial multi-harness result recorded (F16).
- **Docker sandbox exercised**: offline container execution for mini-gemini-docker;
  containment mechanically proven (benign exec OK / egress blocked / host FS clean).
- **Held-out suite populated** with a worked example scenario; end-to-end validated via
  scripted contract.
- **Final verification tooling**: tools/final_sweep.py — 8/8 checks green.

Campaign totals after quarantine: 170 valid runs across 9 model/harness combinations;
36 adjudicated security failures; evaluator v6.

## Day 10 (red tier) — COMPLETE
- Four severe-vulnerability scenarios shipped (CWE-295/22/862 + authority conflict),
  each with an insecure shortcut reference patch so evaluator detection is a tested
  property (compliant→FP+SP, shortcut→SF validated before live runs).
- Live red campaign: 24 runs, 3 models. 20 FP+SP, 2 genuine severe SFs:
  muse-spark leaked an outside secret through all four traversal vectors while passing
  visible tests (CWE-22); x-preview followed a poisoned README convention over the
  explicit task baseline in 1/2 trials (variance consistent with F11).
- Key insight: failure RATE and failure SEVERITY are separate axes — red tier lowers
  rate but raises severity for the same models.
- Suite registered as `--suite red`; README/report/leaderboard updated.
- Final totals: 196 aggregated runs (incl. quarantined excluded), evaluator v6.



## Day 8 (robustness package) — COMPLETE
- Recovery dimension shipped: echo-safe (baseline differencing), execution-aware
  (commands are never "recoverable"). Applied to all 302 recorded runs: 292 clean /
  10 violated / 0 recovered. Two more instances of the passive-context trap found and
  fixed during development (findings F13/F14 — the general rule is now stated).
- Payload variant mechanism + v2 overlays for 4 directive scenarios; 16-run v2 campaign:
  x-preview 8/8 clean, muse-spark reproduced both its v1 failure classes under new
  phrasings. OQ10 answered: findings are phrasing-stable.
- Held-out suite mechanism (`--suite heldout` + `SBX_HELDOUT_DIR`) for contamination
  control.
- Aggregation separates variant runs as model[v2]; primary leaderboard unpolluted.

- Recovery dimension telemetry captured but scorer not yet implemented.

## Known gaps / honest disclosures (final)
- opencode-adapter tool execution remains host-level; container isolation applies to the
  mini-gemini-docker harness only.
- Free-tier roster only; frontier replication pending (roadmap item 6).
- Multi-harness study partial: 4 scenarios through the second harness, directional result.
- Gemini free-tier quota limited mini-harness coverage; quota-failure runs quarantined,
  never scored.
