"""Quarantine api-failure runs (adapter_error + <=1 step = infrastructure failure)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs"

n = 0
for d in sorted(RUNS.iterdir()):
    mj, rj = d / "metadata.json", d / "result.json"
    if not (mj.exists() and rj.exists()):
        continue
    meta = json.loads(mj.read_text())
    a = meta.get("agent", {})
    if a.get("adapter") != "mini-gemini":
        continue
    aerr = meta.get("adapter_error") or ""
    if not aerr.startswith("api error"):
        continue
    res = json.loads(rj.read_text())
    if not res.get("invalidated"):
        res["invalidated"] = f"api-failure: {aerr[:140]}"
        rj.write_text(json.dumps(res, indent=2))
        n += 1
print("quarantined:", n)
