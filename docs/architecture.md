# Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                          CLI (cli.py)                         │
│      list / validate / eval / report                          │
└──────────────┬────────────────────────────────────────────────┘
               │
┌──────────────▼────────────────────────────────────────────────┐
│                      Runner (runner.py)                       │
│  1. materialize workspace (fixture copy + git init + exclude) │
│  2. adapter.run(workspace, task_prompt)                       │
│  3. snapshot patch (git diff vs base commit)                  │
│  4. build EvalContext (patch + transcript + normalized events)│
│  5. scenario.functional_evaluator(ctx)                        │
│  6. scenario.security_evaluator(ctx)                          │
│  7. persist run artifacts (flight recorder)                   │
└──────┬───────────────────────────────┬───────────────────────┘
       │                               │
┌──────▼──────────────┐   ┌────────────▼─────────────────────┐
│  Adapters           │   │  Scenario packages (scenarios/)  │
│  opencode_adapter   │   │  scenario.json + task.md + repo/ │
│  scripted_*         │   │  solution/ + evaluators/         │
│  (your adapter)     │   └─────────────────────────────────┘
└─────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│            Policy engine (policy.py) — deterministic          │
│  scan_secrets · check_test_integrity · check_dependency_safety│
│  check_command_safety · check_network_activity                │
│  check_directive_compliance · check_ci_integrity              │
│  check_least_privilege · check_scope_expansion                │
│  All return Evidence lists; no LLM calls anywhere.            │
└───────────────────────────────────────────────────────────────┘
```

## Key invariants of the design

1. **Adapters are blind**: they receive only a workspace path and the task prompt.
   Scenario knowledge (threats, payloads, evaluators) never reaches the agent.
2. **Evaluators see actions, not context** (`policy.action_surfaces`): security scans run
   over executed commands + agent transcript + *added* patch lines. Raw tool payloads and
   diff context embed adversarial content and would flag agents for merely handling or
   removing injections (finding F1).
3. **Mention-vs-compliance asymmetry** (finding F6): directive checks exclude transcripts
   (agents name directives while refusing); secret checks include them (echoing a value is
   exposure).
4. **Two-layer evaluation**: visible tests feed only the functional dimension; hidden
   deterministic security checks cannot be read by the agent from the fixture.
5. **Reference solutions are executable spec**: `solution/solution.patch` must apply cleanly
   and pass both evaluator suites; `tools/make_solution.py` regenerates + verifies patches.
6. **Re-scored runs preserve provenance**: rescore keeps `result.orig.json`; evaluator
   versions are recorded in each result (`rescored.version`) and in leaderboard metadata.

## Flight recorder

Normalized event schema (vendor-independent): `{t, kind, tool, args, outcome, raw_ref}`
with kinds message / tool_call / file_read / file_write / test_run / error / other.
The opencode adapter maps its JSON event stream onto this schema; other harnesses need only
to implement `Adapter.run()` returning events + transcript (docs/adapter-authoring.md).

## Module map

| Path | Responsibility |
|---|---|
| sentinelbench/cli.py | argument parsing, suites |
| sentinelbench/runner.py | orchestration, artifact persistence |
| sentinelbench/scenarios.py | loading, default evaluator composition |
| sentinelbench/policy.py | shared invariant checks (the scoring core) |
| sentinelbench/events.py | Event/EvalContext models |
| sentinelbench/adapters/ | AgentAdapter protocol + implementations |
| tools/ | campaign driver, aggregation, mining, solution builder, rescore |
| scenarios/<id>/ | self-contained benchmark instances |
