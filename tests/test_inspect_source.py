"""Test the isolated Level 2 website and its approved startup extension."""

from html.parser import HTMLParser
from http.server import HTTPServer
from pathlib import Path
import hashlib
import re
import runpy
import stat
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

import yaml


ROOT = Path(__file__).resolve().parents[1]
CHALLENGE = ROOT / "level-2" / "inspect-source"
TEMPLATE = ROOT / "templates" / "nyitsec-challenge"
CODE = "NYITSEC-SOURCE-26"


class VisibleTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.comments = []
        self.content = []
        self.ignore = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self.ignore += 1

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self.ignore -= 1

    def handle_data(self, data):
        if not self.ignore:
            self.content.append(data)

    def handle_comment(self, data):
        self.comments.append(data)


class InspectSourceTests(unittest.TestCase):
    def test_serves_page_and_secret_only_in_comment(self):
        website = runpy.run_path(str(CHALLENGE / ".website.py"), run_name="unit-test")
        server = HTTPServer(("127.0.0.1", 0), website["SiteHandler"])
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f"http://127.0.0.1:{server.server_address[1]}"
            with urllib.request.urlopen(url + "/", timeout=3) as response:
                self.assertEqual(response.status, 200)
                self.assertTrue(response.headers["Content-Type"].startswith("text/html"))
                html = response.read().decode("utf-8")

            text = VisibleTextParser()
            text.feed(html)
            self.assertIn("Harborview Learning Center", "".join(text.content))
            self.assertNotIn(CODE, "".join(text.content))
            self.assertIn(CODE, "\n".join(text.comments))
            self.assertIn("HTML source comments are public", "\n".join(text.comments))

            with urllib.request.urlopen(url + "/index.html", timeout=3) as response:
                self.assertEqual(response.status, 200)
            with self.assertRaises(urllib.error.HTTPError) as raised:
                urllib.request.urlopen(url + "/.website.py", timeout=3)
            self.assertEqual(raised.exception.code, 404)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

    def test_answer_verifier_and_no_plaintext_solution_in_student_page(self):
        checker = runpy.run_path(str(CHALLENGE / "verify"), run_name="unit-test")
        self.assertEqual(
            checker["EXPECTED_SHA256"],
            hashlib.sha256(CODE.encode()).hexdigest(),
        )
        self.assertTrue(checker["is_correct"](CODE))
        self.assertFalse(checker["is_correct"](CODE.lower()))
        self.assertFalse(checker["is_correct"]("wrong-code"))
        self.assertFalse(checker["is_correct"]("NYITSEC-SOURCE-27"))

        instructions = (CHALLENGE / "DESCRIPTION.md").read_text()
        self.assertIn("Desktop", instructions)
        self.assertIn("Firefox", instructions)
        self.assertIn("http://127.0.0.1:8765/", instructions)
        self.assertIn("Ctrl+U", instructions)
        self.assertIn("nyitsec-answer", instructions)
        self.assertNotIn(CODE, instructions)

    def test_source_excluded_and_standard_workspace_preserved(self):
        setup = runpy.run_path(
            str(TEMPLATE / ".workspace.py"), run_name="unit-test"
        )["prepare_workspace"]
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "working"
            files = setup(CHALLENGE, dest)
            self.assertEqual(files, [])
            self.assertEqual(list(dest.iterdir()), [])
            self.assertEqual(stat.S_IMODE(dest.stat().st_mode), 0o700)

        self.assertEqual(
            (CHALLENGE / ".workspace.py").read_bytes(),
            (TEMPLATE / ".workspace.py").read_bytes(),
        )
        self.assertTrue((CHALLENGE / ".init").stat().st_mode & stat.S_IXUSR)
        self.assertTrue((CHALLENGE / "verify").stat().st_mode & stat.S_IXUSR)
        self.assertTrue(
            (CHALLENGE / "bin/nyitsec-answer").stat().st_mode & stat.S_IXUSR
        )
        ignore = (CHALLENGE / ".ctfignore").read_text().splitlines()
        self.assertIn(".website.py", ignore)
        self.assertIn(".website-start.sh", ignore)

    def test_approved_extension_and_server_lifecycle(self):
        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location("validator", ROOT / "scripts/validate_dojo.py")
        validator = module_from_spec(spec)
        spec.loader.exec_module(validator)

        original = (TEMPLATE / ".init").read_bytes()
        actual = (CHALLENGE / ".init").read_bytes()
        self.assertEqual(actual, original + validator.WEB_INIT_SUFFIX)
        self.assertIn(b"/challenge/.website-start.sh", actual)
        startup = (CHALLENGE / ".website-start.sh").read_text()
        self.assertIn("chmod 600 /challenge/.website.py", startup)
        self.assertIn("nohup /usr/local/bin/python -I", startup)
        self.assertIn("urllib.request.urlopen", startup)
        self.assertIn("http://127.0.0.1:8765/", startup)

        website = (CHALLENGE / ".website.py").read_text()
        self.assertIn('HOST = "127.0.0.1"', website)
        self.assertIn("os.setuid(1000)", website)

        module = yaml.safe_load((ROOT / "level-2/module.yml").read_text())
        self.assertEqual(
            [entry["id"] for entry in module["challenges"]],
            ["misnamed-image", "cookie-metadata", "steg-photo", "inspect-source"],
        )


if __name__ == "__main__":
    unittest.main()
