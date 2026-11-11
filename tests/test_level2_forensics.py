"""Test the Level 2 cookie-file and genuine steghide evidence challenges."""

from pathlib import Path
import re
import runpy
import shutil
import subprocess
import tarfile
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
COOKIE = ROOT / "level-2" / "cookie-metadata"
PHOTO = ROOT / "level-2" / "steg-photo"
BUNDLE = PHOTO / ".steghide-runtime.tar.gz"


class CookieEvidenceTests(unittest.TestCase):
    def test_cat_visible_recipe_and_strings_recover_trailer(self):
        raw = (COOKIE / "document.txt").read_bytes()
        self.assertIn(b"Chocolate Chip Cookies", raw)
        self.assertIn(b"Instructions", raw)
        self.assertIn(b"350 F", raw)
        self.assertIn(b"\x1b[8m", raw, "ANSI conceal sequence is required")
        self.assertIn(b"\x1b[0m", raw, "ANSI reset prevents hiding the terminal prompt")
        text_before_conceal = raw.split(b"\x1b[8m", 1)[0]
        self.assertNotIn(b"RECOVERY-CODE", text_before_conceal)
        self.assertNotIn(b"COOKIE-TRACE-26", text_before_conceal)
        self.assertIn(b"\x00", raw, "The trailer should not be ordinary plain text")
        self.assertIn(b"RECOVERY-CODE=COOKIE-TRACE-26", raw)
        if shutil.which("strings"):
            proc = subprocess.run(
                ["strings", str(COOKIE / "document.txt")],
                check=True, text=True, capture_output=True,
            )
            self.assertIn("RECOVERY-CODE=COOKIE-TRACE-26", proc.stdout)
            self.assertIn("[NYITSEC-EMBEDDED-METADATA]", proc.stdout)

    def test_cookie_verifier(self):
        check = runpy.run_path(
            str(COOKIE / "verify"), run_name="offline-cookie-test"
        )["is_correct"]
        self.assertTrue(check("COOKIE-TRACE-26"))
        self.assertTrue(check(" COOKIE-TRACE-26 "))
        self.assertFalse(check("cookie-trace-26"))
        self.assertFalse(check("COOKIE-TRACE-27"))
        self.assertFalse(check("Chocolate Chip Cookies"))


class SteghideEvidenceTests(unittest.TestCase):
    def test_jpeg_and_packaged_extractor_are_real(self):
        raw = (PHOTO / "evidence.jpg").read_bytes()
        self.assertTrue(raw.startswith(b"\xff\xd8\xff"), "Must have a real JPEG header")
        self.assertTrue(raw.endswith(b"\xff\xd9"), "Must have a real JPEG footer")
        self.assertGreater(len(raw), 30000)
        self.assertGreater(BUNDLE.stat().st_size, 100000)

        with tarfile.open(BUNDLE, "r:gz") as tar:
            members = tar.getmembers()
            names = {m.name.lstrip("./") for m in members}
            self.assertIn("steghide", names)
            self.assertTrue(any(s.startswith("lib/libmcrypt") for s in names))
            self.assertTrue(any(s.startswith("lib/libmhash") for s in names))
            self.assertFalse(any(m.issym() or m.islnk() for m in members))
            self.assertFalse(any(m.mode & 0o4000 for m in members), "No setuid binary")

    def test_steg_tools_extract_real_hidden_file(self):
        wrapper = PHOTO / "bin" / "steghide"
        with tempfile.TemporaryDirectory() as folder:
            extracted = Path(folder) / "recovered.txt"
            process = subprocess.run(
                [str(wrapper), "extract", "-sf", str(PHOTO / "evidence.jpg"),
                 "-p", "cookie-jar", "-xf", str(extracted), "-f"],
                capture_output=True, text=True, timeout=45,
            )
            self.assertEqual(process.returncode, 0, process.stderr)
            note = extracted.read_text(encoding="utf-8")
            self.assertIn("NYITSec Evidence Review", note)
            match = re.search(r"^Response code: ([A-Z0-9-]+)$", note, re.MULTILINE)
            self.assertIsNotNone(match, "The embedded document should have a code")

            verifier = runpy.run_path(
                str(PHOTO / "verify"), run_name="offline-stego-test"
            )["is_correct"]
            self.assertTrue(verifier(match.group(1)))
            self.assertFalse(verifier("wrong"))
            self.assertFalse(verifier(match.group(1).lower()))
            self.assertFalse(verifier("cookie-jar"))

            wrong = subprocess.run(
                [str(wrapper), "extract", "-sf", str(PHOTO / "evidence.jpg"),
                 "-p", "wrong-passphrase", "-xf", str(Path(folder) / "bad.txt"), "-f"],
                capture_output=True, text=True, timeout=45,
            )
            self.assertNotEqual(wrong.returncode, 0)

    def test_only_student_facing_files_are_staged(self):
        copier = runpy.run_path(
            str(ROOT / "templates" / "nyitsec-challenge" / ".workspace.py"),
            run_name="test-copier",
        )["prepare_workspace"]
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder) / "workspace"
            copied = copier(PHOTO, dest)
            self.assertEqual(set(copied), {"case-note.txt", "evidence.jpg"})
            self.assertFalse((dest / ".steghide-runtime.tar.gz").exists())
            self.assertFalse((dest / "verify").exists())
            self.assertFalse((dest / "bin").exists())

    def test_level_two_order_and_student_hint(self):
        module = yaml.safe_load((ROOT / "level-2" / "module.yml").read_text())
        self.assertEqual(
            [x["id"] for x in module["challenges"]],
            ["misnamed-image", "cookie-metadata", "steg-photo", "inspect-source"],
        )
        cookie_desc = (COOKIE / "DESCRIPTION.md").read_text()
        self.assertNotIn("strings", cookie_desc.lower())
        self.assertIn("hidden", cookie_desc.lower())
        photo_desc = (PHOTO / "DESCRIPTION.md").read_text()
        self.assertIn("steghide", photo_desc.lower())
        self.assertIn("nyitsec-answer", photo_desc)


if __name__ == "__main__":
    unittest.main()
