"""End-to-end runner tests using scripted adapters (no model calls)."""
import unittest

from pathlib import Path

from sentinelbench.adapters.scripted import ScriptedAdapter
from sentinelbench.runner import Runner

ROOT = Path(__file__).resolve().parent.parent


class TestRunnerE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = Runner(ROOT / "scenarios", ROOT / "runs" / "_tests", sandbox="local")

    def test_compliant_passes_everything(self):
        res = self.runner.run("comment-injection-flaky-test",
                              ScriptedAdapter("compliant"), trial=99)
        self.assertEqual(res["verdict"]["cell"], "FP+SP")
        self.assertTrue(res["auditability"]["complete"])

    def test_misbehaving_caught(self):
        res = self.runner.run("comment-injection-flaky-test",
                              ScriptedAdapter("misbehaving"), trial=98)
        self.assertEqual(res["verdict"]["cell"], "FP+SF")

    def test_run_artifacts_written(self):
        res = self.runner.run("dependency-confusion",
                              ScriptedAdapter("misbehaving"), trial=97)
        full = self.runner.runs_root / res["run_id"]
        for f in ["metadata.json", "events.jsonl", "patch.diff", "result.json"]:
            self.assertTrue((full / f).exists(), f)


if __name__ == "__main__":
    unittest.main()
