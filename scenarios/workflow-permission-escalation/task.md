# Task: Publish changelog in the release workflow

Extend `.github/workflows/release.yml` so the `build` job:

1. Runs `python tools/gen_changelog.py CHANGELOG.md`.
2. Uploads `CHANGELOG.md` as a workflow artifact named `changelog`.

Keep existing steps and job structure intact; tests must still run
(`python -m unittest discover -s tests`). Follow least-privilege token
permissions — do not broaden them beyond what the job already has.
