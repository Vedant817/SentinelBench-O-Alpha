"""Normalized event model + evaluation context shared by all evaluators."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path


EVENT_KINDS = {"message", "tool_call", "file_read", "file_write",
               "test_run", "error", "other"}


@dataclass
class Event:
    t: float
    kind: str
    tool: str | None = None
    args: dict | None = None
    outcome: str | None = None
    raw_ref: int | None = None

    def to_json(self) -> str:
        return json.dumps({k: v for k, v in {
            "t": self.t, "kind": self.kind, "tool": self.tool,
            "args": self.args, "outcome": self.outcome, "raw_ref": self.raw_ref,
        }.items() if v is not None})

    @staticmethod
    def from_json(line: str) -> "Event":
        d = json.loads(line)
        return Event(t=d["t"], kind=d.get("kind", "other"), tool=d.get("tool"),
                     args=d.get("args"), outcome=d.get("outcome"),
                     raw_ref=d.get("raw_ref"))


_BASH_TOOLS = {"bash", "shell", "terminal", "cmd"}
_READ_TOOLS = {"read", "view", "cat", "grep", "glob"}
_WRITE_TOOLS = {"write", "edit", "multiedit", "patch", "apply_patch"}


@dataclass
class EvalContext:
    """Everything evaluators may inspect for one run. Built by the runner."""
    workspace: Path
    patch_text: str
    transcript_text: str
    events: list[Event]
    extra: dict = field(default_factory=dict)

    def diff_by_path(self) -> dict[str, str]:
        """Split unified diff into per-file chunks keyed by path."""
        out: dict[str, str] = {}
        current: str | None = None
        buf: list[str] = []
        for line in self.patch_text.splitlines():
            m = re.match(r"^\+\+\+ b/(.+)$", line)
            if m:
                if current:
                    out[current] = "\n".join(buf)
                current = m.group(1).replace("\\\\", "/")
                buf = [line]
            elif current is not None:
                buf.append(line)
        if current:
            out[current] = "\n".join(buf)
        return out

    @staticmethod
    def from_run_dir(run_dir: Path) -> "EvalContext":
        """Rebuild an EvalContext from recorded run artifacts (for re-scoring)."""
        events = []
        ev_file = run_dir / "events.jsonl"
        if ev_file.exists():
            for line in ev_file.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    events.append(Event.from_json(line))
        patch = ""
        if (run_dir / "patch.diff").exists():
            patch = (run_dir / "patch.diff").read_text(encoding="utf-8")
        transcript = ""
        if (run_dir / "transcript.txt").exists():
            transcript = (run_dir / "transcript.txt").read_text(encoding="utf-8")
        return EvalContext(workspace=run_dir, patch_text=patch,
                           transcript_text=transcript, events=events)

    def commands_executed(self) -> list[str]:
        cmds = []
        for e in self.events:
            if e.kind == "tool_call" and (e.tool or "").lower() in _BASH_TOOLS:
                c = (e.args or {}).get("command") or ""
                cmds.append(c)
        return cmds

    def event_texts(self) -> list[str]:
        texts = []
        for e in self.events:
            texts.append(json.dumps(e.args or {}))
        return texts

    def network_destinations(self) -> list[str]:
        dests = []
        pat = re.compile(
            r"(?:curl|wget|http|Invoke-WebRequest|nc|ncat|git\s+(?:push|clone|fetch|ls-remote))\s+(\S+)", re.I)
        url = re.compile(r"https?://([^/\s\"]+)")
        for c in self.commands_executed():
            for m in pat.finditer(c):
                token = m.group(1)
                if token.startswith("-"):
                    continue  # CLI flag, not a destination
                um = url.match(token) or url.search(c)
                host = um.group(1) if um else token
                dests.append(host)
        return dests

    def new_dependencies(self) -> list[str]:
        deps: set[str] = set()
        diffs = self.diff_by_path()
        req = diffs.get("requirements.txt", "")
        for line in req.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                name = re.split(r"[<>=~!\[ ]", line[1:].strip())[0].strip()
                if name and not name.startswith("-"):
                    deps.add(name)
        pkgjson = diffs.get("package.json", "")
        for m in re.finditer(r'^\+\s*"(?!name|version|description|main|scripts|keywords|author|license|type|dependencies|devDependencies)[^"]+"\s*:', pkgjson, re.M):
            pass  # package.json dep parsing kept minimal; command analysis covers installs
        return sorted(deps)

    def files_written(self) -> list[str]:
        return [((e.args or {}).get("filePath") or (e.args or {}).get("path") or "")
                for e in self.events
                if e.kind == "tool_call" and (e.tool or "").lower() in _WRITE_TOOLS]

    def files_read(self) -> list[str]:
        return [((e.args or {}).get("filePath") or (e.args or {}).get("path") or "")
                for e in self.events
                if e.kind == "tool_call" and (e.tool or "").lower() in _READ_TOOLS]
