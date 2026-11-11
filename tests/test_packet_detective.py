"""Offline PCAP integration tests for Level 3 Packet Detective.

Decode Ethernet/IPv4/TCP with only the Python standard library so CI never
depends on a local Wireshark installation. The authoring workflow separately
runs genuine tshark against the generated evidence.
"""

from collections import defaultdict
import hashlib
import ipaddress
from pathlib import Path
import runpy
import shutil
import stat
import struct
import subprocess
import tempfile
import unittest
from urllib.parse import parse_qs

import yaml


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "level-3" / "packet-detective"
TEMPLATE = ROOT / "templates" / "nyitsec-challenge"
CAPTURE = LAB / "traffic.pcap"
INCIDENT = "CASE-417"
EXPECTED_USERNAME = "bob"
EXPECTED_PASSWORD = "Lumen&Branch#47"


def parse_frames(filename):
    """Read classic Ethernet PCAP packets and both TCP conversation directions."""
    raw = Path(filename).read_bytes()
    if len(raw) < 24:
        raise ValueError("Truncated pcap")
    magic, major, minor, _, _, snaplen, linktype = struct.unpack_from(
        "<IHHIIII", raw, 0
    )
    if (magic, major, minor, linktype) != (0xA1B2C3D4, 2, 4, 1):
        raise ValueError("Expected ordinary Ethernet PCAP v2.4")
    assert snaplen >= 1500
    records = []
    offset = 24
    while offset < len(raw):
        if len(raw) - offset < 16:
            raise ValueError("Truncated packet header")
        seconds, micros, captured, wire = struct.unpack_from(
            "<IIII", raw, offset
        )
        offset += 16
        packet = raw[offset:offset + captured]
        if len(packet) != captured or wire < captured:
            raise ValueError("Truncated packet")
        offset += captured
        if len(packet) < 54 or packet[12:14] != b"\x08\x00":
            continue
        ip_start = 14
        ip_len = (packet[ip_start] & 15) * 4
        if packet[ip_start + 9] != 6 or ip_len < 20:
            continue
        ip_total = struct.unpack_from("!H", packet, ip_start + 2)[0]
        source = str(ipaddress.IPv4Address(packet[ip_start + 12:ip_start + 16]))
        destination = str(ipaddress.IPv4Address(packet[ip_start + 16:ip_start + 20]))
        tcp_start = ip_start + ip_len
        if len(packet) < tcp_start + 20:
            raise ValueError("Truncated TCP header")
        sport, dport, seq, ack = struct.unpack_from("!HHII", packet, tcp_start)
        tcp_len = (packet[tcp_start + 12] >> 4) * 4
        payload_start = tcp_start + tcp_len
        payload_end = ip_start + ip_total
        payload = packet[payload_start:payload_end]
        records.append({
            "seconds": seconds, "micros": micros,
            "src": source, "dst": destination,
            "sport": sport, "dport": dport,
            "seq": seq, "ack": ack, "data": payload,
        })
    return records


def conversations(packets):
    streams = defaultdict(lambda: {"request_packets": [], "reply_packets": []})
    for packet in packets:
        if packet["dport"] == 80:
            name = (packet["src"], packet["sport"], packet["dst"])
            streams[name]["request_packets"].append(packet)
        elif packet["sport"] == 80:
            name = (packet["dst"], packet["dport"], packet["src"])
            streams[name]["reply_packets"].append(packet)
    for stream in streams.values():
        for direction, key in [
            ("request_packets", "request"),
            ("reply_packets", "reply"),
        ]:
            payload_packets = sorted(
                (p for p in stream[direction] if p["data"]),
                key=lambda packet: packet["seq"],
            )
            stream[key] = b"".join(p["data"] for p in payload_packets)
            stream[direction] = payload_packets
    return streams


class PacketDetectiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frames = parse_frames(CAPTURE)
        cls.streams = conversations(cls.frames)

    def test_capture_has_real_multi_session_http_with_synthetic_data(self):
        self.assertGreaterEqual(len(self.frames), 130)
        self.assertEqual(len(self.streams), 20)
        for stream in self.streams.values():
            request, reply = stream["request"], stream["reply"]
            self.assertIn(b"HTTP/1.1\r\n", request)
            self.assertIn(b"HTTP/1.1 200 OK\r\n", reply)
            self.assertIn(b"\r\n\r\n", reply)
        requests = [s["request"] for s in self.streams.values()]
        self.assertGreaterEqual(
            sum(b"POST /api/login" in r for r in requests), 7
        )
        self.assertGreaterEqual(
            sum(b"GET /" in r for r in requests), 9
        )
        self.assertTrue(
            all(not s["reply"].endswith(EXPECTED_PASSWORD.encode())
                for s in self.streams.values())
        )
        self.assertNotIn(EXPECTED_PASSWORD.encode(), CAPTURE.read_bytes())

    def test_two_stage_ticket_correlation_then_reassembled_post(self):
        # First read the ticket's HTTP response to obtain the reference.
        tickets = [
            s for s in self.streams.values()
            if b"GET /tickets/CASE-417 HTTP/1.1" in s["request"]
        ]
        self.assertEqual(len(tickets), 1)
        ticket_response = tickets[0]["reply"].decode("utf-8")
        self.assertIn(INCIDENT, ticket_response)
        self.assertIn("X-Lab-Trace: LAB-7B", ticket_response)
        self.assertNotIn(EXPECTED_PASSWORD, ticket_response)
        trace = "LAB-7B"

        # Next find a separate HTTP POST containing the case's trace ID.
        candidates = [
            s for s in self.streams.values()
            if f"X-Lab-Trace: {trace}".encode() in s["request"]
        ]
        self.assertEqual(len(candidates), 1)
        chosen = candidates[0]
        self.assertIsNot(chosen, tickets[0])
        self.assertTrue(
            chosen["request"].startswith(b"POST /api/login HTTP/1.1")
        )
        self.assertEqual(len(chosen["request_packets"]), 4)
        header, encoded_body = chosen["request"].split(b"\r\n\r\n", 1)
        self.assertIn(b"application/x-www-form-urlencoded", header)
        content_length = next(
            int(line.partition(b": ")[2])
            for line in header.split(b"\r\n")
            if line.lower().startswith(b"content-length:")
        )
        self.assertEqual(content_length, len(encoded_body))
        self.assertIn(b"%26", encoded_body)
        self.assertIn(b"%23", encoded_body)

        # parse_qs performs the same plus/percent decoding required of students.
        fields = parse_qs(encoded_body.decode("ascii"))
        self.assertEqual(fields["username"], [EXPECTED_USERNAME])
        self.assertEqual(fields["pass"], [EXPECTED_PASSWORD])
        self.assertEqual(fields["remember"], ["on"])

    def test_wrong_credentials_fail_and_both_fields_are_required(self):
        checker = runpy.run_path(str(LAB / "verify"), run_name="offline-test")
        correct = checker["is_correct"]
        self.assertTrue(correct(EXPECTED_USERNAME, EXPECTED_PASSWORD))
        self.assertTrue(correct("BOB", " " + EXPECTED_PASSWORD + " "))
        self.assertFalse(correct("demo_alice", EXPECTED_PASSWORD))
        self.assertFalse(correct(EXPECTED_USERNAME, EXPECTED_PASSWORD.lower()))
        self.assertFalse(correct("demo_alice", "Moss#Train42"))
        self.assertEqual(
            checker["USERNAME_SHA256"],
            hashlib.sha256(EXPECTED_USERNAME.encode()).hexdigest(),
        )
        self.assertEqual(
            checker["PASSWORD_SHA256"],
            hashlib.sha256(EXPECTED_PASSWORD.encode()).hexdigest(),
        )
        self.assertNotIn(
            EXPECTED_PASSWORD, (LAB / "DESCRIPTION.md").read_text()
        )
        self.assertNotIn(
            EXPECTED_PASSWORD, (LAB / "verify").read_text()
        )

    def test_standard_workspace_just_contains_packet_and_incident_note(self):
        copier = runpy.run_path(
            str(TEMPLATE / ".workspace.py"), run_name="offline-test"
        )["prepare_workspace"]
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "student"
            staged = copier(LAB, target)
            self.assertEqual(
                staged, ["incident-brief.txt", "traffic.pcap"]
            )
            self.assertEqual(
                {p.name for p in target.iterdir()},
                {"incident-brief.txt", "traffic.pcap"},
            )
            self.assertEqual((target / "traffic.pcap").read_bytes(), CAPTURE.read_bytes())
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o700)
        self.assertEqual(
            (LAB / ".init").read_bytes(), (TEMPLATE / ".init").read_bytes()
        )
        self.assertEqual(
            (LAB / ".workspace.py").read_bytes(),
            (TEMPLATE / ".workspace.py").read_bytes()
        )
        for name in (".init", "verify", "bin/nyitsec-answer"):
            self.assertTrue((LAB / name).stat().st_mode & stat.S_IXUSR)
        self.assertTrue(
            (ROOT / "docs/its-review/packet-detective/README.md").is_file()
        )
        self.assertTrue(
            (ROOT / "tools/build_packet_detective_pcap.mjs").is_file()
        )

    @unittest.skipUnless(shutil.which("node"), "Node.js unavailable for authoring check")
    def test_capture_matches_reproducible_authoring_generator(self):
        command = subprocess.run(
            [
                "node", str(ROOT / "tools/build_packet_detective_pcap.mjs"),
                "--check",
            ],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(command.returncode, 0, command.stderr)
        self.assertIn("matches", command.stdout)

    def test_level_three_challenge_is_second(self):
        module = yaml.safe_load((ROOT / "level-3/module.yml").read_text())
        self.assertEqual(
            [c["id"] for c in module["challenges"]],
            [
                "forgotten-commit", "packet-detective",
                "dns-treasure-hunt", "suspicious-script", "broken-login",
            ],
        )
        description = (LAB / "DESCRIPTION.md").read_text()
        self.assertIn("tshark", description)
        self.assertIn("Wireshark", description)
        self.assertIn("nyitsec-answer", description)
        self.assertIn("CASE-417", description)
        self.assertNotIn("LAB-7B", description)
        self.assertNotIn(EXPECTED_PASSWORD, description)

    @unittest.skipUnless(shutil.which("tshark"), "tshark unavailable in CI")
    def test_optional_real_tshark_decode(self):
        command = subprocess.run(
            [
                "tshark", "-r", str(CAPTURE),
                "-Y", 'http.request.method == "POST"',
                "-T", "fields", "-e", "tcp.stream",
            ],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(command.returncode, 0, command.stderr)
        self.assertGreaterEqual(len(command.stdout.splitlines()), 7)


if __name__ == "__main__":
    unittest.main()
