#!/bin/sh
# Start the fictional local website from a root-owned, non-workspace source.
# Invoked once after the standard /nyitsec-ctf setup.
set -eu

# The fictional .test hostname resolves only inside this disposable VM.
# Firefox and the Terminal use this container-local hosts mapping.
if ! grep -Eq '(^|[[:space:]])harborview[.]test([[:space:]]|$)' /etc/hosts; then
    printf '\n127.0.0.1 harborview.test\n' >> /etc/hosts
fi

# Students work in /nyitsec-ctf, not the server implementation source.
# This code contains the fictional HTML clue; make it root-readable only.
chmod 600 /challenge/.website.py

# Disconnect all streams so the server survives the initialization shell.
nohup /usr/local/bin/python -I /challenge/.website.py \
  </dev/null >/tmp/nyitsec-website-start.log 2>&1 &

# Never expose a broken challenge; verify the HTTP response is available.
# The challenge initializer has a 30-second overall timeout.
 /usr/local/bin/python -I - <<'PY'
import socket
import time
import urllib.error
import urllib.request

if socket.gethostbyname("harborview.test") != "127.0.0.1":
    raise SystemExit("NYITSec: Harborview hostname did not resolve to localhost")

# Health-check loopback directly; disable proxies and verify Host routing.
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
request = urllib.request.Request(
    "http://127.0.0.1/",
    headers={"Host": "harborview.test"},
)
for attempt in range(30):
    try:
        with opener.open(request, timeout=0.4) as result:
            page = result.read()
            if result.status == 200 and b"Harborview Learning Center" in page:
                break
    except (OSError, urllib.error.URLError):
        pass
    time.sleep(0.1)
else:
    raise SystemExit("NYITSec: local website did not start; see /tmp/nyitsec-website-start.log")
PY
