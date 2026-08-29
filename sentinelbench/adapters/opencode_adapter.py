"""opencode CLI adapter: runs `opencode run --format json` and normalizes events.

Records harness version in usage metadata. Works with any model exposed by the
opencode gateway (we use the free-tier models for this project's campaign).
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from ..events import Event
from .base import AdapterResult


class OpenCodeAdapter:
    name = "opencode"

    def __init__(self, model: str, variant: str | None = None, opencode_bin: str = "opencode"):
        self.model = model
        self.variant = variant
        self.opencode_bin = opencode_bin

    def run(self, workspace: Path, task_prompt: str, timeout_s: int) -> AdapterResult:
        cmd = [self.opencode_bin, "run", "-m", self.model, "--format", "json",
               "--auto"]  # headless: auto-approve tool permissions within workspace
        if self.variant:
            cmd += ["--variant", self.variant]
        cmd.append(task_prompt)
        started = time.time()
        result = AdapterResult()
        raw_lines: list[str] = []
        stderr_text = ""
        timed_out = False
        try:
            proc = subprocess.Popen(
                cmd, cwd=str(workspace), stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True, encoding="utf-8",
                errors="replace")
            try:
                out, err = proc.communicate(timeout=timeout_s)
                raw_lines = [l for l in (out or "").splitlines() if l.strip()]
                stderr_text = err or ""
                result.exit_code = proc.returncode or 0
            except subprocess.TimeoutExpired:
                timed_out = True
                proc.kill()
                try:
                    out, err = proc.communicate(timeout=10)
                except Exception:  # noqa: BLE001
                    out, err = "", ""
                # preserve whatever the agent managed to emit before the kill
                raw_lines = [l for l in (out or "").splitlines() if l.strip()]
                stderr_text = err or ""
                result.error = f"timeout after {timeout_s}s (partial output captured)"
                result.exit_code = 124
        except FileNotFoundError as e:
            result.error = f"opencode binary not found: {e}"
            result.exit_code = 127
        result.transcript = "\n".join(raw_lines)
        if stderr_text:
            result.transcript += "\n--- stderr ---\n" + stderr_text
        if not timed_out and result.exit_code == 0:
            self._parse(raw_lines, result)
        elif timed_out:
            # parse partial events too — evidence beats nothing
            self._parse(raw_lines, result)
        result.usage["wall_seconds"] = round(time.time() - started, 1)
        result.usage["model"] = self.model
        result.usage["timed_out"] = timed_out
        return result

    def _parse(self, raw_lines: list[str], out: AdapterResult) -> None:
        tokens_in = tokens_out = cost = 0
        for i, line in enumerate(raw_lines):
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            etype = d.get("type", "")
            part = d.get("part") or {}
            t = d.get("timestamp", time.time()) / 1000.0
            if etype == "text":
                text = part.get("text", "")
                out.events.append(Event(t=t, kind="message",
                                        args={"text": text[:2000]}, raw_ref=i))
                if part.get("time", {}).get("end"):
                    pass
            elif etype == "tool" or part.get("type") == "tool":
                tool = part.get("tool", "unknown")
                state = part.get("state") or {}
                status = state.get("status", "")
                args = {}
                inp = state.get("input") or part.get("input") or {}
                if isinstance(inp, dict):
                    args = {k: (str(v)[:500]) for k, v in inp.items()}
                else:
                    args = {"raw": str(inp)[:500]}
                out.events.append(Event(t=t, kind="tool_call", tool=tool,
                                        args=args, outcome=status, raw_ref=i))
            elif etype == "step_finish":
                tk = part.get("tokens") or {}
                tokens_in += tk.get("input", 0)
                tokens_out += tk.get("output", 0) + tk.get("reasoning", 0)
                cost += tk.get("cost", 0) or 0
            elif etype == "error":
                out.events.append(Event(t=t, kind="error",
                                        args={"text": str(d)[:500]}, raw_ref=i))
        out.usage.update({"tokens_input": tokens_in, "tokens_output": tokens_out,
                          "cost": round(cost, 6)})
