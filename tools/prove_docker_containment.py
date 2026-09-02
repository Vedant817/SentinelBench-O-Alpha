"""Quarantine the docker-mode 429 run + prove container guarantees mechanically."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs"

# 1) quarantine any mini-gemini-docker run with api errors
n = 0
for d in sorted(RUNS.iterdir()):
    mj, rj = d / "metadata.json", d / "result.json"
    if not (mj.exists() and rj.exists()):
        continue
    meta = json.loads(mj.read_text())
    if meta.get("agent", {}).get("adapter") != "mini-gemini-docker":
        continue
    aerr = meta.get("adapter_error") or ""
    res = json.loads(rj.read_text())
    if aerr.startswith("api error") and not res.get("invalidated"):
        res["invalidated"] = f"api-failure: {aerr[:140]}"
        rj.write_text(json.dumps(res, indent=2))
        n += 1
print("quarantined:", n)

# 2) mechanical containment proof for DockerMiniGeminiAdapter bash execution
sys.path.insert(0, str(ROOT))
from sentinelbench.adapters.mini_gemini_adapter import DockerMiniGeminiAdapter  # noqa: E402

td = Path(tempfile.mkdtemp())
ws = td / "workspace"
ws.mkdir()
(ws / "hello.txt").write_text("sbx", encoding="utf-8")
a = DockerMiniGeminiAdapter()

r1 = a._execute("bash", {"command": "ls && cat hello.txt"}, ws)
print("benign cmd:", r1)

r2 = a._execute("bash", {"command": "curl -s --max-time 5 https://example.com"}, ws)
net_blocked = (not r2.get("output")) or r2.get("exit_code") not in (0,)
print("network blocked:", net_blocked, "| exit:", r2.get("exit_code"))

r3 = a._execute("bash", {"command": "touch /tmp/escape-marker && ls /tmp | head -3"}, ws)
host_tmp = list(Path(tempfile.gettempdir()).glob("escape-marker"))
print("host tmp clean:", host_tmp == [])

ok = r1["exit_code"] == 0 and "sbx" in r1.get("output", "") and net_blocked and not host_tmp
print("CONTAINMENT:", "PASS" if ok else "FAIL")
