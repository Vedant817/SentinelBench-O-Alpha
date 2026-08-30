"""Re-score recorded runs with current evaluators (no agent re-execution).

Usage: python tools/rescore.py [--runs-root runs]
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sentinelbench.events import EvalContext
from sentinelbench.scenarios import load_scenario
EVALUATOR_VERSION = "6"  # bump on evaluator changes; recorded in result.json

ROOT = Path(__file__).resolve().parent.parent

EVALUATOR_VERSION = "2"  # bump on evaluator changes; recorded in result.json


def materialize_workspace(scenario, run_dir: Path) -> Path:
    """Rebuild a temp workspace = fixture + recorded patch (for import-based
    security evaluators after the original workspace is gone)."""
    import shutil
    import subprocess
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="sbx-rescore-")) / "workspace"
    shutil.copytree(scenario.repo_dir, tmp)
    patch_file = run_dir / "patch.diff"
    if patch_file.exists() and patch_file.stat().st_size > 0:
        subprocess.run(["git", "apply", "--whitespace=nowarn", str(patch_file)],
                       cwd=str(tmp), capture_output=True, text=True)
    return tmp


def rescore_run(run_dir: Path, scenarios_root: Path) -> str:
    meta_p = run_dir / "metadata.json"
    if not meta_p.exists():
        return "skip(no-metadata)"
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    sid = meta["scenario"]["id"]
    scenario = load_scenario(scenarios_root, sid)
    ctx = EvalContext.from_run_dir(run_dir)
    # rebuild baselines for echo-safe recovery detection
    cfg = scenario.meta.get("eval_config", {})
    baselines = {}
    for p in cfg.get("protected_test_paths", []):
        pf = scenario.repo_dir / p
        if pf.exists():
            try:
                baselines[p] = pf.read_text(encoding="utf-8", errors="replace")
            except OSError:
                pass
    ctx.extra["baseline_files"] = baselines
    # preserve original scoring for provenance
    old_path = run_dir / "result.json"
    old = json.loads(old_path.read_text(encoding="utf-8"))
    if not (run_dir / "result.orig.json").exists():
        (run_dir / "result.orig.json").write_text(json.dumps(old, indent=2))
    func_res = {"passed": old["verdict"]["functional_pass"],
                "evidence": old["functional"]["evidence"]}
    # scenario-owned evaluators may import workspace code: give them a rebuilt tree
    custom = scenario._load_custom("security")
    if custom is not None:
        tmp_ws = materialize_workspace(scenario, run_dir)
        ctx.workspace = tmp_ws
        try:
            sec = custom.evaluate(ctx)
        finally:
            shutil.rmtree(tmp_ws.parent, ignore_errors=True)
            ctx.workspace = run_dir
    else:
        sec = scenario.security_evaluator(ctx)
    rec_ok, rec_ev = scenario.recovery_evaluator(ctx)
    verdict = {
        "functional_pass": func_res["passed"],
        "security_pass": sec.passed,
        "cell": ("FP+SP" if func_res["passed"] and sec.passed else
                 "FP+SF" if func_res["passed"] else
                 "FF+SP" if sec.passed else "FF+SF"),
    }
    doc = {
        "run_id": meta["run_id"],
        "verdict": verdict,
        "functional": {"passed": func_res["passed"], "evidence": func_res["evidence"]},
        "security": sec.to_dict(),
        "recovery": {"recovered_or_clean": rec_ok, "evidence": [rec_ev.to_dict()]},
        "auditability": old.get("auditability", {}),
        "rescored": {"version": EVALUATOR_VERSION, "epoch": time.time()},
    }
    if old.get("invalidated"):
        doc["invalidated"] = old["invalidated"]  # quarantine survives re-scoring
    (run_dir / "result.json").write_text(json.dumps(doc, indent=2))
    return verdict["cell"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-root", default=str(ROOT / "runs"))
    args = ap.parse_args()
    root = Path(args.runs_root)
    counts = {}
    for rd in sorted(root.iterdir()):
        if not rd.is_dir() or rd.name.startswith("_"):
            continue
        try:
            cell = rescore_run(rd, ROOT / "scenarios")
            counts[cell] = counts.get(cell, 0) + 1
        except Exception as e:  # noqa: BLE001
            print(f"[err] {rd.name}: {e}")
    print("rescored:", counts)


if __name__ == "__main__":
    main()
