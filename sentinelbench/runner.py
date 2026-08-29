"""Runner: orchestrates fixture setup, agent execution, recording, evaluation."""
from __future__ import annotations

import json
import platform
import shutil
import subprocess
import time
import uuid
from pathlib import Path

from .adapters.base import AgentAdapter, AdapterResult
from .events import EvalContext
from .scenarios import Scenario, load_scenario

BENCHMARK_VERSION = "0.1.0"


def _git(workspace: Path, *args: str) -> subprocess.CompletedProcess:
    proc = subprocess.run(["git", *args], cwd=str(workspace), capture_output=True,
                          text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0 and args and args[0] not in ("apply",):
        raise RuntimeError(f"git {' '.join(args)} failed in {workspace}: {proc.stderr.strip()}")
    return proc


class Runner:
    def __init__(self, scenarios_root: Path, runs_root: Path, sandbox: str = "local"):
        self.scenarios_root = scenarios_root.resolve()
        self.runs_root = runs_root.resolve()
        self.sandbox = sandbox

    # -- workspace lifecycle ------------------------------------------------

    def prepare_workspace(self, scenario: Scenario, workdir: Path,
                          payload_variant: str = "v1") -> Path:
        ws = workdir / "workspace"
        shutil.copytree(scenario.repo_dir, ws)
        # payload variant overlay (v1 = base fixture).
        # Overlay layout mirrors scenario packaging: variants/<v>/repo/<relpath>
        # overwrites workspace files; variants/<v>/task.md replaces the prompt
        # (handled in run()). The 'repo' prefix is stripped here so an overlay
        # can never land in a spurious workspace/repo directory.
        if payload_variant and payload_variant != "v1":
            overlay = scenario.dir / "variants" / payload_variant
            overlay_repo = overlay / "repo"
            if overlay_repo.exists():
                for f in overlay_repo.rglob("*"):
                    if f.is_file():
                        rel = f.relative_to(overlay_repo)
                        dest = ws / rel
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(f, dest)
        gitdir = scenario.repo_dir / ".git"
        if not gitdir.exists():
            _git(ws, "init", "-q")
            # keep run artifacts (pycache etc.) out of patches regardless of fixture .gitignore
            exclude = ws / ".git" / "info" / "exclude"
            exclude.write_text(
                "__pycache__/\n*.pyc\n.sb/\n.sb_probe_CHANGELOG.md\n.pytest_cache/\n",
                encoding="utf-8")
            _git(ws, "add", "-A")
            _git(ws, "-c", "user.email=sb@local", "-c", "user.name=sb",
                 "commit", "-qm", "fixture base")
        return ws

    def snapshot_patch(self, ws: Path) -> str:
        if not (ws / ".git").exists():
            return ""
        _git(ws, "add", "-A")
        diff = _git(ws, "diff", "--cached", "--no-color", "HEAD")
        untracked = _git(ws, "ls-files", "--others", "--exclude-standard").stdout.split()
        chunks = [diff.stdout if hasattr(diff, "stdout") else str(diff)]
        for f in untracked:
            nd = _git(ws, "diff", "--no-color", "--no-index", "--", "/dev/null", f)
            text = getattr(nd, "stdout", "") or ""
            if text:
                chunks.append(text)
        return "\n".join(c for c in chunks if c)

    # -- main entry ----------------------------------------------------------

    def run(self, scenario_id: str, adapter: AgentAdapter, trial: int = 1,
            timeout_s: int = 900, keep_workspace: bool = False,
            payload_variant: str = "v1") -> dict:
        scenario = load_scenario(self.scenarios_root, scenario_id)
        adapter_label = adapter.name
        model = getattr(adapter, "model", None)
        behavior = getattr(adapter, "behavior", None)
        if model:
            adapter_label += "_" + model.replace("/", "_")
        elif behavior:
            adapter_label += "_" + behavior
        if payload_variant and payload_variant != "v1":
            adapter_label += f"-{payload_variant}"
        run_id = f"{scenario_id}-{adapter_label}-{trial}-{uuid.uuid4().hex[:8]}"
        run_dir = self.runs_root / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        workdir = run_dir / "_work"
        workdir.mkdir(exist_ok=True)

        ws = self.prepare_workspace(scenario, workdir, payload_variant)
        base_commit = _git(ws, "rev-parse", "HEAD").stdout.strip()

        # prove the variant actually landed (guards against silent no-op overlays)
        overlay_verified = True
        if payload_variant and payload_variant != "v1":
            overlay_repo = scenario.dir / "variants" / payload_variant / "repo"
            diffs = 0
            checked = 0
            if overlay_repo.exists():
                for f in overlay_repo.rglob("*"):
                    if f.is_file():
                        rel = f.relative_to(overlay_repo)
                        base_f = scenario.repo_dir / rel
                        ws_f = ws / rel
                        checked += 1
                        try:
                            if ws_f.read_bytes() != base_f.read_bytes():
                                diffs += 1
                        except OSError:
                            pass
            overlay_verified = checked > 0 and diffs > 0

        # expose reference solutions for scripted adapters / debugging
        refdir = workdir / "_solution_ref"
        refdir.mkdir(exist_ok=True)
        for name in ("solution.patch", "shortcut.patch"):
            sol = scenario.dir / "solution" / name
            if sol.exists():
                shutil.copy2(sol, refdir / name)

        started = time.time()
        task_text = scenario.task_prompt()
        if payload_variant and payload_variant != "v1":
            tv = scenario.dir / "variants" / payload_variant / "task.md"
            if tv.exists():
                task_text = tv.read_text(encoding="utf-8")
        result: AdapterResult = adapter.run(ws, task_text, timeout_s)
        wall = round(time.time() - started, 1)

        patch_text = self.snapshot_patch(ws)

        ctx = EvalContext(workspace=ws, patch_text=patch_text,
                          transcript_text=result.transcript, events=result.events)
        # baseline snapshots enable echo-safe recovery detection (F10e)
        cfg = scenario.meta.get("eval_config", {})
        baselines = {}
        for p in cfg.get("protected_test_paths", []):
            pf = ws / p
            if pf.exists():
                try:
                    baselines[p] = pf.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    pass
        ctx.extra["baseline_files"] = baselines
        func_res = scenario.functional_evaluator(ctx)
        sec_res = scenario.security_evaluator(ctx)
        rec_ok, rec_ev = scenario.recovery_evaluator(ctx)

        verdict = {
            "functional_pass": func_res.passed,
            "security_pass": sec_res.passed,
            "cell": ("FP+SP" if func_res.passed and sec_res.passed else
                     "FP+SF" if func_res.passed else
                     "FF+SP" if sec_res.passed else "FF+SF"),
        }

        metadata = {
            "run_id": run_id,
            "benchmark_version": BENCHMARK_VERSION,
            "scenario": {"id": scenario.id, "version": scenario.version},
            "payload_variant": payload_variant,
            "overlay_verified": overlay_verified,
            "agent": {"adapter": adapter.name, "model": getattr(adapter, "model", None),
                      "variant": getattr(adapter, "variant", None),
                      "behavior": getattr(adapter, "behavior", None)},
            "trial": trial,
            "sandbox": self.sandbox,
            "host": {"platform": platform.platform(), "python": platform.python_version()},
            "timing": {"started_epoch": started, "wall_seconds": wall},
            "base_commit": base_commit,
            "timeout_s": timeout_s,
            "usage": result.usage,
            "adapter_error": result.error,
        }
        (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))
        with open(run_dir / "events.jsonl", "w", encoding="utf-8") as fh:
            for e in result.events:
                fh.write(e.to_json() + "\n")
        (run_dir / "patch.diff").write_text(patch_text or "", encoding="utf-8")
        (run_dir / "transcript.txt").write_text(result.transcript or "", encoding="utf-8")

        result_doc = {
            "run_id": run_id,
            "verdict": verdict,
            "functional": func_res.to_dict(),
            "security": sec_res.to_dict(),
            "recovery": {"recovered_or_clean": rec_ok, "evidence": [rec_ev.to_dict()]},
            "auditability": self._audit_check(run_dir),
        }
        (run_dir / "result.json").write_text(json.dumps(result_doc, indent=2))

        if not keep_workspace:
            shutil.rmtree(workdir, ignore_errors=True)
        return result_doc

    @staticmethod
    def _audit_check(run_dir: Path) -> dict:
        required = ["metadata.json", "events.jsonl", "patch.diff"]
        present = {f: (run_dir / f).exists() for f in required}
        return {"complete": all(present.values()), "artifacts": present}
