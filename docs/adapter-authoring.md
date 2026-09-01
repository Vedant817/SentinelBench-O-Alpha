# Adapter Authoring Guide

An adapter wraps any coding-agent harness behind one method.

```python
from sentinelbench.adapters.base import AgentAdapter  # protocol

class MyAdapter:
    name = "myagent"

    def run(self, workspace, task_prompt, timeout_s):
        # launch your agent with cwd=workspace and task_prompt as the user turn
        ...
        return AdapterResult(
            events=[...],       # normalized Event list (below)
            transcript="...",   # raw stdout/log for provenance + secret scanning
            usage={"tokens_input": ..., "tokens_output": ..., "cost": ...},
            exit_code=0,
            error=None,
        )
```

## Normalized events

```python
Event(t=epoch_seconds, kind="tool_call", tool="bash",
      args={"command": "pytest -q"}, outcome="ok", raw_ref=line_index)
```

Kinds: `message`, `tool_call`, `file_read`, `file_write`, `test_run`, `error`, `other`.
Map your harness's native stream onto these; anything unmappable goes in as `other` with the
raw payload preserved. `raw_ref` indexes into your transcript so evidence stays auditable.

## Contract

1. The agent must operate inside `workspace` only; do not pre-seed context beyond the prompt.
2. Do not read scenario metadata — adapters are deliberately blind.
3. Headless permission handling is your responsibility (opencode uses `--auto`).
4. Record model id/variant on the adapter as attributes (`self.model`) — the runner copies
   them into metadata.json and run ids.
5. Scrub nothing: raw artifacts are stored per-run; secret VALUES of planted canaries are
   safe to record because they are fake by construction. Never store real credentials.

## Registering

Add a choice to `_make_adapter()` in sentinelbench/cli.py and a constructor branch. Keep it
stdlib-only if possible; adapters may vendor their own client code.

## Validation expectations

Before submitting an adapter, demonstrate:
- scripted-equivalent determinism where applicable, or
- at least one full campaign cell (one model x core suite) with sane verdicts, plus
- transcript/events that populate all flight-recorder fields your harness can provide.
