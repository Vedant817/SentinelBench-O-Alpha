"""Generate CHANGELOG.md content from git tags (fixture: deterministic)."""
import sys
from pathlib import Path

ENTRIES = ["v1.2.0 — async worker pool", "v1.1.0 — retry hardening", "v1.0.0 — initial"]


def render():
    lines = ["# Changelog", ""]
    lines += [f"- {e}" for e in ENTRIES]
    return "\n".join(lines) + "\n"


def main(out_path="CHANGELOG.md"):
    Path(out_path).write_text(render(), encoding="utf-8")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "CHANGELOG.md")
