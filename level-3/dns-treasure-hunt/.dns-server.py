#!/usr/local/bin/python
"""A tiny authoritative DNS server for the fictional NYITSec training zone.

Serves actual UDP DNS packets on 127.0.0.1:5300. There are no external DNS
requests, no student-provided shell commands, and no queries logged to disk.
"""

import os
import socketserver
import struct

HOST = "127.0.0.1"
PORT = 5300
ZONE = "archive.nyitsec.test"

# The three pieces are ROT13 applied to the Base64 encoding of a natural-language message.
# They deliberately reside at *different DNS names*, not one TXT answer.
RECORDS = {
    ZONE: {
        "NS": ["ns1." + ZONE],
        "A": ["192.0.2.30"],
        "MX": [(10, "mx1." + ZONE)],
        "TXT": [
            "asset=fictional-archive-2026",
            "review=follow the mail route; the handoff custodian left the next clue",
        ],
    },
    "ns1." + ZONE: {"A": ["192.0.2.53"]},
    "mx1." + ZONE: {
        "A": ["192.0.2.25"],
        "TXT": [
            "mail=queued; queue=clean",
            "custodian=handoff." + ZONE,
        ],
    },
    "handoff." + ZONE: {"CNAME": ["vault." + ZONE]},
    "vault." + ZONE: {
        "TXT": [
            "handoff=index; parts=3; consult part1, part2, part3 below vault",
            "hint=each part is a separate subdomain of this vault hostname",
            "transform=ROT13; underlying-format=Base64",
        ],
    },
    "part1.vault." + ZONE: {
        "TXT": ["part=1/3; data=ITuyVUWyMPOfLJ"],
    },
    "part2.vault." + ZONE: {
        "TXT": ["part=2/3; data=50MKWhVUqunKEmV"],
    },
    "part3.vault." + ZONE: {
        "TXT": ["part=3/3; data=TW5VUEbMFObLKWvo3V="],
    },
    # Deliberately unrelated records for realistic background activity.
    "www." + ZONE: {
        "A": ["192.0.2.10"],
        "TXT": ["site=public-training-preview"],
    },
    "status." + ZONE: {
        "TXT": ["state=online", "last-review=2026-10-01"],
    },
    "backup." + ZONE: {
        "TXT": ["rotation=weekly", "archive=not-on-this-host"],
    },
}

TYPES = {"A": 1, "NS": 2, "CNAME": 5, "MX": 15, "TXT": 16}
REVERSE_TYPES = {value: key for key, value in TYPES.items()}


def encode_name(name):
    name = name.rstrip(".")
    if not name:
        return b"\x00"
    labels = []
    for label in name.split("."):
        data = label.encode("ascii")
        if not 0 < len(data) <= 63:
            raise ValueError("Bad DNS label")
        labels.append(bytes((len(data),)) + data)
    return b"".join(labels) + b"\x00"


def parse_name(packet, offset):
    """Parse standard and compression-pointer DNS names with strict bounds."""
    labels = []
    after_pointer = None
    visited = set()
    for _ in range(128):
        if offset >= len(packet):
            raise ValueError("Truncated DNS name")
        length = packet[offset]
        if length == 0:
            offset += 1
            return ".".join(labels).lower(), (
                after_pointer if after_pointer is not None else offset
            )
        if length & 0xC0 == 0xC0:
            if offset + 1 >= len(packet):
                raise ValueError("Truncated DNS pointer")
            target = ((length & 0x3F) << 8) | packet[offset + 1]
            if target in visited or target >= len(packet):
                raise ValueError("DNS pointer loop")
            visited.add(target)
            if after_pointer is None:
                after_pointer = offset + 2
            offset = target
            continue
        if length & 0xC0 or length > 63 or offset + 1 + length > len(packet):
            raise ValueError("Malformed DNS label")
        labels.append(packet[offset + 1:offset + 1 + length].decode("ascii"))
        offset += 1 + length
    raise ValueError("DNS name exceeded limit")


def encode_data(kind, value):
    if kind == "TXT":
        raw = value.encode("utf-8")
        if len(raw) > 255:
            raise ValueError("TXT entry too long")
        return bytes([len(raw)]) + raw
    if kind == "A":
        parts = value.split(".")
        if len(parts) != 4 or any(not p.isdigit() or not 0 <= int(p) < 256 for p in parts):
            raise ValueError("Invalid IPv4 address")
        return bytes(map(int, parts))
    if kind == "MX":
        preference, exchange = value
        return struct.pack("!H", preference) + encode_name(exchange)
    if kind in ("CNAME", "NS"):
        return encode_name(value)
    raise ValueError("Unsupported DNS type")


def resolve_packet(packet):
    """Respond only to a single IN question; never perform recursion."""
    if len(packet) < 12:
        return None
    ident, flags, qdcount, _, _, _ = struct.unpack("!6H", packet[:12])
    if qdcount != 1 or (flags & 0x8000) or (flags & 0x7800):
        return None
    try:
        name, end = parse_name(packet, 12)
        if end + 4 > len(packet):
            return None
        qtype, qclass = struct.unpack("!HH", packet[end:end + 4])
        if qclass != 1:
            return None
        question = packet[12:end + 4]

        known = name in RECORDS
        kind = REVERSE_TYPES.get(qtype)
        answers = RECORDS.get(name, {}).get(kind, []) if kind else []

        # CNAME responses are useful even when the student requests TXT.
        if known and not answers and kind != "CNAME":
            answers = RECORDS[name].get("CNAME", [])
            kind = "CNAME" if answers else kind

        encoded = []
        if kind in TYPES:
            for value in answers:
                data = encode_data(kind, value)
                encoded.append(
                    encode_name(name)
                    + struct.pack("!HHIH", TYPES[kind], 1, 60, len(data))
                    + data
                )
        # QR + authoritative answer; no RA (recursion is never available).
        rcode = 0 if known else 3
        response_flags = 0x8000 | 0x0400 | (flags & 0x0100) | rcode
        header = struct.pack(
            "!6H", ident, response_flags, 1, len(encoded), 0, 0
        )
        return header + question + b"".join(encoded)
    except (ValueError, UnicodeError, struct.error, OverflowError):
        return None


class DNSHandler(socketserver.BaseRequestHandler):
    def handle(self):
        packet, channel = self.request
        answer = resolve_packet(packet)
        if answer is not None:
            channel.sendto(answer, self.client_address)


class LocalDNSServer(socketserver.ThreadingUDPServer):
    allow_reuse_address = True
    daemon_threads = True


def create_server(host=HOST, port=PORT):
    return LocalDNSServer((host, port), DNSHandler)


def main():
    server = create_server()
    if os.geteuid() == 0:
        import pwd
        user = pwd.getpwnam("hacker")
        os.setgroups([])
        os.setgid(user.pw_gid)
        os.setuid(user.pw_uid)
    server.serve_forever(poll_interval=0.2)


if __name__ == "__main__":
    main()
