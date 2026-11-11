#!/bin/sh
# Start the localhost evidence service after the standard workspace setup.
set -eu

# Only the untrusted-looking starter script is copied into /nyitsec-ctf.
chmod 600 /challenge/.payload-service.py /challenge/.payload-start.sh /challenge/.payload.bin

nohup /usr/local/bin/python -I /challenge/.payload-service.py \
    </dev/null >/tmp/nyitsec-payload-start.log 2>&1 &

# Fail before a student opens the exercise if the service did not start.
# Verify actual HTTP content instead of checking only the process ID.
/usr/local/bin/python -I - <<'PY'
import time
from urllib.request import urlopen

url = "http://127.0.0.1:8876/assets/payload.bin"
for _ in range(30):
    try:
        with urlopen(url, timeout=0.3) as reply:
            data = reply.read(4096)
            if reply.status == 200 and data.startswith(b"LAB1"):
                break
    except OSError:
        pass
    time.sleep(0.1)
else:
    raise SystemExit("NYITSec: payload service unavailable; check /tmp/nyitsec-payload-start.log")
PY
