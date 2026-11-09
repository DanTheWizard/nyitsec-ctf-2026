"""Regression checks for the live migration to /nyitsec-ctf.

The three pilot challenges remain unchanged as a known-good reference while
five real Fundamentals challenges move to the writable workspace.
"""

import hashlib
from pathlib import Path
import runpy
import stat
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
FUNDAMENTALS = ROOT / "fundamentals"
TEMPLATE = ROOT / "templates" / "nyitsec-challenge"
INPUTS = {
    "incident-id": {"events.log"},
    "base64-basics": {"message.b64"},
    "base64-layers": {"message.b64"},
    "base64-more": {"message.b64"},
    "password-audit": {"audit_record.txt", "common_passwords.txt"},
}


class WritableWorkspaceMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tool = runpy.run_path(
            str(TEMPLATE / ".workspace.py"), run_name="migration-unit-test"
        )
        cls.prepare = staticmethod(tool["prepare_workspace"])

    def test_all_five_fundamentals_use_shared_workspace_setup(self):
        init = (TEMPLATE / ".init").read_bytes()
        worker = (TEMPLATE / ".workspace.py").read_bytes()
        self.assertIn(b"/nyitsec-ctf", init)
        self.assertIn(b"/challenge/.workspace.py", init)
        self.assertIn(b"PROTECTED_NAMES", worker)

        for exercise, expected in INPUTS.items():
            with self.subTest(challenge=exercise):
                folder = FUNDAMENTALS / exercise
                self.assertEqual((folder / ".init").read_bytes(), init)
                self.assertEqual((folder / ".workspace.py").read_bytes(), worker)
                self.assertTrue((folder / ".ctfignore").is_file())
                for name in (".init", "verify", "bin/nyitsec-answer"):
                    self.assertTrue((folder / name).stat().st_mode & stat.S_IXUSR)
                desc = (folder / "DESCRIPTION.md").read_text()
                self.assertIn("/nyitsec-ctf", desc)
                self.assertIn("nyitsec-answer", desc)
                self.assertIn("Temporary workspace notice", desc)
                self.assertNotIn("cd /challenge", desc)

                with tempfile.TemporaryDirectory() as root:
                    dest = Path(root) / "student-workspace"
                    staged = set(self.prepare(folder, dest))
                    self.assertEqual(staged, expected)
                    self.assertEqual({p.name for p in dest.iterdir()}, expected)
                    self.assertEqual(stat.S_IMODE(dest.stat().st_mode), 0o700)
                    for name in expected:
                        self.assertEqual(
                            (dest / name).read_bytes(), (folder / name).read_bytes()
                        )
                        self.assertEqual(
                            stat.S_IMODE((dest / name).stat().st_mode), 0o600
                        )
                    # A normal user may write their own files beside the copied
                    # challenge materials. The privileged files must not be there.
                    script = dest / "scratch.sh"
                    script.write_text("#!/bin/sh\nprintf 'test'\n")
                    self.assertTrue(script.is_file())
                    for private in (
                        ".init", ".workspace.py", ".ctfignore",
                        "verify", "bin", "README.md", "DESCRIPTION.md",
                    ):
                        self.assertFalse((dest / private).exists(), private)

    def test_password_audit_still_matches_protected_verifier(self):
        folder = FUNDAMENTALS / "password-audit"
        record = (folder / "audit_record.txt").read_text()
        digest = record.split("sha256=", 1)[1].splitlines()[0]
        candidates = (folder / "common_passwords.txt").read_text().splitlines()
        solutions = [
            c for c in candidates
            if hashlib.sha256(c.encode("utf-8")).hexdigest() == digest
        ]
        self.assertEqual(len(solutions), 1)
        checker = runpy.run_path(
            str(folder / "verify"), run_name="migration-unit-test"
        )["is_correct"]
        self.assertTrue(checker(solutions[0]))
        self.assertFalse(checker("a wrong guess"))

    def test_pilot_is_retained_for_post_merge_comparison(self):
        pilot = ROOT / "workspace-pilot"
        for id in ("incident-id", "base64-basics", "password-audit"):
            with self.subTest(challenge=id):
                folder = pilot / id
                self.assertTrue((folder / ".init").is_file())
                self.assertIn(b"/nyitsec-ctf", (folder / ".init").read_bytes())
                self.assertEqual(
                    (folder / "verify").read_bytes(),
                    (FUNDAMENTALS / id / "verify").read_bytes()
                )


if __name__ == "__main__":
    unittest.main()
