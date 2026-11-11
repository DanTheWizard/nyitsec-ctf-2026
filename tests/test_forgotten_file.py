"""Check the randomized, synthetic archive used by The Forgotten File."""

import hashlib
from pathlib import Path
import random
import runpy
import stat
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
CHALLENGE = ROOT / "level-2" / "forgotten-file"
TEMPLATE = ROOT / "templates" / "nyitsec-challenge"
EXPECTED_CODE = "NYITSEC-LOST-26"


class ForgottenFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.setup = runpy.run_path(
            str(CHALLENGE / ".scatter.py"), run_name="offline-test"
        )
        cls.generate = staticmethod(cls.setup["generate_archive"])

    def test_random_location_with_many_realistic_decoys(self):
        locations = set()
        top_level_areas = set()
        for seed in range(18):
            with self.subTest(seed=seed):
                with tempfile.TemporaryDirectory() as tmp:
                    workspace = Path(tmp) / "nyitsec-ctf"
                    workspace.mkdir()
                    target = self.generate(workspace, rng=random.Random(seed))
                    target_path = workspace / target
                    locations.add(str(target))
                    top_level_areas.add(target.parts[0])

                    self.assertTrue(target_path.is_file())
                    self.assertGreaterEqual(len(target.parts), 3)
                    documents = [p for p in workspace.rglob("*") if p.is_file()]
                    folders = [p for p in workspace.rglob("*") if p.is_dir()]
                    self.assertEqual(len(documents), 108)
                    self.assertGreaterEqual(len(folders), 45)
                    self.assertEqual(
                        len({p.parent for p in documents}), 36,
                        "Documents must be scattered across 36 leaf folders",
                    )
                    matches = [
                        p for p in documents
                        if EXPECTED_CODE in p.read_text(encoding="utf-8")
                    ]
                    self.assertEqual(matches, [target_path])
                    self.assertNotIn("secret", target_path.name.lower())
                    self.assertNotIn("answer", target_path.name.lower())

                    self.assertTrue(all(p.stat().st_size > 50 for p in documents))
                    self.assertTrue(
                        all(stat.S_IMODE(p.stat().st_mode) == 0o600
                            for p in documents)
                    )
                    self.assertTrue(
                        all(stat.S_IMODE(p.stat().st_mode) == 0o700
                            for p in folders)
                    )
        self.assertGreaterEqual(
            len(locations), 12,
            "Different launches should select multiple unique filenames/locations",
        )
        self.assertGreaterEqual(
            len(top_level_areas), 5,
            "The clue should not remain in only one top-level directory",
        )

    def test_existing_workspace_contents_are_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "nyitsec-ctf"
            workspace.mkdir()
            original = workspace / "my-script.sh"
            original.write_text("Please keep my script", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                self.generate(workspace, rng=random.Random(42))
            self.assertEqual(original.read_text(), "Please keep my script")
            self.assertEqual(list(workspace.iterdir()), [original])

    def test_rejects_symlink_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            real = Path(tmp) / "real"
            real.mkdir()
            link = Path(tmp) / "link"
            link.symlink_to(real, target_is_directory=True)
            with self.assertRaises(ValueError):
                self.generate(link, rng=random.Random(1))
            self.assertEqual(list(real.iterdir()), [])

    def test_correct_answer_and_unmodified_protected_verifier(self):
        checker = runpy.run_path(str(CHALLENGE / "verify"), run_name="offline-test")
        self.assertEqual(
            checker["EXPECTED_SHA256"],
            hashlib.sha256(EXPECTED_CODE.encode()).hexdigest(),
        )
        check = checker["is_correct"]
        self.assertTrue(check(EXPECTED_CODE))
        self.assertFalse(check(EXPECTED_CODE.lower()))
        self.assertFalse(check("NYITSEC-LOST-25"))
        self.assertFalse(check("wrong"))

        instructions = (CHALLENGE / "DESCRIPTION.md").read_text()
        self.assertIn("/nyitsec-ctf", instructions)
        self.assertIn("find", instructions)
        self.assertIn("grep", instructions)
        self.assertIn("nyitsec-answer", instructions)
        self.assertNotIn(EXPECTED_CODE, instructions)

    def test_generator_remains_outside_student_workspace(self):
        worker = runpy.run_path(
            str(TEMPLATE / ".workspace.py"), run_name="offline-test"
        )["prepare_workspace"]
        with tempfile.TemporaryDirectory() as tmp:
            student = Path(tmp) / "student"
            self.assertEqual(worker(CHALLENGE, student), [])
            self.assertEqual(list(student.iterdir()), [])

        self.assertEqual(
            (CHALLENGE / ".workspace.py").read_bytes(),
            (TEMPLATE / ".workspace.py").read_bytes(),
        )
        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location("validator", ROOT / "scripts/validate_dojo.py")
        validator = module_from_spec(spec)
        spec.loader.exec_module(validator)

        self.assertEqual(
            (CHALLENGE / ".init").read_bytes(),
            (TEMPLATE / ".init").read_bytes()
            + validator.RANDOM_ARCHIVE_INIT_SUFFIX,
        )
        self.assertIn(
            ".scatter.py", (CHALLENGE / ".ctfignore").read_text().splitlines()
        )
        self.assertIn(
            b"chmod 600 /challenge/.scatter.py",
            (CHALLENGE / ".init").read_bytes(),
        )

        module = yaml.safe_load((ROOT / "level-2/module.yml").read_text())
        self.assertEqual(
            [item["id"] for item in module["challenges"]],
            ["misnamed-image", "cookie-metadata", "steg-photo",
             "inspect-source", "forgotten-file"],
        )


if __name__ == "__main__":
    unittest.main()
