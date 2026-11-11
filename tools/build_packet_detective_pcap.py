#!/usr/bin/env python3
"""Generate a synthetic, offline HTTP packet capture for NYITSec training.

All names, accounts, and network addresses are fictional. Packets are built in
memory with Scapy and saved to disk; no sockets or network requests are made.
This officer-only authoring script is not deployed to the student workspace.
"""
from pathlib import Path
from urllib.parse import quote
from scapy.all import Ether, IP, TCP, Raw, wrpcap

OUTPUT = Path(__file__).resolve().parents[1] / "level-3/packet-detective/traffic.pcap"
TRACE = "LAB-7B"
USER = "bob"
PASSWORD = "Lumen&Branch#47"

frames = []
clock = 1794400000.0


def emit(src, dst, sport, dport, seq, ack, flags, data=b""):
    global clock
    packet = Ether(src="02:00:00:00:00:10", dst="02:00:00:00:00:20")
    packet /= IP(src=src, dst=dst, ttl=64)
    packet /= TCP(sport=sport, dport=dport, seq=seq, ack=ack, flags=flags)
    if data:
        packet /= Raw(data)
    packet.time = clock
    clock += 0.016
    frames.append(packet)


def exchange(number, path, content="", reference="", method="GET", response=None,
             segments=1):
    src, dst = "10.77.40.17", "198.51.100.44"
    sport, dport = 42000 + number, 80
    a, b = 100000 + number * 1000, 900000 + number * 1000
    emit(src, dst, sport, dport, a, 0, "S")
    emit(dst, src, dport, sport, b, a + 1, "SA")
    a, b = a + 1, b + 1
    emit(src, dst, sport, dport, a, b, "A")

    body = content.encode("ascii")
    headers = [
        f"{method} {path} HTTP/1.1", "Host: relaydesk.test",
        "User-Agent: TrainingBrowser/1.0", "Connection: close",
    ]
    if reference:
        headers.append(f"X-Lab-Trace: {reference}")
    if method == "POST":
        headers.extend(["Content-Type: application/x-www-form-urlencoded",
                        f"Content-Length: {len(body)}"])
    request = ("\r\n".join(headers) + "\r\n\r\n").encode("ascii")
    if segments > 1:
        offsets = [0, 22, 30, 39, len(body)]
        pieces = [request + body[:22]]
        pieces += [body[offsets[i]:offsets[i + 1]] for i in range(1, 4)]
    else:
        pieces = [request + body]

    for piece in pieces:
        if not piece:
            continue
        emit(src, dst, sport, dport, a, b, "PA", piece)
        a += len(piece)
        emit(dst, src, dport, sport, b, a, "A")

    response = response or "<html><body>Fictional portal response.</body></html>"
    payload = response.encode("utf-8")
    reply = (b"HTTP/1.1 200 OK\r\nServer: FictionalRelay/1\r\n"
             b"Content-Type: text/html; charset=utf-8\r\n"
             + f"Content-Length: {len(payload)}\r\nConnection: close\r\n\r\n".encode()
             + payload)
    emit(dst, src, dport, sport, b, a, "PA", reply)
    b += len(reply)
    emit(src, dst, sport, dport, a, b, "A")
    emit(src, dst, sport, dport, a, b, "FA")
    a += 1
    emit(dst, src, dport, sport, b, a, "A")
    emit(dst, src, dport, sport, b, a, "FA")
    b += 1
    emit(src, dst, sport, dport, a, b, "A")


def login(username, password):
    return "username=" + quote(username, safe="") + "&pass=" + quote(password, safe="")


def build(output=OUTPUT):
    exchange(1, "/")
    exchange(2, "/login")
    exchange(3, "/api/login", login("demo_alice", "Moss#Train42"),
             "LAB-2A", "POST")
    exchange(4, "/forum?topic=networking")
    exchange(5, "/api/login", login("demo_jonas", "Autumn&Test81"),
             "LAB-5C", "POST")
    exchange(6, "/docs/faq")
    exchange(7, "/tickets/CASE-105", response="<p>Unrelated support ticket.</p>")
    exchange(8, "/api/login", login("demo_riley", "Mint#Demo56"),
             "LAB-9D", "POST")
    exchange(9, "/tickets/CASE-417", response=(
        "<h1>CASE-417</h1><p>Fictional HTTP login investigation.</p>"
        "<p>Correlate the portal request whose X-Lab-Trace is LAB-7B.</p>"
    ))
    exchange(10, "/static/app.css", response="body{background:#19233b}")
    exchange(11, "/api/login", login(USER, PASSWORD) + "&remember=on",
             TRACE, "POST", segments=4)
    exchange(12, "/api/login", login("demo_morgan", "Cloud#Sample93"),
             "LAB-6E", "POST")
    exchange(13, "/api/settings", "theme=night&lang=en", "LAB-8F", "POST")
    exchange(14, "/forum?topic=soldering")
    exchange(15, "/api/login", login("demo_kira", "Prism&Test99"),
             "LAB-1G", "POST")
    exchange(16, "/status")
    exchange(17, "/api/login", login("demo_nina", "Cobalt#Draft61"),
             "LAB-4K", "POST")
    exchange(18, "/logout")
    exchange(19, "/static/logo.svg", response="<svg><text>RelayDesk</text></svg>")
    exchange(20, "/forum?topic=ctf")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    wrpcap(str(output), frames)
    return output


if __name__ == "__main__":
    result = build()
    print(f"Created synthetic pcap: {result}, {result.stat().st_size} bytes")
