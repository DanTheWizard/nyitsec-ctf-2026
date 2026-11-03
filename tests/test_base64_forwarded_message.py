"""Offline regression tests for the forwarded-message Base64 challenge."""

import base64
from pathlib import Path
import re
import runpy
import unittest


ROOT = Path(__file__).resolve().parents[1] / "fundamentals" / "base64-more"
B64_TOKEN = re.compile(r"^[A-Za-z0-9+/]+={0,2}$")


def decode_b64(text: str) -> str:
    assert B64_TOKEN.fullmatch(text), "Expected an isolated Base64 segment"
    return base64.b64decode(text, validate=True).decode("utf-8")


class ForwardedMessageBase64Tests(unittest.TestCase):
    def test_three_layers_with_text_wrappers_and_verifier(self):
        ciphertext = (ROOT / "message.b64").read_text(encoding="utf-8").strip()

        first = decode_b64(ciphertext)
        self.assertTrue(first.startswith("Forwarded to you:"))
        forwarded_lines = first.splitlines()
        self.assertEqual(len(forwarded_lines), 2)
        self.assertEqual(forwarded_lines[0].strip(), "Forwarded to you:")
        forwarded_payload = forwarded_lines[1].strip()

        # The text wrapper must be removed before decoding again.
        self.assertFalse(B64_TOKEN.fullmatch(first))
        second = decode_b64(forwarded_payload)

        reply_lines = second.splitlines()
        self.assertEqual(len(reply_lines), 2)
        reply_match = re.fullmatch(r"Reply to ([A-Za-z0-9+/]+={0,2})", reply_lines[0])
        self.assertIsNotNone(reply_match)
        self.assertTrue(reply_lines[1].strip())
        self.assertFalse(B64_TOKEN.fullmatch(second))

        third = decode_b64(reply_match.group(1))
        original = re.fullmatch(r"My message: ([A-Za-z]+ [A-Za-z]+)", third)
        self.assertIsNotNone(original, "Last decode must reveal a two-word message")
        answer = original.group(1)

        # Load the checker without running interactive main() or touching /flag.
        checker = runpy.run_path(str(ROOT / "verify"), run_name="nyitsec-test")["is_correct"]
        self.assertTrue(checker(answer))
        self.assertTrue(checker(answer.upper()))
        self.assertTrue(checker(" " + answer + " "))
        self.assertFalse(checker(""))
        self.assertFalse(checker("incorrect answer"))
        self.assertFalse(checker(reply_lines[1].strip()))
        self.assertFalse(checker(forwarded_payload))
        self.assertFalse(checker(answer + " extra"))


if __name__ == "__main__":
    unittest.main()
