# Reproduction Guide

Everything in research/REPORT.md can be regenerated from this repository.

## Level 0 — harness integrity (minutes)

```bash
python -m unittest discover -s tests
python -m sentinelbench validate
python -m sentinelbench eval --agent scripted-compliant   # expect 10x FP+SP
python -m sentinelbench eval --agent scripted-misbehaving # expect SF cells
```

## Level 1 — recompute published numbers from recorded runs

Recorded campaign artifacts (events.jsonl, patch.diff, transcript.txt per run) are included.
Evaluators are deterministic; scoring is reproducible offline:

```bash
python tools/rescore.py        # re-scores every run with current evaluators
python tools/aggregate.py      # rebuilds results/leaderboard.json + failure-catalog.md
```

Cross-check: leaderboard joint rates should match the REPORT.md table. Note `rescored.version`
in result.json — published numbers use evaluator v4.

## Level 2 — replicate the campaign with live agents (hours, needs opencode + provider auth)

```bash
python tools/campaign.py --model opencode/mimo-v2.5-free --trials 3
# repeat for each model in the roster; free-tier roster:
#   opencode/x-preview-f-free, opencode/hy3-free,
#   opencode/mimo-v2.5-free, opencode/muse-spark-1.2-contributor-free,
#   opencode/nemotron-3-ultra-free, opencode/nemotron-3.5-lightning-free
python tools/rescore.py && python tools/aggregate.py
```

Expectation for replication: cell-level agreement on the *structure* of findings
(insecure-fix universal SF; transcript secret echo; muse-spark directive-following).
Individual trial verdicts are stochastic (finding F11): compare distributions over >=3
trials, never single runs.

## Level 3 — independent reimplementation (days)

The strongest check: implement the scenario evaluators from research/threat-model.md +
docs/scenario-authoring.md without reading our policy.py, run both evaluator sets over the
same recorded patches, and compare disagreements. Any disagreement is either your bug or
ours — both are publishable findings. Please open an issue.

## Reproducibility metadata recorded per run

benchmark version · scenario id+version · adapter name/model/variant · trial number ·
sandbox mode · host platform/python · base commit · timestamps · token usage ·
evaluator version at score time (`rescored.version`) · original scores preserved
(`result.orig.json` when re-scored).

## Known reproducibility caveats

1. Free-tier gateway models may be deprecate/route-shift over time; model ids are recorded
   per run so drift is detectable.
2. opencode CLI version affects event stream details (schema hash not yet pinned — OQ7);
   pin >=1.18.
3. Local sandbox does not enforce egress (docs/isolation.md); payloads are inert so this
   cannot change scores, but it changes what "network destination detected" means vs docker.
