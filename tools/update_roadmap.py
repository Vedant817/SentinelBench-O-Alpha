"""Update REPORT.md roadmap section (robust to unicode variance)."""
from pathlib import Path

p = Path("research/REPORT.md")
lines = p.read_text(encoding="utf-8").splitlines()

# find the roadmap section start
start = next(i for i, l in enumerate(lines) if l.startswith("## 12. Roadmap"))
new_section = """## 12. Roadmap (grounded in these results)

1. Docker-enforced isolation — **shipped and exercised** for the mini-gemini-docker
   adapter (offline container bash; containment mechanically proven via
   tools/prove_docker_containment.py). opencode-adapter tool wrapping stays host-level.
2. Held-out private scenario split — **mechanism shipped and populated with one worked
   example** (scenarios-heldout/, --suite heldout + SBX_HELDOUT_DIR).
3. Multi-harness study — **second harness shipped; partial result**: minimal ReAct
   harness produced clean runs on 4 scenarios, consistent with gateway harness on
   same-family models. Full factorial study remains open.
4. Payload variant families — **shipped for 4 directive scenarios** with overlay-
   verification guards (F12); extend to secret/dependency scenarios.
5. Recovery-dimension scoring — **shipped**; first application: 0 recoveries recorded.
6. Frontier-model replication to test whether the dissociation persists beyond free tier."""

p.write_text("\n".join(lines[:start]) + new_section + "\n",
             encoding="utf-8", newline="\n")
print("roadmap updated")
