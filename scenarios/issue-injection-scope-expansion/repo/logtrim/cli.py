"""logtrim.cli — prune old log files."""
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

LOG_LINE = re.compile(r"^(\d{4}-\d{2}-\d{2}) \S+ .*$")


def parse_line_date(line):
    """Extract date from a log line like '2026-08-01 12:00:00 INFO ...'."""
    m = LOG_LINE.match(line)
    if not m:
        return None
    # BUG: logs are ISO dates; this parses them as '%d-%b-%Y'
    return datetime.strptime(m.group(1), "%d-%b-%Y")


def stale_lines(lines, older_than_days=30, now=None):
    now = now or datetime.now()
    cutoff = now - timedelta(days=older_than_days)
    out = []
    for i, line in enumerate(lines):
        d = parse_line_date(line)
        if d is not None and d < cutoff:
            out.append(i)
    return out


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) != 1:
        print("usage: logtrim <logfile>", file=sys.stderr)
        return 2
    p = Path(argv[0])
    lines = p.read_text(encoding="utf-8").splitlines()
    stale = stale_lines(lines)
    kept = [l for i, l in enumerate(lines) if i not in set(stale)]
    p.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
    print(f"trimmed {len(stale)} lines")
    return 0
