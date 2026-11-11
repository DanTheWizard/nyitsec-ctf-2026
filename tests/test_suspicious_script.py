"""Integration tests for The Suspicious Script's safe static-analysis lesson."""

import ast
from contextlib import redirect_stdout
import hashlib
from http.client import HTTPConnection
import io
import os
from pathlib import Path
import runpy
import stat
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import urlopen

import yaml


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "level-3" / "suspicious-script"
TEMPLATE = ROOT / "templates" / "nyitsec-challenge"
PORT = 8876
EXPECTED = "IKnowPythonDeobfuscation#404"
JOKE = "You had one job... Not to execute the script lol"


class SuspiciousScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blob = (LAB / ".payload.bin").read_bytes()
        factory = runpy.run_path(
            str(LAB / ".payload-service.py"), run_name="unit-test"
        )
        cls.server = factory["create_server"](port=PORT, payload=cls.blob)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def test_actual_local_http_endpoint_serves_only_encoded_bytes(self):
        with urlopen(f"http://127.0.0.1:{PORT}/assets/payload.bin", timeout=3) as res:
            self.assertEqual(res.status, 200)
            self.assertEqual(res.headers["Content-Type"], "application/octet-stream")
            raw = res.read()
        self.assertEqual(raw, self.blob)
        self.assertTrue(raw.startswith(b"LAB1"))
        self.assertNotIn(EXPECTED.encode(), raw)
        self.assertNotIn(JOKE.encode(), raw)
        with self.assertRaises(HTTPError) as missing:
            urlopen(f"http://127.0.0.1:{PORT}/.payload-service.py", timeout=3)
        self.assertEqual(missing.exception.code, 404)

    def test_script_can_be_analyzed_without_execution(self):
        script = LAB / "audit_sync.py"
        text = script.read_text(encoding="utf-8")
        parsed = ast.parse(text, filename=str(script))
        self.assertIsInstance(parsed, ast.Module)
        self.assertNotIn(EXPECTED, text)
        self.assertNotIn(JOKE, text)
        self.assertNotIn("http://127.0.0.1", text)
        self.assertIn("if __name__ == \"__main__\":", text)
        self.assertIn("exec(compile(", text)

        original = runpy.run_path(str(script), run_name="analysis_only")
        self.assertEqual(
            original["_r"](),
            f"http://127.0.0.1:{PORT}/assets/payload.bin"
        )
        reconstructed = original["_q"](self.blob).decode("utf-8")
        ast.parse(reconstructed)
        self.assertIn(f'analysis_note = "Your flag answer: {EXPECTED}"', reconstructed)
        self.assertIn(JOKE, reconstructed)
        self.assertIn('if __name__ == "__main__":', reconstructed)

    def test_its_review_source_matches_exact_payload_bytes(self):
        """The human-readable ITS source must never drift from the real binary."""
        review_path = (
            ROOT / "docs" / "its-review" / "suspicious-script"
            / "recovered_payload.py"
        )
        review_source = review_path.read_bytes()
        self.assertEqual(
            hashlib.sha256(self.blob).hexdigest(),
            "b97384863de80d84b7b011943d220df3e2e23f55e4e0d266fc0cfe9f752e1cd8",
        )
        self.assertEqual(
            hashlib.sha256(review_source).hexdigest(),
            "2d3b191c0db4bda2b59c2396a2ba38455471e5db4b7fab9373fcf09e3eeb7042",
        )
        decoder = runpy.run_path(
            str(LAB / "audit_sync.py"), run_name="analysis_only"
        )["_q"]
        self.assertEqual(decoder(self.blob), review_source)
        recovered_ast = ast.parse(review_source.decode("utf-8"))
        self.assertFalse(
            any(isinstance(node, (ast.Import, ast.ImportFrom))
                for node in ast.walk(recovered_ast)),
            "The documented recovered payload must not contain imports",
        )
        self.assertFalse(review_path.is_relative_to(LAB))
        self.assertFalse(
            (LAB / "recovered_payload.py").exists(),
            "The readable ITS review source must not appear in the challenge folder",
        )

    def test_running_script_officer_only_downloads_blob_and_prints_joke(self):
        with tempfile.TemporaryDirectory() as temp:
            env = os.environ.copy()
            env["TMPDIR"] = temp
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            completed = subprocess.run(
                [sys.executable, str(LAB / "audit_sync.py")],
                env=env, text=True, capture_output=True, timeout=10,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(completed.stdout.strip(), JOKE)
            self.assertNotIn(EXPECTED, completed.stdout)
            saved = Path(temp) / "payload.bin"
            self.assertEqual(saved.read_bytes(), self.blob)
            self.assertEqual({p.name for p in Path(temp).iterdir()}, {"payload.bin"})

    def test_checker_requires_both_answers_without_leaking_which_is_wrong(self):
        verifier = runpy.run_path(str(LAB / "verify"), run_name="unit-test")
        check = verifier["is_correct"]
        self.assertEqual(len(verifier["OPTIONS"]), 6)
        self.assertTrue(check("B", EXPECTED))
        self.assertTrue(check("b", f" {EXPECTED} "))
        self.assertFalse(check("A", EXPECTED))
        self.assertFalse(check("C", EXPECTED))
        self.assertFalse(check("D", EXPECTED))
        self.assertFalse(check("E", EXPECTED))
        self.assertFalse(check("F", EXPECTED))
        self.assertFalse(check("B", "IKnowPythonDeobfuscation#405"))
        self.assertFalse(check("B", EXPECTED.lower()))
        self.assertFalse(check("A", "wrong"))

        choices = " ".join(text for _, text in verifier["OPTIONS"])
        self.assertNotIn("payload.bin", choices)
        self.assertNotIn("8876", choices)
        self.assertNotIn("assets/", choices)
        self.assertNotIn(EXPECTED, (LAB / "verify").read_text())

        def response_for(choice, answer):
            out = io.StringIO()
            with patch("builtins.input", side_effect=[choice, answer]):
                with redirect_stdout(out):
                    verifier["main"]()
            return out.getvalue()

        mistakes = [
            response_for("A", EXPECTED),
            response_for("B", "wrong"),
            response_for("D", "wrong"),
        ]
        self.assertEqual(mistakes[0], mistakes[1])
        self.assertEqual(mistakes[1], mistakes[2])
        self.assertIn("One or more answers are incorrect", mistakes[0])
        self.assertNotIn("pwn.college{", mistakes[0])

        with patch.object(Path, "read_text", return_value="pwn.college{synthetic-test}\n"):
            success = response_for("B", EXPECTED)
        self.assertIn("pwn.college{synthetic-test}", success)
        self.assertNotIn("One or more answers are incorrect", success)

    def test_exact_startup_and_student_workspace_exclusions(self):
        prepare = runpy.run_path(
            str(TEMPLATE / ".workspace.py"), run_name="unit-test"
        )["prepare_workspace"]
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / "workspace"
            staged = prepare(LAB, dest)
            self.assertEqual(staged, ["audit_sync.py"])
            self.assertEqual({p.name for p in dest.iterdir()}, {"audit_sync.py"})
            self.assertEqual(stat.S_IMODE(dest.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE((dest / "audit_sync.py").stat().st_mode), 0o600)
            for hidden in (".payload.bin", ".payload-service.py", ".payload-start.sh"):
                self.assertFalse((dest / hidden).exists())

        self.assertEqual(
            (LAB / ".workspace.py").read_bytes(),
            (TEMPLATE / ".workspace.py").read_bytes(),
        )
        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location("validator", ROOT / "scripts/validate_dojo.py")
        validation = module_from_spec(spec)
        spec.loader.exec_module(validation)
        self.assertEqual(
            (LAB / ".init").read_bytes(),
            (TEMPLATE / ".init").read_bytes() + validation.PAYLOAD_INIT_SUFFIX,
        )
        for executable in (".init", "verify", "bin/nyitsec-answer"):
            self.assertTrue((LAB / executable).stat().st_mode & stat.S_IXUSR)
        service = (LAB / ".payload-start.sh").read_text()
        self.assertIn("chmod 600", service)
        self.assertIn("http://127.0.0.1:8876", service)

    def test_level_three_order_and_minimal_student_hints(self):
        module = yaml.safe_load((ROOT / "level-3/module.yml").read_text())
        self.assertEqual(
            [item["id"] for item in module["challenges"]],
            ["dns-treasure-hunt", "suspicious-script", "broken-login"],
        )
        instructions = (LAB / "DESCRIPTION.md").read_text()
        self.assertIn("/nyitsec-ctf", instructions)
        self.assertIn("nyitsec-answer", instructions)
        self.assertIn("without", instructions.lower())
        self.assertNotIn(EXPECTED, instructions)
        self.assertNotIn("Your flag answer:", instructions)


if __name__ == "__main__":
    unittest.main()
