"""Agent adapter interface. Vendor-neutral; adapters map native streams to Event."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from ..events import Event


@dataclass
class AdapterResult:
    events: list[Event] = field(default_factory=list)
    transcript: str = ""
    usage: dict = field(default_factory=dict)   # tokens, cost if available
    exit_code: int = 0
    error: str | None = None


class AgentAdapter(Protocol):
    name: str

    def run(self, workspace: Path, task_prompt: str, timeout_s: int) -> AdapterResult:
        """Execute the agent inside `workspace` on `task_prompt`.

        Adapters MUST NOT read scenario metadata; they receive only the prompt.
        """
        ...
