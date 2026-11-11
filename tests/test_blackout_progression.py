"""Offline regression checks for Operation Blackout's three-stage progression pilot."""
import runpy
from pathlib import Path
import unittest
import yaml


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "blackout-pilot"


class BlackoutProgressionPilotTests(unittest.TestCase):
    def test_lock_order_is_sequential_and_within_one_module(self):
        dojo = yaml.safe_load((ROOT / "dojo.yml").read_text(encoding="utf-8"))
        self.assertEqual(dojo["id"], "example")
        self.assertEqual(dojo["modules"][-1]["id"], "blackout-pilot")
        module = yaml.safe_load((PILOT / "module.yml").read_text(encoding="utf-8"))
        challenges = module["challenges"]
        self.assertEqual(
            [challenge["id"] for challenge in challenges],
            ["signal-intercept", "incident-investigation", "restore-communications"],
        )
        self.assertFalse(challenges[0].get("progression_locked", False))
        self.assertTrue(challenges[1]["progression_locked"])
        self.assertTrue(challenges[2]["progression_locked"])

    def test_each_verifier_rejects_wrong_input_and_accepts_artifact_answer(self):
        for challenge_id in ("signal-intercept", "incident-investigation", "restore-communications"):
            with self.subTest(challenge=challenge_id):
                directory = PILOT / challenge_id
                verifier = runpy.run_path(str(directory / "verify"), run_name="pilot-verifier-test")
                expected = self._derive_expected(directory)
                self.assertFalse(verifier["is_correct"]("not-the-answer"))
                # Production reads the root-owned /challenge file; patch the verifier's
                # Path binding to redirect only this test to the checked-in artifact.
                real_path = verifier["Path"]
                verifier["is_correct"].__globals__["Path"] = (
                    lambda p, real_path=real_path, directory=directory:
                    real_path(directory / p.removeprefix("/challenge/"))
                )
                self.assertTrue(verifier["is_correct"](expected))
                self.assertFalse(verifier["is_correct"](expected + "-wrong"))

    @staticmethod
    def _derive_expected(directory):
        import base64
        import codecs
        if (directory / "transmission.b64").is_file():
            plain = base64.b64decode((directory / "transmission.b64").read_bytes()).decode()
            return next(line.split("=", 1)[1] for line in plain.splitlines()
                        if line.startswith("AUTH_CODE="))
        if (directory / "access.log").is_file():
            fields_by_line = [dict(part.split("=", 1) for part in line.split() if "=" in part)
                              for line in (directory / "access.log").read_text().splitlines()]
            result = [fields["event_id"] for fields in fields_by_line
                      if fields.get("service") == "ssh"
                      and fields.get("network") == "external"
                      and fields.get("outcome") == "blocked"
                      and int(fields.get("attempts", "0")) >= 10]
            assert len(result) == 1
            return result[0]
        plain = codecs.decode((directory / "recovery.rot13").read_text(), "rot_13")
        return next(line.split("=", 1)[1] for line in plain.splitlines()
                    if line.startswith("RESTORE_CODE="))


if __name__ == "__main__":
    unittest.main()
