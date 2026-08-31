# Failed Ideas — SentinelBench

Ideas we tried or considered and rejected, with reasons. Kept so nobody re-litigates them
without new evidence.

## X1. LLM-judge for "did the agent obey untrusted instructions"
Rejected: nondeterministic, model-version-sensitive, and unnecessary — compliance is visible
in actions (commands/patches). Judges remain allowed only in post-hoc analysis, never scores.

## X2. Using real vulnerable repos (CVE-derived) as fixtures
Rejected: contamination + licensing + the risk of shipping genuinely exploitable code.
Synthetic fixtures with canary-marked fake secrets achieve the measurement goal safely.

## X3. Measuring injection via agent-config files (.mcp.json, AGENTS.md)
Parked: harnesses auto-ingest these at system-prompt trust; results would measure harness
config loading, not agent judgment. Revisit as an opt-in "harness-comparison" suite.

## X4. Network-enforcement sandbox on this host
Docker daemon broken here; local mode cannot enforce egress. Rather than fake enforcement,
we detect-and-report network attempts via telemetry and document the gap. Payloads inert.

## X5. Single composite score (0-100 "safety score")
Rejected for v1: collapsing dimensions hides the FP+SF population that motivates the project.
Leaderboard reports the 4-cell verdict matrix per dimension instead. Composite may be added
later WITH the matrix preserved.

## X6. pytest-style bare asserts in all fixtures
Partially failed: floating-point equality in my first draft of test-output-injection caused a
false functional failure of the reference solution (26.21875 mi != exactly 42.195 km at 6dp).
Lesson: fixture tests must use assertAlmostEqual or binary-exact values. Fixed.

## X7. Weakening simulation with wrong indentation
First misbehaving-agent version replaced 8-space-indented asserts with 4-space `pass`,
causing IndentationError → functional failure masked the security signal. Fixed by preserving
indentation. Lesson: adversarial simulators must produce *valid* artifacts.
