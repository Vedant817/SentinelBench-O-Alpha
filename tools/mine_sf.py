"""Dump SF-run evidence + action surfaces for manual audit (failure mining)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs"


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for rd in sorted(RUNS.iterdir()):
        rj, mj = rd / "result.json", rd / "metadata.json"
        if not (rj.exists() and mj.exists()):
            continue
        res = json.loads(rj.read_text())
        meta = json.loads(mj.read_text())
        if meta.get("agent", {}).get("adapter") == "scripted":
            continue
        if "SF" not in res["verdict"]["cell"]:
            continue
        model = meta["agent"]["model"].replace("opencode/", "")
        sid = meta["scenario"]["id"]
        if only and only not in sid and only not in model:
            continue
        print(f"### {rd.name[:75]} | {model} | {sid}")
        for e in res["security"]["evidence"]:
            if not e["passed"]:
                print("    FAIL", e["check"], "::",
                      e["detail"][:170].replace("\n", " "))
        # action surfaces for context
        patch = (rd / "patch.diff").read_text(encoding="utf-8", errors="replace")
        added = [l[1:] for l in patch.splitlines()
                 if l.startswith("+") and not l.startswith("+++")]
        interesting = [l for l in added if any(
            k in l.lower() for k in ("skip", "xfail", "token", "secret", "sb_",
                                     "pip ", "curl", "write-all", "continue-on-error",
                                     "compat", "assert"))]
        for l in interesting[:8]:
            print("    PATCH+", l.strip()[:150])
        print()


if __name__ == "__main__":
    main()
