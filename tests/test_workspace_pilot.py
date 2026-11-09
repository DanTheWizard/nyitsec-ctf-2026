"""Checks for the experimental NYITSec /nyitsec-ctf workspace module."""

import os
from pathlib import Path
import runpy
import stat
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "workspace-pilot"
IDS = ("incident-id", "base64-basics", "password-audit")
INPUTS = {
    "incident-id": {"events.log"},
    "base64-basics": {"message.b64"},
    "password-audit": {"audit_record.txt", "common_passwords.txt"},
}
FILES_EXCLUDED = {
    ".init", ".workspace.py", ".ctfignore", "verify",
    "bin", "README.md", "DESCRIPTION.md",
}


class WorkspacePilotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.tmp = Path(self.temp.name)
        self.loader = runpy.run_path(
            str(PILOT / "incident-id" / ".workspace.py"),
            run_name="workspace-pilot-test",
        )
        self.prepare = self.loader["prepare_workspace"]

    def test_three_pilots_preserve_inputs_and_checkers(self):
        canonical_setup = (PILOT / IDS[0] / ".workspace.py").read_bytes()
        canonical_init = (PILOT / IDS[0] / ".init").read_bytes()
        for exercise in IDS:
            with self.subTest(exercise=exercise):
                path = PILOT / exercise
                original = ROOT / "fundamentals" / exercise
                self.assertEqual((path / ".workspace.py").read_bytes(), canonical_setup)
                self.assertEqual((path / ".init").read_bytes(), canonical_init)
                self.assertEqual((path / "verify").read_bytes(),
                                 (original / "verify").read_bytes())
                self.assertEqual((path / "bin/nyitsec-answer").read_bytes(),
                                 (ROOT / "templates/nyitsec-challenge/bin/nyitsec-answer").read_bytes())
                self.assertTrue((path / ".init").stat().st_mode & stat.S_IXUSR)
                self.assertTrue((path / "verify").stat().st_mode & stat.S_IXUSR)
                self.assertTrue((path / "bin/nyitsec-answer").stat().st_mode & stat.S_IXUSR)
                self.assertIn("/nyitsec-ctf", (path / "DESCRIPTION.md").read_text())
                dest = self.tmp / ("copy-" + exercise)
                staged = self.prepare(path, dest)
                self.assertEqual(set(staged), INPUTS[exercise])
                self.assertEqual({p.name for p in dest.iterdir()}, INPUTS[exercise])
                for f in INPUTS[exercise]:
                    self.assertEqual((dest / f).read_bytes(), (original / f).read_bytes())
                    self.assertEqual(stat.S_IMODE((dest / f).stat().st_mode), 0o600)
                self.assertEqual(stat.S_IMODE(dest.stat().st_mode), 0o700)

    def test_writable_student_scratch_and_refuses_overwrite(self):
        dest = self.tmp / "working"
        self.prepare(PILOT / IDS[2], dest)
        scratch = dest / "audit.sh"
        scratch.write_text("#!/bin/bash\necho practice\n")
        self.assertEqual(scratch.read_text(), "#!/bin/bash\necho practice\n")
        with self.assertRaises(FileExistsError):
            self.prepare(PILOT / IDS[2], dest)
        self.assertTrue(scratch.exists(), "Existing student work must not be deleted")

    def test_symlink_source_ignored_and_ignore_patterns_applied(self):
        src = self.tmp / "source"
        src.mkdir()
        (src / "useful.txt").write_text("plain example")
        (src / "ignore.bak").write_text("unwanted")
        (src / "verify").write_text("never stage verifier")
        (src / ".init").write_text("never stage init")
        (src / "secret").mkdir()
        (src / "secret" / "something.txt").write_text("do not stage")
        (src / "other").mkdir()
        (src / "other" / "included.txt").write_text("inside")
        (src / "shortcut").symlink_to(src / "useful.txt")
        (src / ".ctfignore").write_text("*.bak\nsecret/\n")
        dest = self.tmp / "test-copy"
        staged = self.prepare(src, dest)
        self.assertEqual(set(staged), {"useful.txt", "other/included.txt"})
        self.assertFalse((dest / "shortcut").exists())
        self.assertEqual(stat.S_IMODE((dest / "other").stat().st_mode), 0o700)

    def test_existing_symlink_destination_is_not_followed(self):
        src = PILOT / IDS[0]
        protected = self.tmp / "protected"
        protected.mkdir()
        (protected / "dont-delete.txt").write_text("retain")
        link = self.tmp / "redirect"
        link.symlink_to(protected, target_is_directory=True)
        with self.assertRaises(FileExistsError):
            self.prepare(src, link)
        self.assertEqual((protected / "dont-delete.txt").read_text(), "retain")

    def test_protected_exclusions_cannot_be_overridden(self):
        src = self.tmp / "source"
        src.mkdir()
        for name in FILES_EXCLUDED - {"bin"}:
            (src / name).write_text("do not copy")
        (src / "bin").mkdir()
        (src / "bin" / "nyitsec-answer").write_text("wrapper")
        (src / "message.b64").write_text("example")
        (src / ".ctfignore").write_text("# no extra exclusions\n")
        dest = self.tmp / "copied"
        self.prepare(src, dest)
        self.assertEqual([p.name for p in dest.iterdir()], ["message.b64"])


if __name__ == "__main__":
    unittest.main()
