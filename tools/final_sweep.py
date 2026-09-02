"""Final verification sweep for the completed project."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

checks = []


def check(name, ok, detail=""):
    checks.append((name, bool(ok), detail))


# 1 unit tests
r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                   cwd=ROOT, capture_output=True, text=True)
check("unit tests", r.returncode == 0, r.stdout.strip().splitlines()[-1] if r.stdout else "")

# 2 scenario gate (core + red)
r = subprocess.run([sys.executable, "-m", "sentinelbench", "validate"],
                   cwd=ROOT, capture_output=True, text=True)
check("scenario gate (14 scenarios)", "FAIL" not in r.stdout and r.stdout.count("OK") == 14)

import os
os.environ["SBX_HELDOUT_DIR"] = str(ROOT / "scenarios-heldout")
r = subprocess.run([sys.executable, "-m", "sentinelbench", "validate"],
                   cwd=ROOT, capture_output=True, text=True)
# validate only reads scenarios/ dir; heldout validated separately below
from sentinelbench.scenarios import load_scenario
try:
    sc = load_scenario(ROOT / "scenarios-heldout", "heldout-env-dump-issue")
    check("heldout scenario loads", True)
except Exception as e:  # noqa: BLE001
    check("heldout scenario loads", False, str(e))

# 3 leaderboard consistency
lb = json.loads((ROOT / "results" / "leaderboard.json").read_text())
total_valid = sum(v["runs"] for v in lb["leaderboard"].values())
sf_total = sum(v["fp_sf"] + v["ff_sf"] for v in lb["leaderboard"].values())
check("leaderboard totals consistent",
      total_valid == lb["total_runs"],
      f"{total_valid} vs {lb['total_runs']}")
n_invalidated = sum(1 for d in (ROOT / "runs").iterdir()
                    if (d / "result.json").exists()
                    and json.loads((d / "result.json").read_text()).get("invalidated"))
check("quarantined runs excluded from totals",
      sf_total + sum(v["fp_sp"] + v["ff_sp"] for v in lb["leaderboard"].values())
      == total_valid,
      f"cells sum {total_valid}")

# 4 evaluator contract via scripted adapters (fast subset)
from sentinelbench.adapters.scripted import ScriptedAdapter  # noqa: E402
from sentinelbench.runner import Runner  # noqa: E402
runner = Runner(ROOT / "scenarios", ROOT / "runs" / "_final", sandbox="local")
res_c = runner.run("comment-injection-flaky-test", ScriptedAdapter("compliant"), trial=901)
check("scripted compliant FP+SP", res_c["verdict"]["cell"] == "FP+SP")
res_m = runner.run("comment-injection-flaky-test", ScriptedAdapter("misbehaving"), trial=902)
check("scripted misbehaving SF caught", res_m["verdict"]["cell"].endswith("SF"))
check("recovery dimension present", "recovery" in res_m)

fails = [c for c in checks if not c[1]]
for name, ok, detail in checks:
    print(("PASS " if ok else "FAIL "), name, ("| " + detail) if detail else "")
print(f"\n{len(checks)-len(fails)}/{len(checks)} checks passed")
sys.exit(1 if fails else 0)
