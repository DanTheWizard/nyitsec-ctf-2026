"""Run officer QA probes against fake verifiers to prevent false-positive PASS.

Tests never execute the real privileged verifier and never access /flag.
They extract the documented Python code and replace subprocess.run with a fake.
"""
import contextlib
from io import StringIO
from pathlib import Path
import re
import subprocess
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

class OfficerQAProbeSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        guide = (ROOT / "docs/officer-solutions/fundamentals/base64-basics.md").read_text(encoding="utf-8")
        section = guide.split("### Noninteractive checker test over SSH", 1)[1]
        match = re.search(r"```python\n([\s\\S]*?)\n```", section)
        if match is None:
            raise AssertionError("Missing Python QA probe in officer guide")
        cls.probe = match.group(1)

    def run_probe(self, responses=None, exception=None):
        buffer = StringIO()
        side_effect = exception if exception is not None else responses
        with patch("subprocess.run", side_effect=side_effect) as call, contextlib.redirect_stdout(buffer):
            with self.assertRaises(SystemExit) as result:
                exec(compile(self.probe, "<officer-qa-probe>", "exec"), {"__name__": "__main__"})
        self.assertEqual(call.call_count, 2)
        return result.exception.code, buffer.getvalue()

    def response(self, text, code=0):
        return subprocess.CompletedProcess(["nyitsec-answer"], code, stdout=text, stderr="")

    def test_normal_success(self):
        code, output = self.run_probe([
            self.response("Not quite. Decode the provided file and try again.\n"),
            self.response("Correct! Here is your unique pwn.college flag:\npwn.college{test-example-only}\n"),
        ])
        self.assertEqual(code, 0)
        self.assertIn("PASS: deliberately incorrect answer rejected", output)
        self.assertIn("PASS: correct answer accepted", output)
        self.assertNotIn("test-example-only", output)

    def test_verifier_crash_does_not_count_as_rejection(self):
        code, output = self.run_probe([
            self.response("", code=127),
            self.response("Correct! Here is your unique pwn.college flag:\npwn.college{test-example-only}\n"),
        ])
        self.assertEqual(code, 2)
        self.assertIn("BLOCKED: incorrect verifier exited", output)
        self.assertNotIn("PASS: deliberately incorrect answer rejected", output)

    def test_success_marker_without_flag_is_blocked(self):
        code, output = self.run_probe([
            self.response("Not quite. Decode the provided file and try again.\n"),
            self.response("Correct! Here is your unique pwn.college flag:\n"),
        ])
        self.assertEqual(code, 2)
        self.assertIn("BLOCKED: success marker present", output)
        self.assertNotIn("PASS: correct answer accepted", output)

    def test_incorrect_answer_accepted_is_failure(self):
        code, output = self.run_probe([
            self.response("Correct! Here is your unique pwn.college flag:\npwn.college{test-example-only}\n"),
            self.response("Correct! Here is your unique pwn.college flag:\npwn.college{test-example-only}\n"),
        ])
        self.assertEqual(code, 1)
        self.assertIn("FAIL: deliberately incorrect answer was accepted", output)

    def test_transport_timeout_is_blocked(self):
        code, output = self.run_probe(exception=subprocess.TimeoutExpired(cmd="nyitsec-answer", timeout=15))
        self.assertEqual(code, 2)
        self.assertIn("BLOCKED: incorrect probe could not execute or timed out", output)

if __name__ == "__main__":
    unittest.main()
