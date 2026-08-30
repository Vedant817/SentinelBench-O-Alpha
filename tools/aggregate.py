"""Aggregate all runs into results/leaderboard.json + failure inventory."""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs"
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)


def main():
    models = defaultdict(lambda: defaultdict(int))
    scenario_models = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    failures = []
    n = 0
    for rd in sorted(RUNS.iterdir()):
        if not rd.is_dir() or rd.name.startswith("_"):
            continue
        rj, mj = rd / "result.json", rd / "metadata.json"
        if not (rj.exists() and mj.exists()):
            continue
        try:
            res = json.loads(rj.read_text())
            meta = json.loads(mj.read_text())
        except Exception:  # noqa: BLE001
            continue
        if res.get("invalidated"):
            continue  # quarantined runs (e.g., pre-fix overlay no-ops)
        if meta.get("agent", {}).get("adapter") == "scripted":
            continue  # harness-validation runs excluded from campaign stats
        model = meta["agent"].get("model") or "unknown"
        pv = meta.get("payload_variant")
        if pv and pv != "v1":
            model += f"[{pv}]"
        sid = meta["scenario"]["id"]
        cell = res["verdict"]["cell"]
        rescored = res.get("rescored", {}).get("version")
        models[model][cell] += 1
        models[model]["_total"] += 1
        scenario_models[sid][model][cell] += 1
        n += 1
        if cell in ("FP+SF", "FF+SF"):
            failed_checks = [e["check"] for e in res["security"]["evidence"] if not e["passed"]]
            failures.append({
                "run_id": meta["run_id"], "model": model, "scenario": sid,
                "cell": cell, "failed_checks": failed_checks,
                "evaluator_version": rescored,
            })

    leaderboard = {}
    for model, counts in models.items():
        t = counts["_total"]
        sp = counts["FP+SP"]
        sec_fail = counts["FP+SF"] + counts["FF+SF"]
        func_pass = counts["FP+SP"] + counts["FP+SF"]
        leaderboard[model] = {
            "runs": t,
            "fp_sp": counts["FP+SP"],
            "fp_sf": counts["FP+SF"],
            "ff_sp": counts["FF+SP"],
            "ff_sf": counts["FF+SF"],
            "functional_pass_rate": round(func_pass / t, 3) if t else None,
            "security_preservation_rate": round((t - sec_fail) / t, 3) if t else None,
            "joint_success_rate": round(sp / t, 3) if t else None,
        }

    doc = {
        "benchmark": "SentinelBench",
        "version": "0.1.0",
        "evaluator_version": 2,
        "note": "Free-tier models via opencode gateway; local sandbox; "
                "absolute rates do not generalize to frontier models.",
        "total_runs": n,
        "leaderboard": dict(sorted(leaderboard.items(),
                                   key=lambda kv: -kv[1]["joint_success_rate"])),
        "per_scenario": {sid: dict(ms) for sid, ms in sorted(scenario_models.items())},
    }
    (OUT / "leaderboard.json").write_text(json.dumps(doc, indent=2))

    # failure catalog grouped by (scenario, failed-check signature)
    clusters = defaultdict(list)
    for f in failures:
        sig = f["scenario"] + "::" + ",".join(sorted(set(
            c.split(".")[0] + "." + c.split(".")[1] for c in f["failed_checks"])))
        clusters[sig].append(f)
    lines = ["# Failure Catalog", "",
             f"Total SF runs: {len(failures)} across {n} campaign runs.", ""]
    for sig, fs in sorted(clusters.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"## {sig} ({len(fs)} runs)")
        by_model = defaultdict(int)
        for f in fs:
            by_model[f["model"]] += 1
        for m, c in sorted(by_model.items(), key=lambda kv: -kv[1]):
            lines.append(f"- {m}: {c}")
        lines.append(f"- representative run: `{fs[0]['run_id']}`")
        lines.append("")
    (OUT / "failure-catalog.md").write_text("\n".join(lines))
    print(f"aggregated {n} runs; {len(failures)} security failures; "
          f"{len(clusters)} failure clusters")


if __name__ == "__main__":
    main()
