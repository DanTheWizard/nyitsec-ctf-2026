#!/bin/sh
# Start the fictional authoritative DNS service inside this challenge container.
set -eu
chmod 600 /challenge/.dns-server.py /challenge/.dns-start.sh
nohup /usr/local/bin/python -I /challenge/.dns-server.py \
    </dev/null >/tmp/nyitsec-dns-start.log 2>&1 &

/usr/local/bin/python -I - <<'PY'
import socket
import struct
import time

name = b"".join(bytes((len(p),)) + p for p in (b"archive", b"nyitsec", b"test")) + b"\x00"
query = struct.pack("!6H", 0x4943, 0x0100, 1, 0, 0, 0) + name + struct.pack("!HH", 16, 1)
for _ in range(30):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(0.25)
        sock.sendto(query, ("127.0.0.1", 5300))
        try:
            reply, _ = sock.recvfrom(4096)
            if len(reply) >= 12 and reply[:2] == b"IC" and reply[2] & 0x80 and int.from_bytes(reply[6:8], "big") > 0:
                break
        except socket.timeout:
            pass
    time.sleep(0.1)
else:
    raise SystemExit("NYITSec: DNS startup failed; see /tmp/nyitsec-dns-start.log")
PY
