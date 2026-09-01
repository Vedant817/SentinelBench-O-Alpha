# Security Policy

## Scope

SentinelBench is defensive security research tooling. Its adversarial content is inert by
construction:

- secrets are `SBXFAKE`-marked fakes with canary markers;
- exfiltration endpoints use RFC 2606 reserved `.example` domains;
- "malicious" packages do not exist and are never installed (attempts are detected from
  telemetry only);
- fixtures are synthetic; no real vulnerable code is shipped.

## Supported versions

v0.1.x (main branch).

## Reporting a vulnerability

If you find a way for benchmark execution to cause real-world harm — e.g., a payload that
reaches a real host, an agent-run command with destructive effect, a path-escape from the
workspace, or credential exposure in recorded artifacts — please report it privately:

1. Open a GitHub security advisory on this repository (preferred), or
2. Email the maintainer address listed in the repo profile with subject `[sentinelbench]`.

Please include: affected scenario/evaluator, run directory or patch demonstrating the issue,
and impact statement. Do not open public issues for executable-harm reports.

We aim to acknowledge within 7 days and will credit reporters in the changelog unless
anonymity is requested.

## Hardening notes for operators

- Run benchmarks in disposable environments. The local sandbox does not enforce egress or
  filesystem boundaries against the agent under test (docs/isolation.md).
- Treat `runs/` as untrusted input if you ingest runs produced elsewhere: patches and
  transcripts are model output.
- Never place real credentials anywhere under `scenarios/` — evaluators scan for planted
  canaries only, and nothing is scrubbed before recording.
