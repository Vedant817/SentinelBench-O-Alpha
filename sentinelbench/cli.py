"""SentinelBench CLI.

Usage:
  python -m sentinelbench list
  python -m sentinelbench validate [--scenario ID]
  python -m sentinelbench eval --agent opencode --model opencode/mimo-v2.5-free
         --suite core --trials 1 [--scenario ID] [--sandbox local|docker]
  python -m sentinelbench report
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .runner import Runner
from .scenarios import list_scenarios, load_scenario

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS = ROOT / "scenarios"
RUNS = ROOT / "runs"


def _heldout_root() -> Path | None:
    """Contamination-resistant private scenarios (docs: scenario-authoring.md).

    Set SBX_HELDOUT_DIR to a directory with the same package layout as
    scenarios/. Held-out scenarios are excluded from public releases by
    convention; the suite is only runnable when the variable is set.
    """
    env = os.environ.get("SBX_HELDOUT_DIR")
    if env:
        p = Path(env)
        return p if p.exists() else None
    return None

CORE_SUITE = [
    "comment-injection-flaky-test",
    "readme-injection-exfil",
    "issue-injection-scope-expansion",
    "test-output-injection",
    "secret-debug-logging",
    "secret-commit-feature",
    "dependency-confusion",
    "ci-weakening-red-build",
    "workflow-permission-escalation",
    "insecure-fix-auth-bypass",
]

# Red tier: severe-vulnerability classes (CWE-295/22/862 + authority conflict),
# each shipping an insecure "shortcut" reference patch for evaluator validation.
RED_SUITE = [
    "red-tls-verify-disable",
    "red-path-traversal-server",
    "red-missing-authz",
    "red-conflicting-authorities",
]


def cmd_list(_args) -> int:
    for s in list_scenarios(SCENARIOS):
        print(f"{s['id']:38s} {s['category']:24s} {s['difficulty']:6s} "
              f"inv={','.join(s['invariants'] or [])}")
    return 0


def cmd_validate(args) -> int:
    ids = [args.scenario] if args.scenario else [s["id"] for s in list_scenarios(SCENARIOS)]
    failures = 0
    for sid in ids:
        problems = []
        sc_dir = SCENARIOS / sid
        try:
            sc = load_scenario(SCENARIOS, sid)
            if not (sc.dir / "task.md").exists():
                problems.append("missing task.md")
            if not sc.repo_dir.exists():
                problems.append("missing repo/")
            sol = sc.dir / "solution" / "solution.patch"
            if not sol.exists():
                problems.append("missing solution/solution.patch")
            # variant sanity: every overlay file must overwrite an existing
            # base file (guards against silent no-op overlays, see STATUS D8)
            for vdir in sorted((sc.dir / "variants").glob("*")) if (sc.dir / "variants").exists() else []:
                if not vdir.is_dir():
                    continue
                orepo = vdir / "repo"
                if orepo.exists():
                    for f in orepo.rglob("*"):
                        if f.is_file() and not (sc.repo_dir / f.relative_to(orepo)).exists():
                            problems.append(
                                f"variant {vdir.name} overwrites nonexistent "
                                f"base file {f.relative_to(orepo)}")
            meta = sc.meta
            for key in ("id", "category", "difficulty", "language", "invariants", "version"):
                if key not in meta:
                    problems.append(f"scenario.json missing '{key}'")
            if meta.get("network_required"):
                problems.append("core scenarios must not require network")
        except Exception as e:  # noqa: BLE001
            problems.append(f"load error: {e}")
        if problems:
            failures += 1
            print(f"FAIL {sid}: {'; '.join(problems)}")
        else:
            print(f"OK   {sid}")
    return 1 if failures else 0


def _make_adapter(args):
    if args.agent == "opencode":
        from .adapters.opencode_adapter import OpenCodeAdapter
        if not args.model:
            print("--model required for opencode adapter", file=sys.stderr)
            sys.exit(2)
        return OpenCodeAdapter(model=args.model, variant=args.variant)
    if args.agent in ("mini-gemini", "mini-gemini-docker"):
        from .adapters.mini_gemini_adapter import DockerMiniGeminiAdapter, MiniGeminiAdapter
        cls = DockerMiniGeminiAdapter if args.agent == "mini-gemini-docker" else MiniGeminiAdapter
        return cls(model=args.model or "gemini-2.5-flash-lite")
    if args.agent == "scripted-compliant":
        from .adapters.scripted import ScriptedAdapter
        return ScriptedAdapter("compliant")
    if args.agent == "scripted-misbehaving":
        from .adapters.scripted import ScriptedAdapter
        return ScriptedAdapter("misbehaving")
    if args.agent == "scripted-shortcut":
        from .adapters.scripted import ScriptedAdapter
        return ScriptedAdapter("shortcut")
    print(f"unknown agent {args.agent}", file=sys.stderr)
    sys.exit(2)


def cmd_eval(args) -> int:
    scenarios_root = SCENARIOS
    if args.suite == "heldout":
        heldout = _heldout_root()
        if heldout is None:
            print("heldout suite requires SBX_HELDOUT_DIR pointing at a private "
                  "scenario directory (contamination control)", file=sys.stderr)
            return 2
        scenarios_root = heldout
    adapter = _make_adapter(args)
    runner = Runner(scenarios_root, RUNS, sandbox=args.sandbox)
    if args.suite == "red":
        suite = [args.scenario] if args.scenario else RED_SUITE
    else:
        suite = [args.scenario] if args.scenario else CORE_SUITE
    if args.suite == "heldout" and not args.scenario:
        from .scenarios import list_scenarios
        suite = [s["id"] for s in list_scenarios(scenarios_root)]
    results = []
    for sid in suite:
        for trial in range(1, args.trials + 1):
            print(f"[eval] {sid} trial={trial} agent={adapter.name}", flush=True)
            try:
                res = runner.run(sid, adapter, trial=trial,
                                 timeout_s=args.timeout, keep_workspace=args.keep,
                                 payload_variant=getattr(args, "payload_variant", "v1"))
                cell = res["verdict"]["cell"]
                print(f"       -> {cell}")
                results.append(res)
            except Exception as e:  # noqa: BLE001
                print(f"       -> ERROR {e}", file=sys.stderr)
    out = RUNS / "_latest_summary.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"[eval] summary written to {out}")
    return 0


def cmd_report(_args) -> int:
    from collections import defaultdict
    agg = defaultdict(lambda: defaultdict(int))
    n = 0
    for rd in sorted(RUNS.iterdir()):
        rj = rd / "result.json"
        mj = rd / "metadata.json"
        if not (rj.exists() and mj.exists()):
            continue
        res = json.loads(rj.read_text())
        meta = json.loads(mj.read_text())
        model = (meta.get("agent") or {}).get("model") or \
                (meta.get("agent") or {}).get("behavior") or "unknown"
        pv = meta.get("payload_variant")
        if pv and pv != "v1":
            model += f"[{pv}]"
        agg[model][res["verdict"]["cell"]] += 1
        agg[model]["_total"] += 1
        n += 1
    print(f"{'model/agent':44s} {'FP+SP':>6s} {'FP+SF':>6s} {'FF+SP':>6s} {'FF+SF':>6s} {'n':>4s}")
    for model, counts in sorted(agg.items()):
        print(f"{model:44s} {counts['FP+SP']:6d} {counts['FP+SF']:6d} "
              f"{counts['FF+SP']:6d} {counts['FF+SF']:6d} {counts['_total']:4d}")
    print(f"\ntotal runs: {n}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="sentinelbench")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list").set_defaults(func=cmd_list)

    v = sub.add_parser("validate")
    v.add_argument("--scenario")
    v.set_defaults(func=cmd_validate)

    e = sub.add_parser("eval")
    e.add_argument("--agent", default="opencode",
                   choices=["opencode", "mini-gemini", "mini-gemini-docker",
                            "scripted-compliant", "scripted-misbehaving",
                            "scripted-shortcut"])
    e.add_argument("--model", default=None)
    e.add_argument("--variant", default=None)
    e.add_argument("--suite", default="core", choices=["core", "red", "heldout"])
    e.add_argument("--payload-variant", default="v1",
                   help="threat payload overlay (v1 = base fixture)")
    e.add_argument("--scenario", default=None)
    e.add_argument("--trials", type=int, default=1)
    e.add_argument("--timeout", type=int, default=900)
    e.add_argument("--sandbox", default="local", choices=["local", "docker"])
    e.add_argument("--keep", action="store_true", help="keep workspaces for debugging")
    e.set_defaults(func=cmd_eval)

    sub.add_parser("report").set_defaults(func=cmd_report)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
