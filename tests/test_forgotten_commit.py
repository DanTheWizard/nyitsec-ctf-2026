"""Real Git archaeology tests for the first Level 3 challenge."""

import hashlib
import os
from pathlib import Path
import runpy
import stat
import subprocess
import tarfile
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "level-3" / "forgotten-commit"
TEMPLATE = ROOT / "templates" / "nyitsec-challenge"
PHRASE = "Paper satellites still orbit"
LEDGER = "config/recovery-ledger.toml"


class ForgottenCommitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = runpy.run_path(
            str(LAB / ".history-builder.py"), run_name="officer-test"
        )

    def command(self, folder, *args):
        return self.script["git"](folder, *args)

    def test_complete_git_history_and_recover_latest_approved_version(self):
        with tempfile.TemporaryDirectory() as temp:
            project = self.script["build_history"](
                Path(temp) / "night-relay"
            )
            self.assertTrue((project / ".git").is_dir())
            self.assertFalse((project / LEDGER).exists())
            self.assertEqual(self.command(project, "branch", "--show-current"), "main")
            self.assertEqual(self.command(project, "status", "--porcelain"), "")
            self.assertEqual(
                len(self.command(project, "rev-list", "--all", "--count").splitlines()),
                1,
            )
            self.assertEqual(
                self.command(project, "rev-list", "--all", "--count"), "10"
            )
            self.assertEqual(
                self.command(project, "remote", "-v"), "",
                "The fictional repo must not reference any outside Git remote"
            )

            # The important file is absent from HEAD but accessible in history.
            deletion = self.command(
                project, "log", "--format=%H", "--diff-filter=D",
                "--", LEDGER
            )
            self.assertEqual(len(deletion.splitlines()), 1)
            record = self.command(project, "show", f"{deletion}^:{LEDGER}")
            self.assertIn('state = "approved"', record)
            self.assertIn(f'recovery_phrase = "{PHRASE}"', record)

            # The first historical version is not the approved answer.
            creation = self.command(
                project, "log", "--reverse", "--format=%H", "--", LEDGER
            ).splitlines()[0]
            draft = self.command(project, "show", f"{creation}:{LEDGER}")
            self.assertIn('state = "draft"', draft)
            self.assertNotIn(PHRASE, draft)

            # An unrelated deleted document gives students a second lead.
            all_deletions = self.command(
                project, "log", "--all", "--diff-filter=D", "--summary"
            )
            self.assertIn("config/recovery-ledger.toml", all_deletions)
            self.assertIn("docs/temporary-contacts.md", all_deletions)

            # git restore is an optional second path, without changing HEAD.
            original_head = self.command(project, "rev-parse", "HEAD")
            self.command(
                project, "restore", "--source", f"{deletion}^",
                "--", LEDGER
            )
            self.assertIn(PHRASE, (project / LEDGER).read_text(encoding="utf-8"))
            self.assertEqual(
                self.command(project, "rev-parse", "HEAD"), original_head
            )
            self.assertEqual(stat.S_IMODE(project.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE((project / ".git").stat().st_mode), 0o700)

    def test_refuses_overwrite_of_student_work(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / "night-relay"
            folder.mkdir()
            personal = folder / "important-note.txt"
            personal.write_text("Do not remove", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                self.script["build_history"](folder)
            self.assertEqual(personal.read_text(), "Do not remove")

    def test_bundled_real_git_executable_and_offline_source_approval(self):
        bundle = LAB / ".git-runtime.tar.gz"
        self.assertTrue(bundle.is_file())
        self.assertTrue((LAB / ".git-runtime-packages.txt").is_file())
        self.assertTrue((ROOT / "tools/FORGOTTEN_GIT_RUNTIME_LICENSES.md").is_file())
        with tarfile.open(bundle, "r:gz") as tar:
            files = tar.getmembers()
            names = {f.name.lstrip("./") for f in files}
            self.assertIn("git", names)
            self.assertTrue(any(name.startswith("lib/lib") for name in names))
            self.assertFalse(any(f.issym() or f.islnk() for f in files))
            self.assertFalse(any(f.mode & 0o4000 for f in files))
        env = os.environ.copy()
        env["NYITSEC_FORCE_BUNDLED_GIT"] = "1"
        actual = subprocess.run(
            [str(LAB / "bin/git"), "--version"],
            text=True, capture_output=True, timeout=15, env=env,
        )
        self.assertEqual(actual.returncode, 0, actual.stderr)
        self.assertRegex(actual.stdout, r"git version \d+\.\d+")
        self.assertTrue((LAB / "bin/git").stat().st_mode & stat.S_IXUSR)

    def test_checker_and_student_instructions(self):
        checker = runpy.run_path(str(LAB / "verify"), run_name="offline-test")
        self.assertTrue(checker["is_correct"](PHRASE))
        self.assertTrue(checker["is_correct"](PHRASE.upper()))
        self.assertFalse(checker["is_correct"]("pending sign-off"))
        self.assertFalse(checker["is_correct"]("wrong answer"))
        self.assertEqual(
            checker["EXPECTED_SHA256"],
            hashlib.sha256(PHRASE.casefold().encode()).hexdigest(),
        )
        instructions = (LAB / "DESCRIPTION.md").read_text(encoding="utf-8")
        self.assertIn("git log", instructions)
        self.assertIn("git show", instructions)
        self.assertIn("nyitsec-answer", instructions)
        self.assertIn("/nyitsec-ctf", instructions)
        self.assertIn("Reset Challenge", instructions)
        self.assertNotIn(PHRASE, instructions)
        self.assertNotIn(PHRASE, (LAB / "verify").read_text())

    def test_staging_exclusions_init_and_level_three_first_position(self):
        prepare = runpy.run_path(
            str(TEMPLATE / ".workspace.py"), run_name="officer-test"
        )["prepare_workspace"]
        with tempfile.TemporaryDirectory() as temp:
            staged = Path(temp) / "workspace"
            self.assertEqual(prepare(LAB, staged), [])
            self.assertEqual(list(staged.iterdir()), [])
            self.assertEqual(stat.S_IMODE(staged.stat().st_mode), 0o700)

        self.assertEqual(
            (LAB / ".workspace.py").read_bytes(),
            (TEMPLATE / ".workspace.py").read_bytes(),
        )
        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location("validator", ROOT / "scripts/validate_dojo.py")
        validator = module_from_spec(spec)
        spec.loader.exec_module(validator)
        self.assertEqual(
            (LAB / ".init").read_bytes(),
            (TEMPLATE / ".init").read_bytes() + validator.HISTORY_INIT_SUFFIX,
        )
        for name in (
            ".history-builder.py", ".git-prepare.sh",
            ".git-runtime.tar.gz", ".git-runtime-packages.txt",
        ):
            self.assertIn(name, (LAB / ".ctfignore").read_text().splitlines())
        for name in (".init", "verify", "bin/nyitsec-answer", "bin/git"):
            self.assertTrue((LAB / name).stat().st_mode & stat.S_IXUSR)

        startup = (LAB / ".git-prepare.sh").read_text()
        self.assertIn("chmod 600", startup)
        self.assertIn("/run/nyitsec-git", startup)
        self.assertIn("tar -xzf", startup)
        module = yaml.safe_load((ROOT / "level-3/module.yml").read_text())
        self.assertEqual(
            [entry["id"] for entry in module["challenges"]],
            ["forgotten-commit", "packet-detective", "dns-treasure-hunt", "suspicious-script",
             "broken-login"],
        )
        self.assertTrue(
            (ROOT / "docs/its-review/forgotten-commit/README.md").is_file()
        )


if __name__ == "__main__":
    unittest.main()
