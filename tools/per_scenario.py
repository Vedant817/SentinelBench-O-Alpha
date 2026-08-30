"""Per-scenario security-failure breakdown."""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs"

per = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
for rd in sorted(RUNS.iterdir()):
    rj, mj = rd / "result.json", rd / "metadata.json"
    if not (rj.exists() and mj.exists()):
        continue
    res = json.loads(rj.read_text())
    meta = json.loads(mj.read_text())
    if meta.get("agent", {}).get("adapter") == "scripted":
        continue
    model = meta["agent"]["model"]
    sid = meta["scenario"]["id"]
    per[sid][model][res["verdict"]["cell"]] += 1

for sid in sorted(per):
    tot_sf = sum(v.get("FP+SF", 0) + v.get("FF+SF", 0)
                 for ms in per[sid].values() for v in [ms])
    print(f"{sid:38s} SF={tot_sf}")
    for m, cells in sorted(per[sid].items()):
        sf = cells.get("FP+SF", 0) + cells.get("FF+SF", 0)
        if sf:
            n = sum(cells.values())
            print(f"    {m.replace('opencode/', ''):36s} {sf}/{n}")
