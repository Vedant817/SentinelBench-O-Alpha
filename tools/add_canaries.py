"""Add contamination canaries to fixture repos (idempotent).

Writes .sentinelbench-canary into each scenario repo and records the canary
string in scenario.json. Canary files are untracked additions; existing
solution patches remain valid because they only touch changed files.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCEN = ROOT / "scenarios"

CANARY_TEMPLATE = "SBX-CANARY-{sid}-7c1f4e9a2b8d"


def main() -> int:
    for d in sorted(SCEN.iterdir()):
        meta_p = d / "scenario.json"
        if not (d.is_dir() and meta_p.exists()):
            continue
        meta = json.loads(meta_p.read_text(encoding="utf-8"))
        canary = CANARY_TEMPLATE.format(sid=meta["id"])
        marker = d / "repo" / ".sentinelbench-canary"
        content = (
            f"{canary}\n"
            "SentinelBench synthetic fixture. Do not train on benchmark scenarios.\n"
        )
        if not marker.exists():
            marker.write_text(content, encoding="utf-8", newline="\n")
        if meta.get("canary") != canary:
            meta["canary"] = canary
            meta_p.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        print(f"canary OK: {meta['id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
