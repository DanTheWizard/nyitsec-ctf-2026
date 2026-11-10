"""Verify the first Level 2 challenge is a real, disguised PNG image."""

import hashlib
from pathlib import Path
import runpy
import struct
import unittest
import zlib

import yaml


ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "level-2" / "misnamed-image"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


class MisnamedImageTests(unittest.TestCase):
    def test_png_content_masquerades_as_txt(self):
        path = FOLDER / "notice.txt"
        raw = path.read_bytes()
        self.assertEqual(path.suffix, ".txt")
        self.assertTrue(raw.startswith(PNG_MAGIC))
        self.assertNotIn(b"ThePassword#LOL", raw, "The phrase should only be in image pixels")

        offset = len(PNG_MAGIC)
        chunks = {}
        while offset < len(raw):
            size = struct.unpack(">I", raw[offset:offset + 4])[0]
            kind = raw[offset + 4:offset + 8]
            data = raw[offset + 8:offset + 8 + size]
            crc = struct.unpack(">I", raw[offset + 8 + size:offset + 12 + size])[0]
            self.assertEqual(zlib.crc32(kind + data), crc)
            chunks.setdefault(kind, []).append(data)
            offset += size + 12
        self.assertEqual(offset, len(raw))
        self.assertIn(b"IHDR", chunks)
        self.assertIn(b"IDAT", chunks)
        self.assertIn(b"IEND", chunks)
        width, height = struct.unpack(">II", chunks[b"IHDR"][0][:8])
        self.assertGreaterEqual(width, 500)
        self.assertGreaterEqual(height, 200)
        self.assertTrue(zlib.decompress(b"".join(chunks[b"IDAT"])))

    def test_verifier_accepts_only_exact_phrase(self):
        verifier = runpy.run_path(str(FOLDER / "verify"), run_name="offline-check")
        check = verifier["is_correct"]
        self.assertTrue(check("ThePassword#LOL"))
        self.assertFalse(check("thepassword#lol"))
        self.assertFalse(check("ThePasswordLOL"))
        self.assertFalse(check("ThePassword#LOLx"))
        self.assertFalse(check("wrong"))
        self.assertEqual(
            verifier["EXPECTED_SHA256"],
            hashlib.sha256(b"ThePassword#LOL").hexdigest(),
        )

    def test_level_2_is_after_fundamentals_and_workspace_is_standard(self):
        config = yaml.safe_load((ROOT / "dojo.yml").read_text())
        self.assertEqual(
            [m["id"] for m in config["modules"]],
            ["linux-cli-intro", "fundamentals", "level-2"],
        )
        module = yaml.safe_load((ROOT / "level-2" / "module.yml").read_text())
        self.assertEqual(module["challenges"][0]["id"], "misnamed-image")
        self.assertIn("nyitsec-answer", (FOLDER / "DESCRIPTION.md").read_text())
        self.assertIn("/nyitsec-ctf", (FOLDER / "DESCRIPTION.md").read_text())
        for name in (".init", ".workspace.py", ".ctfignore"):
            self.assertEqual(
                (FOLDER / name).read_bytes(),
                (ROOT / "templates" / "nyitsec-challenge" / name).read_bytes(),
            )


if __name__ == "__main__":
    unittest.main()
