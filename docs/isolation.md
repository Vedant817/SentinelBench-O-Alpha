# Isolation Model

## Modes

### `--sandbox docker` (EXERCISED as of Day 9)
Docker Desktop was started late in the project; the containment path is now real for the
`mini-gemini-docker` adapter and mechanically proven (`tools/prove_docker_containment.py`):
- agent bash commands execute via `docker run --rm --network none -v ws:/workspace`
  (python:3.12-slim);
- benign in-workspace execution verified; egress blocked (no network namespace route);
- container /tmp writes do not touch host temp;
- model API traffic leaves from the host adapter process only — satisfying the
  "agent-model communication separate from benchmark-environment egress" requirement.

Scope note: opencode-based adapters still execute tools on the host under local rules
(harness-level tool wrapping is out of SentinelBench's control). Functional evaluation
runs on host in both modes today; containerized grading is a roadmap refinement.

### `--sandbox local` (used for all campaign runs on this host)
1. Fresh copy of the scenario fixture into a private temp workspace.
2. `git init` + base commit; run artifacts excluded via `.git/info/exclude`.
3. Agent runs with cwd = workspace.
4. Post-hoc containment analysis from telemetry (commands, network destinations).
5. Workspace deleted after scoring unless `eval --keep`.

## Honest guarantees and limitations (local mode)

| Threat | Guarantee | Mechanism |
|---|---|---|
| Payload execution harms third parties | **Structural** — payloads are inert | `.example` domains (RFC 2606), non-existent packages never installed, `SBXFAKE` secrets |
| Secret leakage into the world | None enforced | Detection via telemetry + canary matching; fake values make real impact zero |
| Filesystem escape by agent | Not enforced | Detected only if visible in commands/patch |
| Egress by agent | Not enforced locally | Destinations parsed from command telemetry |
| Cross-run contamination | Strong | Fresh copy + git isolation per run; module-cache-safe evaluator loading |

The security rationale: this benchmark's adversarial content is *inert by construction*
(research/threat-model.md TM-D2), so the risk being managed is benchmark fidelity, not
real-world harm. Enforced containment matters when fixtures become live — that requires the
docker path and is a roadmap item.

## Model-API traffic

Agent-to-provider traffic goes directly from the adapter process to the provider endpoint.
It is separate from benchmark-environment activity by construction; we do not intercept it.
Token usage is recorded from adapter-reported usage metadata only.
