"""Build solution patches for scenarios.

For scenario <id>: copies repo/ to a temp git dir, overlays files from
solution/files/, writes the resulting diff to solution/solution.patch.
Verifies the patch applies cleanly back onto repo/.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCEN = ROOT / "scenarios"


def git(d: Path, *a: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *a], cwd=str(d), capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def build(sid: str) -> int:
    sc = SCEN / sid
    repo = sc / "repo"
    files_dir = sc / "solution" / "files"
    if not files_dir.exists():
        print(f"{sid}: no solution/files; skip")
        return 0
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "ws"
        shutil.copytree(repo, tmp)
        if (tmp / ".git").exists():
            shutil.rmtree(tmp / ".git")
        git(tmp, "init", "-q")
        git(tmp, "config", "core.autocrlf", "false")
        git(tmp, "add", "-A")
        git(tmp, "-c", "user.email=s@l", "-c", "user.name=s", "commit", "-qm", "base")
        for f in files_dir.rglob("*"):
            if f.is_file():
                rel = f.relative_to(files_dir)
                dest = tmp / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dest)
        git(tmp, "add", "-A")
        diff = git(tmp, "diff", "--cached", "--no-color", "HEAD").stdout
        out = sc / "solution" / "solution.patch"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(diff, encoding="utf-8", newline="\n")
        # verify clean apply onto pristine copy
        verify = Path(td) / "verify"
        shutil.copytree(repo, verify)
        if (verify / ".git").exists():
            shutil.rmtree(verify / ".git")
        ap = git(verify, "apply", "--check", str(out))
        if ap.returncode != 0:
            print(f"{sid}: PATCH APPLY CHECK FAILED:\n{ap.stderr}")
            return 1
    print(f"{sid}: solution.patch written ({len(diff.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    ids = sys.argv[1:] or [d.name for d in SCEN.iterdir()
                           if (d / "scenario.json").exists()]
    rc = 0
    for i in ids:
        rc |= build(i)
    sys.exit(rc)
