"""End-to-end DNS query and decoding tests for Level 3: DNS Treasure Hunt."""

import base64
import codecs
import hashlib
import os
from pathlib import Path
import runpy
import socket
import stat
import struct
import subprocess
import tarfile
import tempfile
import threading
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "level-3" / "dns-treasure-hunt"
TEMPLATE = ROOT / "templates" / "nyitsec-challenge"
ZONE = "archive.nyitsec.test"
MESSAGE = "The red lantern waits by the harbor"


class DNSInvestigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = runpy.run_path(str(LAB / ".dns-server.py"), run_name="unit-test")
        cls.server = cls.site["create_server"](port=0)
        cls.thread = threading.Thread(
            target=cls.server.serve_forever, daemon=True
        )
        cls.thread.start()
        cls.port = cls.server.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    @classmethod
    def query(cls, name, kind):
        """Send a real UDP DNS request and parse its answer records."""
        type_id = cls.site["TYPES"][kind]
        question = cls.site["encode_name"](name) + struct.pack("!HH", type_id, 1)
        packet = struct.pack("!6H", 0xBEEF, 0x0100, 1, 0, 0, 0) + question
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(3)
            sock.sendto(packet, ("127.0.0.1", cls.port))
            response, _ = sock.recvfrom(4096)

        ident, flags, qd, answer_count, _, _ = struct.unpack("!6H", response[:12])
        assert ident == 0xBEEF and flags & 0x8000 and flags & 0x0400
        assert qd == 1
        _, offset = cls.site["parse_name"](response, 12)
        offset += 4
        answers = []
        for _ in range(answer_count):
            _, offset = cls.site["parse_name"](response, offset)
            rrtype, rrclass, ttl, nbytes = struct.unpack("!HHIH", response[offset:offset+10])
            offset += 10
            data_offset = offset
            data = response[offset:offset+nbytes]
            offset += nbytes
            assert rrclass == 1 and ttl == 60
            if rrtype == 16:
                assert data[0] == len(data) - 1
                answers.append(("TXT", data[1:].decode("utf-8")))
            elif rrtype == 15:
                preference = struct.unpack("!H", data[:2])[0]
                alias, _ = cls.site["parse_name"](response, data_offset + 2)
                answers.append(("MX", (preference, alias)))
            elif rrtype == 5:
                alias, _ = cls.site["parse_name"](response, data_offset)
                answers.append(("CNAME", alias))
            elif rrtype == 1:
                answers.append(("A", ".".join(map(str, data))))
            else:
                answers.append((rrtype, data))
        return answers, flags & 0xF

    def test_reconstructs_message_through_five_query_steps(self):
        initial, rcode = self.query(ZONE, "TXT")
        self.assertEqual(rcode, 0)
        self.assertTrue(any("follow the mail route" in t for _, t in initial))
        self.assertNotIn(MESSAGE, str(initial))
        self.assertNotIn("part=1", str(initial))

        mx, rcode = self.query(ZONE, "MX")
        self.assertEqual(rcode, 0)
        mail = mx[0][1][1]
        self.assertEqual(mail, "mx1." + ZONE)

        clues, _ = self.query(mail, "TXT")
        pointing = [
            txt.partition("=")[2]
            for typ, txt in clues
            if typ == "TXT" and txt.startswith("custodian=")
        ]
        self.assertEqual(pointing, ["handoff." + ZONE])

        cname, _ = self.query(pointing[0], "TXT")
        self.assertEqual(cname, [("CNAME", "vault." + ZONE)])

        index, _ = self.query(cname[0][1], "TXT")
        index_text = " ".join(v for _, v in index)
        self.assertIn("parts=3", index_text)
        self.assertIn("separate subdomain", index_text)
        self.assertNotIn("part1.vault.archive.nyitsec.test", index_text)
        self.assertIn("ROT13", index_text)
        self.assertIn("Base64", index_text)

        chunks = []
        for index in range(1, 4):
            fragments, _ = self.query(f"part{index}.vault.{ZONE}", "TXT")
            self.assertEqual(len(fragments), 1)
            self.assertEqual(fragments[0][0], "TXT")
            self.assertIn(f"part={index}/3; data=", fragments[0][1])
            chunks.append(fragments[0][1].partition("data=")[2])

        # Fragments must be joined *before* decoding.
        encoded = "".join(chunks)
        unrotated = codecs.decode(encoded, "rot_13")
        decoded = base64.b64decode(unrotated, validate=True).decode("utf-8")
        self.assertEqual(decoded, MESSAGE)
        self.assertNotIn("NYITSEC-", decoded)
        self.assertGreater(len({c for c in chunks}), 1)

        checker = runpy.run_path(str(LAB / "verify"), run_name="unit-test")
        self.assertTrue(checker["is_correct"](decoded))
        self.assertTrue(checker["is_correct"](decoded.lower()))
        self.assertFalse(checker["is_correct"]("NYITSEC-DNS-26"))
        self.assertFalse(checker["is_correct"](decoded + " extra"))
        self.assertEqual(
            checker["EXPECTED_SHA256"],
            hashlib.sha256(decoded.casefold().encode()).hexdigest(),
        )

    def test_unrelated_records_and_nonrecursive_unknown_name(self):
        noise, _ = self.query("backup." + ZONE, "TXT")
        self.assertTrue(any("rotation=" in value for _, value in noise))
        unrelated, rcode = self.query("unknown." + ZONE, "TXT")
        self.assertEqual(unrelated, [])
        self.assertEqual(rcode, 3)

    def test_authentic_offline_dig_queries_local_service(self):
        wrapped = LAB / "bin" / "dig"
        env = os.environ.copy()
        env["NYITSEC_FORCE_BUNDLED_DIG"] = "1"
        result = subprocess.run(
            [str(wrapped), "@127.0.0.1", "-p", str(self.port),
             ZONE, "MX", "+short"],
            text=True, capture_output=True, timeout=30, env=env,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("mx1.archive.nyitsec.test.", result.stdout)

        self.assertTrue(wrapped.stat().st_mode & stat.S_IXUSR)
        with tarfile.open(LAB / ".dig-runtime.tar.gz", "r:gz") as archive:
            members = archive.getmembers()
            names = {m.name.lstrip("./") for m in members}
            self.assertIn("dig", names)
            self.assertTrue(any(s.startswith("lib/lib") for s in names))
            self.assertFalse(any(m.issym() or m.islnk() for m in members))
            self.assertFalse(any(m.mode & 0o4000 for m in members))

    def test_source_excluded_from_student_workspace(self):
        prepare = runpy.run_path(
            str(TEMPLATE / ".workspace.py"), run_name="unit-test"
        )["prepare_workspace"]
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "student"
            actual = prepare(LAB, workspace)
            self.assertEqual(actual, ["dns-briefing.txt"])
            self.assertEqual({p.name for p in workspace.iterdir()}, {"dns-briefing.txt"})
            self.assertEqual(stat.S_IMODE(workspace.stat().st_mode), 0o700)
            self.assertEqual(
                stat.S_IMODE((workspace / "dns-briefing.txt").stat().st_mode),
                0o600,
            )

        self.assertEqual(
            (LAB / ".workspace.py").read_bytes(),
            (TEMPLATE / ".workspace.py").read_bytes()
        )
        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location("validator", ROOT / "scripts/validate_dojo.py")
        validation = module_from_spec(spec)
        spec.loader.exec_module(validation)
        self.assertEqual(
            (LAB / ".init").read_bytes(),
            (TEMPLATE / ".init").read_bytes() + validation.DNS_INIT_SUFFIX
        )
        startup = (LAB / ".dns-start.sh").read_text()
        self.assertIn("chmod 600", startup)
        self.assertIn("127.0.0.1", startup)
        self.assertIn("5300", startup)

    def test_level_three_is_intermediate_and_student_hints_are_limited(self):
        dojo = yaml.safe_load((ROOT / "dojo.yml").read_text())
        ids = [m["id"] for m in dojo["modules"]]
        self.assertEqual(ids[:4], ["linux-cli-intro", "fundamentals", "level-2", "level-3"])
        module = yaml.safe_load((ROOT / "level-3/module.yml").read_text())
        self.assertEqual(
            [c["id"] for c in module["challenges"]],
            ["dns-treasure-hunt", "suspicious-script"]
        )
        instructions = (LAB / "DESCRIPTION.md").read_text()
        self.assertIn("dig @127.0.0.1 -p 5300", instructions)
        self.assertIn("nothing to install", instructions)
        self.assertIn("nyitsec-answer", instructions)
        self.assertNotIn(MESSAGE, instructions)
        self.assertNotIn("part1.vault", instructions)
        self.assertNotIn("ROT13", instructions)


if __name__ == "__main__":
    unittest.main()
