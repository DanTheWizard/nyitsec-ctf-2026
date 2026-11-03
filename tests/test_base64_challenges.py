"""Offline checks for NYITSec Base64 fundamentals challenges.

The tests derive the correct answers by independently decoding the student
artifacts. They intentionally do not store plaintext solutions in the repo.
"""

import base64
from pathlib import Path
import re
import runpy
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Base64ChallengeTests(unittest.TestCase):
    def check_challenge(self, challenge_id: str, expected_layers: int) -> None:
        folder = ROOT / "fundamentals" / challenge_id
        raw = (folder / "message.b64").read_bytes().strip()

        self.assertNotIn(b"Answer code:", raw)
        for layer in range(expected_layers):
            raw = base64.b64decode(raw, validate=True)
            if layer < expected_layers - 1:
                # Intermediate output must still be encoded, not readable text.
                self.assertNotIn(b"Answer code:", raw)

        decoded = raw.decode("utf-8")
        match = re.search(r"^Answer code: ([A-Z0-9-]+)$", decoded, re.MULTILINE)
        self.assertIsNotNone(match, "Decoded file must contain an answer code")
        answer = match.group(1)

        # Executing the verifier with a different run_name loads is_correct
        # without executing its interactive main() or accessing /flag.
        verifier = runpy.run_path(str(folder / "verify"), run_name="nyitsec-test")
        check = verifier["is_correct"]

        self.assertTrue(check(answer))
        self.assertTrue(check(answer.lower()))
        self.assertTrue(check(f"  {answer}  "))
        self.assertFalse(check(""))
        self.assertFalse(check("incorrect-answer"))
        self.assertFalse(check(answer + "-wrong"))

    def test_basic_base64_single_layer(self):
        self.check_challenge("base64-basics", expected_layers=1)

    def test_triple_base64_three_layers(self):
        self.check_challenge("base64-layers", expected_layers=3)


if __name__ == "__main__":
    unittest.main()
