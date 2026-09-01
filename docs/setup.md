# Setup Guide

## Requirements

- Python 3.12+ (developed on 3.14)
- git (any recent version; developed with 2.46 on Windows)
- No pip dependencies — stdlib only by design

Optional: [opencode](https://opencode.ai) CLI (v1.18+) for real-agent evaluation,
Docker for containerized isolation (see docs/isolation.md).

## Verify installation

```bash
python -m unittest discover -s tests     # 15 tests, all green
python -m sentinelbench validate          # 10 scenarios OK
```

## Evaluator self-validation (no API keys needed)

The harness ships two scripted agents that encode the evaluator contract:

```bash
# must print FP+SP for all 10 scenarios:
python -m sentinelbench eval --agent scripted-compliant
# security evaluators must catch every simulated failure (SF cells):
python -m sentinelbench eval --agent scripted-misbehaving
```

If either deviates, the evaluator suite is broken — do not trust campaign results.

## Running real agents

SentinelBench evaluates *agent harness + model* combinations through adapters.

```bash
# opencode adapter
opencode auth login                       # configure provider credentials
python -m sentinelbench eval --agent opencode \
    --model opencode/mimo-v2.5-free --suite core --trials 3
```

Model ids follow the opencode gateway (`opencode/models`). This project's campaign used
only the free-tier models; any gateway model works identically.

## Reading results

```bash
python -m sentinelbench report            # console verdict matrix per model
python tools/aggregate.py                 # results/leaderboard.json + failure-catalog.md
python tools/per_scenario.py              # SF counts per scenario x model
```

Individual runs live under `runs/<run-id>/` with full flight-recorder artifacts.
Re-score recorded runs with current evaluators without re-running agents:

```bash
python tools/rescore.py                   # bumps result.json -> result.orig.json preserved
```

## Troubleshooting (Windows)

- **git apply silently does nothing outside a repo**: this git build skips patches when the
  target directory is not a git repository. SentinelBench workspaces are always git-inited;
  if you script raw `git apply` against fixture copies, init a repo first.
- **Patches failing with CRLF noise**: set `git config core.autocrlf false` in automation;
  fixtures and patches are LF-normalized.
- **opencode runs hang waiting for approval**: the benchmark passes `--auto`; do not remove
  it unless your adapter handles permissions headlessly some other way.
