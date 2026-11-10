"""Test the standard NYITSec writable workspace copier and safety rules."""

import os
from pathlib import Path
import runpy
import stat
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "nyitsec-challenge"
FILES_EXCLUDED = {
    ".init", ".workspace.py", ".ctfignore", "verify",
    "bin", "README.md", "DESCRIPTION.md",
}


class WorkspaceStagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.tmp = Path(self.temp.name)
        self.loader = runpy.run_path(
            str(TEMPLATE / ".workspace.py"),
            run_name="workspace-staging-test",
        )
        self.prepare = self.loader["prepare_workspace"]

    def test_template_stages_normal_data(self):
        source = ROOT / "fundamentals" / "password-audit"
        dest = self.tmp / "copied-lab"
        expected = {"audit_record.txt", "common_passwords.txt"}
        self.assertEqual(set(self.prepare(source, dest)), expected)
        self.assertEqual({p.name for p in dest.iterdir()}, expected)
        for name in expected:
            self.assertEqual((dest / name).read_bytes(), (source / name).read_bytes())
            self.assertEqual(stat.S_IMODE((dest / name).stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(dest.stat().st_mode), 0o700)

    def test_writable_student_scratch_and_refuses_overwrite(self):
        dest = self.tmp / "working"
        self.prepare(ROOT / "fundamentals" / "password-audit", dest)
        scratch = dest / "audit.sh"
        scratch.write_text("#!/bin/bash\necho practice\n")
        self.assertEqual(scratch.read_text(), "#!/bin/bash\necho practice\n")
        with self.assertRaises(FileExistsError):
            self.prepare(ROOT / "fundamentals" / "password-audit", dest)
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
        src = ROOT / "fundamentals" / "incident-id"
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
