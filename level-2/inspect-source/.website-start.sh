#!/bin/sh
# Start the fictional local website from a root-owned, non-workspace source.
# Invoked once after the standard /nyitsec-ctf setup.
set -eu

# Students work in /nyitsec-ctf, not the server implementation source.
# This code contains the fictional HTML clue; make it root-readable only.
chmod 600 /challenge/.website.py

# Disconnect all streams so the server survives the initialization shell.
nohup /usr/local/bin/python -I /challenge/.website.py \
  </dev/null >/tmp/nyitsec-website-start.log 2>&1 &

# Never expose a broken challenge; verify the HTTP response is available.
# The challenge initializer has a 30-second overall timeout.
 /usr/local/bin/python -I - <<'PY'
import time
import urllib.error
import urllib.request

url = "http://127.0.0.1:8765/"
for attempt in range(30):
    try:
        with urllib.request.urlopen(url, timeout=0.4) as result:
            page = result.read()
            if result.status == 200 and b"Harborview Learning Center" in page:
                break
    except (OSError, urllib.error.URLError):
        pass
    time.sleep(0.1)
else:
    raise SystemExit("NYITSec: local website did not start; see /tmp/nyitsec-website-start.log")
PY
