"""End-to-end tests for the intentionally vulnerable, localhost-only NYITSec forum."""

from contextlib import closing
from http.cookiejar import CookieJar
from pathlib import Path
import hashlib
import os
import re
import runpy
import sqlite3
import stat
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import (
    HTTPCookieProcessor, ProxyHandler, Request, build_opener
)

import yaml


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "level-3" / "broken-login"
TEMPLATE = ROOT / "templates" / "nyitsec-challenge"
CODE = "OrbitingToaster#73"
ADMIN = "CopperGate!26"
STACKED_SQL = "a@example.test', '2026-11-11'); DROP TABLE signup_queue; --"
PASSWORD_BYPASS = "' OR '1'='1' --"
UNION_SEARCH = "x%' UNION SELECT username,password FROM users --"


class ForumTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db_path = Path(self.temp.name) / "forum.sqlite3"
        self.code = runpy.run_path(str(LAB / ".forum-app.py"), run_name="unit-test")
        self.code["seed_database"](self.db_path)
        self.server = self.code["create_server"](
            host="127.0.0.1", port=0, db_path=self.db_path
        )
        self.thread = threading.Thread(
            target=self.server.serve_forever, daemon=True
        )
        self.thread.start()
        self.addCleanup(self.stop)
        self.base = f"http://127.0.0.1:{self.server.server_port}"
        self.opener = build_opener(ProxyHandler({}), HTTPCookieProcessor(CookieJar()))

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def get(self, path="/", opener=None, host=None):
        header = {"Host": host} if host else {}
        req = Request(self.base + path, headers=header)
        with (opener or self.opener).open(req, timeout=5) as response:
            return response.read().decode("utf-8"), response.status

    def post(self, path, fields, opener=None):
        req = Request(
            self.base + path, data=urlencode(fields).encode("utf-8"),
            method="POST",
        )
        with (opener or self.opener).open(req, timeout=5) as response:
            return response.read().decode("utf-8"), response.status

    def db(self):
        return sqlite3.connect(self.db_path)

    def login(self, password, username="admin"):
        return self.post("/login", {"username": username, "password": password})

    def queue_exists(self):
        with closing(self.db()) as db:
            return self.code["table_exists"](db, "signup_queue")

    def confirm_nuke(self):
        page, status = self.get("/admin/nuke")
        self.assertEqual(status, 200)
        self.assertIn("Are you absolutely sure", page)
        match = re.search(
            r'name="confirm" value="([A-Za-z0-9_-]+)"', page
        )
        self.assertIsNotNone(match)
        return self.post("/admin/nuke", {"confirm": match.group(1)})

    def test_initial_forum_looks_real_and_uses_only_fictional_data(self):
        page, status = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn("NYITSEC", page)
        self.assertIn("SUPER SECURE", page)
        self.assertIn("Underground", page)
        self.assertIn("Keyboard Switch Debate", page)
        self.assertIn("signup queue", page.lower())
        self.assertNotIn(CODE, page)

        login, status = self.get("/login")
        self.assertEqual(status, 200)
        self.assertIn('name="password"', login)
        self.assertIn('name="username"', login)

        signup, status = self.get("/queue")
        self.assertEqual(status, 200)
        self.assertIn('name="email"', signup)

        thread, status = self.get("/thread?id=1")
        self.assertEqual(status, 200)
        self.assertIn("Welcome to the NYITSec Underground", thread)

        results, status = self.get("/search?q=keyboard")
        self.assertEqual(status, 200)
        self.assertIn("Keyboard Switch Debate", results)
        self.assertNotIn(CODE, results)

        with closing(self.db()) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM posts").fetchone()[0], 12)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM users").fetchone()[0], 5)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM signup_queue").fetchone()[0], 5)

    def test_queue_sqli_then_password_sqli_then_confirmed_nuke(self):
        # Direct Nuke access and guessed passwords must fail before auth.
        with self.assertRaises(HTTPError) as unauth:
            self.get("/admin/nuke")
        self.assertEqual(unauth.exception.code, 403)
        failed, _ = self.login("incorrect")
        self.assertIn("Login failed", failed)
        self.assertNotIn("Nuke Forum</a>", failed)

        normal, _ = self.post("/queue", {"email": "normal@example.test"})
        self.assertIn("Added to the fictional waiting list", normal)
        with closing(self.db()) as db:
            self.assertEqual(
                db.execute("SELECT COUNT(*) FROM signup_queue").fetchone()[0], 6
            )

        # INTENTIONALLY VULNERABLE: stacked SQL deletes *only* synthetic queue.
        dropped, status = self.post("/queue", {"email": STACKED_SQL})
        self.assertEqual(status, 200)
        self.assertFalse(self.queue_exists())

        authenticated, status = self.login(PASSWORD_BYPASS)
        self.assertEqual(status, 200)
        self.assertIn("Welcome, admin!", authenticated)
        self.assertIn("Nuke Forum", authenticated)
        self.assertNotIn(CODE, authenticated)

        # First click renders a server-side confirmation page.
        confirm_page, status = self.get("/admin/nuke")
        self.assertEqual(status, 200)
        self.assertIn("Are you absolutely sure", confirm_page)
        self.assertNotIn(CODE, confirm_page)

        completed, status = self.confirm_nuke()
        self.assertEqual(status, 200)
        self.assertIn("Forum successfully nuked", completed)
        self.assertIn(CODE, completed)
        self.assertIn("nyitsec-answer", completed)

        with closing(self.db()) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM posts").fetchone()[0], 0)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM users").fetchone()[0], 5)
            self.assertTrue(self.code["is_nuked"](db))
        after, _ = self.get("/")
        self.assertIn("Simulation complete", after)
        self.assertNotIn(CODE, after)

    def test_nuke_interlock_requires_drop_even_if_admin_is_legitimate(self):
        authenticated, _ = self.login(ADMIN)
        self.assertIn("Welcome, admin!", authenticated)
        blocked, status = self.confirm_nuke()
        self.assertEqual(status, 200)
        self.assertIn("signup waiting queue still", blocked)
        self.assertNotIn(CODE, blocked)
        with closing(self.db()) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM posts").fetchone()[0], 12)

        # A repeated POST without a fresh confirmation cannot bypass the gate.
        with self.assertRaises(HTTPError) as denied:
            self.post("/admin/nuke", {"confirm": "made-up-confirmation"})
        self.assertEqual(denied.exception.code, 403)

    def test_optional_union_search_can_reveal_fake_admin_credentials(self):
        import urllib.parse
        result, status = self.get("/search?q=" + urllib.parse.quote(UNION_SEARCH))
        self.assertEqual(status, 200)
        self.assertIn("CopperGate!26", result)
        self.assertIn("admin", result)
        authenticated, _ = self.login(ADMIN)
        self.assertIn("Welcome, admin!", authenticated)
        # Alternative legitimate login still needs the fictional queue disabled.
        self.post("/queue", {"email": STACKED_SQL})
        completed, status = self.confirm_nuke()
        self.assertEqual(status, 200)
        self.assertIn(CODE, completed)

    def test_no_cross_origin_nuke_or_host_rebinding(self):
        with self.assertRaises(HTTPError) as exception:
            self.get("/", host="outside.example:80")
        self.assertEqual(exception.exception.code, 421)

        with self.assertRaises(HTTPError) as nuke:
            self.post("/admin/nuke", {"confirm": "anything"})
        self.assertEqual(nuke.exception.code, 403)

        page, _ = self.get("/", host=f"nyitsecwebsite.test:{self.server.server_port}")
        self.assertIn("SUPER SECURE", page)
        self.assertNotIn(CODE, page)

    def test_reset_reseeds_fictional_database(self):
        self.post("/queue", {"email": STACKED_SQL})
        self.login(PASSWORD_BYPASS)
        self.confirm_nuke()
        reset_db = Path(self.temp.name) / "after-reset.sqlite3"
        self.code["seed_database"](reset_db)
        with closing(sqlite3.connect(reset_db)) as db:
            self.assertTrue(self.code["table_exists"](db, "signup_queue"))
            self.assertEqual(db.execute("SELECT COUNT(*) FROM signup_queue").fetchone()[0], 5)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM posts").fetchone()[0], 12)
            self.assertFalse(self.code["is_nuked"](db))

    def test_checker_and_compartmentalization(self):
        verifier = runpy.run_path(str(LAB / "verify"), run_name="offline-test")
        check = verifier["is_correct"]
        self.assertTrue(check(CODE))
        self.assertFalse(check(CODE.lower()))
        self.assertFalse(check("another-guess"))
        self.assertEqual(
            verifier["EXPECTED_SHA256"],
            hashlib.sha256(CODE.encode()).hexdigest(),
        )
        self.assertNotIn(CODE, (LAB / "DESCRIPTION.md").read_text())
        self.assertNotIn(CODE, (LAB / "verify").read_text())

        copier = runpy.run_path(
            str(TEMPLATE / ".workspace.py"), run_name="offline-test"
        )["prepare_workspace"]
        with tempfile.TemporaryDirectory() as destination:
            out = Path(destination) / "ctf"
            self.assertEqual(copier(LAB, out), [])
            self.assertEqual(list(out.iterdir()), [])
            self.assertEqual(stat.S_IMODE(out.stat().st_mode), 0o700)

        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location("validator", ROOT / "scripts/validate_dojo.py")
        val = module_from_spec(spec)
        spec.loader.exec_module(val)
        self.assertEqual(
            (LAB / ".init").read_bytes(),
            (TEMPLATE / ".init").read_bytes() + val.FORUM_INIT_SUFFIX,
        )
        self.assertIn("nyitsecwebsite.test", (LAB / ".forum-start.sh").read_text())
        self.assertIn("/etc/hosts", (LAB / ".forum-start.sh").read_text())
        self.assertIn("chmod 600", (LAB / ".forum-start.sh").read_text())
        self.assertTrue((LAB / ".init").stat().st_mode & stat.S_IXUSR)
        self.assertTrue((LAB / "verify").stat().st_mode & stat.S_IXUSR)
        self.assertTrue((LAB / "bin/nyitsec-answer").stat().st_mode & stat.S_IXUSR)

        module = yaml.safe_load((ROOT / "level-3/module.yml").read_text())
        self.assertEqual(
            [entry["id"] for entry in module["challenges"]],
            ["dns-treasure-hunt", "suspicious-script", "broken-login"],
        )

        startup = (LAB / ".forum-start.sh").read_text()
        self.assertIn("127.0.0.1 nyitsecwebsite.test", startup)
        self.assertIn("gethostbyname", startup)
        app = (LAB / ".forum-app.py").read_text()
        self.assertIn('HOST = "127.0.0.1"', app)
        self.assertIn('pwd.getpwnam("nobody")', app)
        self.assertIn("os.setuid(account.pw_uid)", app)
        self.assertIn("DROP TABLE", (LAB / "README.md").read_text())
        self.assertTrue(
            (ROOT / "docs/its-review/broken-login/README.md").is_file()
        )


if __name__ == "__main__":
    unittest.main()
