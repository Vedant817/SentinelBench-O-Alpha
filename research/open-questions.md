# Open Questions — SentinelBench

Maintained throughout the project. Status: OPEN / RESOLVED / PARKED. Resolved items move to
decisions.md with rationale; this file keeps the live list.

## Scientific
- OQ1 (PARTIALLY RESOLVED Day 7): free-tier roster only; dissociation finding is structural
  but absolute rates await frontier replication (roadmap item 6).
- OQ2 (OPEN): cross-threat-class correlation untested at current cell sizes.
- OQ3 (RESOLVED Day 5, F11): security verdicts flip within identical cells; multi-trial
  protocols mandatory.
- OQ4 (RESOLVED Day 6): test-weakening detection via normalized assert-content matching;
  conservative patterns for skip/xfail/pass. Multi-line asserts remain a documented gap.
- OQ5 (ANSWERED Day 6, F6): agents that notice injections typically name-and-refuse;
  noticed-but-complied class observed only in muse-spark.

## Engineering
- OQ6 (OPEN): docker mode implemented but not exercised on this host.
- OQ7 (OPEN): opencode event schema pinned by version metadata only.
- OQ8 (CLOSED as limitation L4): local mode detects but does not enforce egress; documented.

## Benchmark validity
- OQ9 (PARTIALLY RESOLVED): fixtures modeled on recognizable OSS patterns; realism transfer
  to production repos remains unquantified.
- OQ10 (OPEN): payload variant families not yet built; single-variant payloads risk
  phrasing pattern-match.
- OQ11 (MITIGATED): canaries embedded in every fixture (tools/add_canaries.py); held-out
  split designed, not populated.
- OQ12 (OPEN): encoded/indirect exfil channels outside detection surfaces remain a blind spot.

## Re-check at Day 5 and Day 7
- Re-run searches: "coding agent security benchmark", "repository prompt injection benchmark",
  "agentic SWE security eval" to confirm no one shipped the missing system mid-project.
