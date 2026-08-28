"""Minimal secret scanner used by CI (fixture stand-in for a real SAST tool)."""
import argparse
import re
import sys
from pathlib import Path

PATTERNS = [
    (re.compile(r"(?i)(api_key|secret|token)\s*=\s*['\"][A-Za-z0-9]{16,}['\"]"), "hardcoded credential"),
]


def scan(root):
    findings = []
    for p in Path(root).rglob("*.py"):
        if ".git" in p.parts or "__pycache__" in p.parts:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            for pat, label in PATTERNS:
                if pat.search(line):
                    findings.append(f"{p}:{i}: {label}")
    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fail-on-findings", action="store_true")
    args = ap.parse_args()
    findings = scan(".")
    for f in findings:
        print(f"SECRETSCAN: {f}")
    if args.fail_on_findings and findings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
