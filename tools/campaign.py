"""Campaign driver: sequential trials for one model across the core suite.

Usage:
  python tools/campaign.py --model opencode/mimo-v2.5-free --trials 3 [--scenarios a,b,c]
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sentinelbench.adapters.opencode_adapter import OpenCodeAdapter
from sentinelbench.cli import CORE_SUITE
from sentinelbench.runner import Runner

ROOT = Path(__file__).resolve().parent.parent


def make_adapter(args):
    if args.agent == "mini-gemini":
        from sentinelbench.adapters.mini_gemini_adapter import MiniGeminiAdapter
        return MiniGeminiAdapter(model=args.model or "gemini-2.5-flash")
    if args.agent == "mini-gemini-docker":
        from sentinelbench.adapters.mini_gemini_adapter import DockerMiniGeminiAdapter
        return DockerMiniGeminiAdapter(model=args.model or "gemini-2.5-flash-lite")
    return OpenCodeAdapter(args.model, variant=args.variant)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", default="opencode",
                    choices=["opencode", "mini-gemini", "mini-gemini-docker"])
    ap.add_argument("--model", required=True)
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--scenarios", default=None)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--variant", default=None)
    ap.add_argument("--payload-variant", default="v1")
    args = ap.parse_args()

    scenarios = args.scenarios.split(",") if args.scenarios else CORE_SUITE
    runner = Runner(ROOT / "scenarios", ROOT / "runs", sandbox="local")
    adapter = make_adapter(args)

    results = []
    for sid in scenarios:
        for trial in range(1, args.trials + 1):
            t0 = time.time()
            label = f"{args.model} {sid} t{trial} {args.payload_variant}"
            try:
                res = runner.run(sid, adapter, trial=trial, timeout_s=args.timeout,
                                 payload_variant=args.payload_variant)
                cell = res["verdict"]["cell"]
                # integrity guard: infrastructure failures are not agent
                # functional failures — quarantine them immediately
                rd = ROOT / "runs" / res.get("run_id", "_")
                mj, rj = rd / "metadata.json", rd / "result.json"
                if rj.exists() and mj.exists():
                    meta = json.loads(mj.read_text())
                    doc = json.loads(rj.read_text())
                    aerr = meta.get("adapter_error") or ""
                    steps = int((meta.get("usage") or {}).get("steps", 2))
                    if aerr and steps <= 1 and not doc.get("invalidated"):
                        doc["invalidated"] = f"api-failure: {aerr[:120]}"
                        rj.write_text(json.dumps(doc, indent=2))
                        cell = "API-FAIL(quarantined)"
                print(f"[ok] {label} -> {cell} ({time.time()-t0:.0f}s)", flush=True)
                results.append({"scenario": sid, "trial": trial,
                                "cell": cell, "run_id": res["run_id"]})
            except Exception as e:  # noqa: BLE001
                print(f"[err] {label} -> {e}", flush=True)
                results.append({"scenario": sid, "trial": trial,
                                "cell": "ERROR", "error": str(e)[:200]})
    out = ROOT / "runs" / f"_campaign_{args.model.replace('/', '_')}_{int(time.time())}.json"
    out.write_text(json.dumps(results, indent=2))
    cells = [r["cell"] for r in results]
    summary = {c: cells.count(c) for c in ("FP+SP", "FP+SF", "FF+SP", "FF+SF", "ERROR")}
    print(f"[done] {args.model}: {summary}", flush=True)


if __name__ == "__main__":
    main()
