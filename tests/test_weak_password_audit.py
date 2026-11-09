"""Offline tests for the synthetic weak-password audit challenge."""

import hashlib
from pathlib import Path
import runpy
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1] / "fundamentals" / "password-audit"


class WeakPasswordAuditTests(unittest.TestCase):
    def test_synthetic_wordlist_contains_one_match(self):
        record = (ROOT / "audit_record.txt").read_text(encoding="utf-8")
        fields = dict(
            line.split("=", 1)
            for line in record.splitlines()
            if line and not line.startswith("#")
        )
        self.assertEqual(fields["algorithm"], "sha256")
        self.assertEqual(fields["account"], "lab-demo")
        target = fields["sha256"]
        self.assertRegex(target, r"^[0-9a-f]{64}$")

        candidates = (ROOT / "common_passwords.txt").read_text(encoding="utf-8").splitlines()
        self.assertGreaterEqual(len(candidates), 40)
        self.assertEqual(len(candidates), len(set(candidates)))
        matching = [
            p for p in candidates
            if hashlib.sha256(p.encode("utf-8")).hexdigest() == target
        ]
        self.assertEqual(len(matching), 1)

        checker = runpy.run_path(str(ROOT / "verify"), run_name="unit-test")["is_correct"]
        self.assertTrue(checker(matching[0]))
        self.assertFalse(checker(""))
        self.assertFalse(checker(matching[0].swapcase()))
        self.assertFalse(checker("not-the-password"))
        self.assertFalse(checker(matching[0] + " "))

    def test_local_bash_wordlist_audit(self):
        # This script only checks local synthetic data; no network/login tools.
        script = r'''
target="$(grep '^sha256=' audit_record.txt | cut -d= -f2)"
found=""
while IFS= read -r candidate; do
    digest="$(printf '%s' "$candidate" | sha256sum | cut -d' ' -f1)"
    if [ "$digest" = "$target" ]; then
        found="$candidate"
        break
    fi
done < common_passwords.txt
printf '%s' "$found"
'''
        proc = subprocess.run(
            ["bash", "-c", script],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        candidate = proc.stdout
        self.assertTrue(candidate)
        self.assertEqual(
            hashlib.sha256(candidate.encode("utf-8")).hexdigest(),
            (ROOT / "audit_record.txt").read_text().split("sha256=")[1].splitlines()[0],
        )

    def test_beginner_instructions_use_writable_home_directory(self):
        description = (ROOT / "DESCRIPTION.md").read_text(encoding="utf-8")
        self.assertIn("nano ~/audit.sh", description)
        self.assertIn("bash ~/audit.sh", description)
        self.assertIn("Ctrl+O", description)
        self.assertIn("Ctrl+X", description)
        self.assertIn("/challenge/common_passwords.txt", description)
        self.assertIn("/challenge/audit_record.txt", description)
        self.assertNotIn("saved as `audit.sh` in your working directory", description)


if __name__ == "__main__":
    unittest.main()
