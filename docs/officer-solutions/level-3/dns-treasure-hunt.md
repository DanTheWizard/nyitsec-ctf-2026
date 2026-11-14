# DNS Treasure Hunt — Officer notes

**Module:** `level-3` | **Challenge ID:** `dns-treasure-hunt` | **Difficulty:** Intermediate

The fictional authoritative DNS server binds exclusively to UDP `127.0.0.1:5300`. Its starting zone is `archive.nyitsec.test`.

**Intended path:** initial TXT hint → MX mail server → mail server TXT → custodian CNAME → vault TXT → three ordered TXT fragments. Concatenate the three `data=` portions, undo ROT13, and Base64-decode to recover a **natural-language phrase**, deliberately not another predictable `NYITSEC-...` code. Extra normal DNS entries distract from the correct route.

The root-owned `.dns-server.py` is protected by a startup `chmod 600`; `.dns-start.sh` launches the UDP service and checks a real DNS response. The service drops to the unprivileged `hacker` UID, does not recurse or log DNS requests, and has no external dependencies.

The `.init` file uses the standard writable workspace startup plus an exact approved suffix. The `.ctfignore` file excludes server implementation and the offline tool archive. Only `dns-briefing.txt` is copied to the student's `/nyitsec-ctf`.

The `bin/dig` wrapper prefers a real system dig binary or runs the **genuine ISC dig** program from the bundled Ubuntu library archive. This requires no student installation, internet access, or privilege escalation. Third-party provenance is documented in `tools/DIG_RUNTIME_LICENSES.md`. The regular `nyitsec-answer` verifier unlocks only the platform's per-student `/flag`.

**Live checks:** `dig -v`; `dig @127.0.0.1 -p 5300 archive.nyitsec.test TXT`; follow the DNS chain; decode the message; test correct/wrong answers; ensure the server source cannot be read by `hacker`; restart the challenge and repeat. Do not assume that one DNS request reveals the answer.
