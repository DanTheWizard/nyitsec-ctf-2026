#!/bin/sh
# pwn.college runs .init as root; this configuration is container-local.
set -eu

# The .test name is fictional and must never resolve through public DNS.
# The isolated XFCE/Firefox desktop uses the same container hosts file.
if ! grep -Eq '(^|[[:space:]])nyitsecwebsite[.]test([[:space:]]|$)' /etc/hosts; then
    printf '\n127.0.0.1 nyitsecwebsite.test\n' >> /etc/hosts
fi

# Hide source and use a protected runtime database accessible only to nobody.
chmod 600 /challenge/.forum-app.py /challenge/.forum-start.sh
if [ -e /run/nyitsec-forum ] && [ ! -d /run/nyitsec-forum ]; then
    echo "NYITSec: unsafe forum runtime path" >&2
    exit 1
fi

nohup /usr/local/bin/python -I /challenge/.forum-app.py \
    </dev/null >/tmp/nyitsec-forum-start.log 2>&1 &

# Check the DNS hosts mapping and real HTTP response before accepting the lab.
# Skip environment proxy settings so the check cannot leave this container.
/usr/local/bin/python -I - <<'PY'
import socket
import time
import urllib.error
import urllib.request

if socket.gethostbyname("nyitsecwebsite.test") != "127.0.0.1":
    raise SystemExit("NYITSec: fictional domain did not map to loopback")

opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
request = urllib.request.Request(
    "http://127.0.0.1/",
    headers={"Host": "nyitsecwebsite.test"},
)
for _ in range(30):
    try:
        with opener.open(request, timeout=0.3) as response:
            html = response.read(15000)
            if response.status == 200 and b"SUPER SECURE" in html:
                break
    except (OSError, urllib.error.URLError):
        pass
    time.sleep(0.1)
else:
    raise SystemExit("NYITSec: forum did not start; see /tmp/nyitsec-forum-start.log")
PY
