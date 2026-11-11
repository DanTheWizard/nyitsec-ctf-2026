"""Tests for NYITSec's challenge generator and YAML validator."""

import importlib.util
from pathlib import Path
import stat
import tempfile
import unittest

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def import_script(name: str):
    spec = importlib.util.spec_from_file_location(name, PROJECT_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


scaffold = import_script("new_challenge")
validate = import_script("validate_dojo")


class ScaffoldTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name)
        (self.root / "dojo.yml").write_text(
            "id: example\nmodules:\n  - id: linux-cli-intro\n  - id: fundamentals\n",
            encoding="utf-8",
        )
        (self.root / "fundamentals").mkdir()
        (self.root / "fundamentals" / "module.yml").write_text(
            "name: CTF Fundamentals\nchallenges: []\n", encoding="utf-8",
        )
        (self.root / "linux-cli-intro").mkdir()
        (self.root / "linux-cli-intro" / "module.yml").write_text(
            "name: Linux Intro\nchallenges: []\n", encoding="utf-8",
        )

    def test_scaffolds_existing_module(self):
        path = scaffold.create_challenge(
            self.root, "fundamentals", "first-task", "First Task",
        )
        for relative in [".init", "verify", "bin/nyitsec-answer"]:
            self.assertTrue((path / relative).is_file(), relative)
            self.assertTrue((path / relative).stat().st_mode & stat.S_IXUSR, relative)

        for relative in [".workspace.py", ".ctfignore"]:
            self.assertTrue((path / relative).is_file(), relative)
        self.assertIn("/nyitsec-ctf", (path / ".init").read_text(encoding="utf-8"))
        self.assertIn("/challenge/.workspace.py", (path / ".init").read_text(encoding="utf-8"))
        self.assertIn("PROTECTED_NAMES", (path / ".workspace.py").read_text(encoding="utf-8"))

        description = (path / "DESCRIPTION.md").read_text(encoding="utf-8")
        self.assertIn("First Task", description)
        self.assertIn("nyitsec-answer", description)
        self.assertIn("return False", (path / "verify").read_text(encoding="utf-8"))

        module = yaml.safe_load((self.root / "fundamentals/module.yml").read_text())
        self.assertEqual(module["challenges"][0]["id"], "first-task")
        self.assertEqual(
            [m["id"] for m in yaml.safe_load((self.root / "dojo.yml").read_text())["modules"]],
            ["linux-cli-intro", "fundamentals"],
        )

    def test_duplicate_rejected_without_side_effects(self):
        scaffold.create_challenge(self.root, "fundamentals", "first-task", "First Task")
        with self.assertRaises(FileExistsError):
            scaffold.create_challenge(self.root, "fundamentals", "first-task", "First Task")

    def test_creates_module_and_appends_after_fundamentals(self):
        path = scaffold.create_challenge(
            self.root, "web-basics", "first-http", "First HTTP",
            new_module_name="Web Security Basics",
        )
        self.assertTrue((path / "bin/nyitsec-answer").exists())
        modules = yaml.safe_load((self.root / "dojo.yml").read_text())["modules"]
        self.assertEqual([m["id"] for m in modules],
                         ["linux-cli-intro", "fundamentals", "web-basics"])

    def test_ungraded_intro_rejected(self):
        with self.assertRaises(ValueError):
            scaffold.create_challenge(self.root, "linux-cli-intro", "test", "Test")

    def test_validator_rejects_unfinished_scaffold(self):
        scaffold.create_challenge(self.root, "fundamentals", "pending", "Pending")
        issues = validate.check_repository(self.root)
        self.assertTrue(any("replace TODO" in x for x in issues))
        self.assertTrue(any("implement and remove TODO" in x for x in issues))

    def test_validator_allows_completed_scaffold(self):
        folder = scaffold.create_challenge(
            self.root, "fundamentals", "complete", "Complete",
        )
        desc = folder / "DESCRIPTION.md"
        desc.write_text(desc.read_text().replace(
            "TODO: Describe the student's task and which files to inspect.",
            "Practice inspecting a sample file."),
            encoding="utf-8",
        )
        verifier = folder / "verify"
        verifier.write_text(verifier.read_text().replace(
            "# TODO: Implement a challenge-specific, safe verification strategy.\n    return False",
            "return answer == 'example-test-answer'"),
            encoding="utf-8",
        )
        self.assertEqual(validate.check_repository(self.root), [])

    def test_validator_detects_missing_workspace_setup(self):
        path = scaffold.create_challenge(self.root, "fundamentals", "missing", "Missing")
        (path / ".workspace.py").unlink()
        issues = validate.check_repository(self.root)
        self.assertTrue(any("missing .workspace.py" in x for x in issues))

    def test_validator_detects_template_drift(self):
        path = scaffold.create_challenge(self.root, "fundamentals", "drift", "Drift")
        setup = path / ".init"
        setup.write_text(setup.read_text() + "\n# accidental drift\n")
        issues = validate.check_repository(self.root)
        self.assertTrue(any(".init differs from standard template" in x for x in issues))

    def test_validator_accepts_controlled_web_init_extension(self):
        path = scaffold.create_challenge(
            self.root, "fundamentals", "local-site", "Local Site",
        )
        (path / ".website.py").write_text("# test site\n", encoding="utf-8")
        (path / ".website-start.sh").write_text("# test startup\n", encoding="utf-8")
        init = path / ".init"
        init.write_bytes(init.read_bytes() + validate.WEB_INIT_SUFFIX)
        issues = validate.check_repository(self.root)
        self.assertFalse(
            any(".init differs from standard template" in problem for problem in issues),
            issues,
        )

    def test_validator_rejects_web_init_when_setup_file_missing(self):
        path = scaffold.create_challenge(
            self.root, "fundamentals", "missing-site", "Missing Site",
        )
        init = path / ".init"
        init.write_bytes(init.read_bytes() + validate.WEB_INIT_SUFFIX)
        issues = validate.check_repository(self.root)
        self.assertTrue(
            any(".init differs from standard template" in problem for problem in issues)
        )

    def test_validator_accepts_controlled_random_archive_init(self):
        path = scaffold.create_challenge(
            self.root, "fundamentals", "random-archive", "Random Archive",
        )
        (path / ".scatter.py").write_text("# synthetic generator\n", encoding="utf-8")
        ignore = path / ".ctfignore"
        ignore.write_text(ignore.read_text() + "\n.scatter.py\n")
        init = path / ".init"
        init.write_bytes(init.read_bytes() + validate.RANDOM_ARCHIVE_INIT_SUFFIX)
        issues = validate.check_repository(self.root)
        self.assertFalse(
            any(".init differs from standard template" in problem for problem in issues),
            issues,
        )

    def test_validator_rejects_unexcluded_random_generator(self):
        path = scaffold.create_challenge(
            self.root, "fundamentals", "leaky-archive", "Leaky Archive",
        )
        (path / ".scatter.py").write_text("# synthetic generator\n", encoding="utf-8")
        init = path / ".init"
        init.write_bytes(init.read_bytes() + validate.RANDOM_ARCHIVE_INIT_SUFFIX)
        issues = validate.check_repository(self.root)
        self.assertTrue(any(".init differs from standard template" in p for p in issues))

    def test_validator_rejects_duplicate_yaml_keys(self):
        (self.root / "fundamentals/module.yml").write_text(
            "name: Intro\nname: Duplicate\nchallenges: []\n", encoding="utf-8",
        )
        issues = validate.check_repository(self.root)
        self.assertTrue(any("Duplicate YAML key" in x for x in issues))


if __name__ == "__main__":
    unittest.main()
