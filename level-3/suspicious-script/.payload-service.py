#!/usr/local/bin/python
"""Serve only the XOR-obfuscated fictional analysis payload over localhost."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os

HOST = "127.0.0.1"
PORT = 8876
RESOURCE = "/assets/payload.bin"
PAYLOAD_PATH = Path("/challenge/.payload.bin")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != RESOURCE:
            self.send_error(404, "Not found")
            return

        data = self.server.payload
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        # No requests or student data are written to log files.
        pass


def create_server(host=HOST, port=PORT, payload=None):
    if payload is None:
        payload = PAYLOAD_PATH.read_bytes()
    if not payload.startswith(b"LAB1"):
        raise ValueError("Invalid payload marker")
    server = ThreadingHTTPServer((host, port), Handler)
    server.payload = payload
    return server


def main():
    # Read the root-only binary before dropping privileges. It must not be
    # readable as a file from the unprivileged student account.
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
