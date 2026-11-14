# DNS Treasure Hunt — Officer notes

**Module:** `level-3` | **Challenge ID:** `dns-treasure-hunt` | **Difficulty:** Intermediate

The fictional authoritative DNS server binds exclusively to UDP `127.0.0.1:5300`. Its starting zone is `archive.nyitsec.test`.

**Intended path:** initial TXT hint → MX mail server → mail server TXT → custodian CNAME → vault TXT → three ordered TXT fragments. Concatenate the three `data=` portions, undo ROT13, and Base64-decode to recover a **natural-language phrase**, deliberately not another predictable `NYITSEC-...` code. Extra normal DNS entries distract from the correct route.

The root-owned `.dns-server.py` is protected by a startup `chmod 600`; `.dns-start.sh` launches the UDP service and checks a real DNS response. The service drops to the unprivileged `hacker` UID, does not recurse or log DNS requests, and has no external dependencies.

The `.init` file uses the standard writable workspace startup plus an exact approved suffix. The `.ctfignore` file excludes server implementation and the offline tool archive. Only `dns-briefing.txt` is copied to the student's `/nyitsec-ctf`.

The `bin/dig` wrapper prefers a real system dig binary or runs the **genuine ISC dig** program from the bundled Ubuntu library archive. This requires no student installation, internet access, or privilege escalation. Third-party provenance is documented in `tools/DIG_RUNTIME_LICENSES.md`. The regular `nyitsec-answer` verifier unlocks only the platform's per-student `/flag`.

**Live checks:** `dig -v`; `dig @127.0.0.1 -p 5300 archive.nyitsec.test TXT`; follow the DNS chain; decode the message; test correct/wrong answers; ensure the server source cannot be read by `hacker`; restart the challenge and repeat. Do not assume that one DNS request reveals the answer.

## Officer QA: verified answer and repeatable solution

**Exact correct inputs (prompt order):** `The red lantern waits by the harbor`  
**Deliberately incorrect test inputs:** `The blue lantern waits by the harbor`  
**Input policy:** Case-insensitive with surrounding whitespace stripped; the phrase and DNS fragments are fixed for this challenge.

### Reproduce the intended solution

Follow the fictional UDP DNS service's chain: TXT at `archive.nyitsec.test` → MX `mx1.archive.nyitsec.test` → TXT custodian `handoff.archive.nyitsec.test` → CNAME `vault.archive.nyitsec.test` → TXT `part1.vault...`, `part2.vault...`, `part3.vault...`. Use the bundled dig (localhost only):

```bash
dig @127.0.0.1 -p 5300 archive.nyitsec.test TXT
dig @127.0.0.1 -p 5300 archive.nyitsec.test MX
dig @127.0.0.1 -p 5300 mx1.archive.nyitsec.test TXT
dig @127.0.0.1 -p 5300 handoff.archive.nyitsec.test CNAME
dig @127.0.0.1 -p 5300 vault.archive.nyitsec.test TXT
for n in 1 2 3; do dig +short @127.0.0.1 -p 5300 part$n.vault.archive.nyitsec.test TXT; done
```

Collect the ordered `data=` tokens, concatenate them without spaces, apply ROT13, then Base64-decode. A reproducible officer reference for the fixed payload:

```bash
python3 - <<'PY'
import base64, codecs
parts = ['ITuyVUWyMPOfLJ','50MKWhVUqunKEmV','TW5VUEbMFObLKWvo3V=']
print(base64.b64decode(codecs.decode(''.join(parts), 'rot_13')).decode())
PY
```

Expected phrase: `The red lantern waits by the harbor`.

### Noninteractive checker test over SSH

Run this self-contained Python probe **inside a fresh SSH-connected challenge instance**. It executes the existing `nyitsec-answer` command twice, one known-wrong and one known-correct submission. It checks exit status, the exact rejection message, and the presence of a correctly shaped platform flag, but **never prints or saves the flag**. `BLOCKED` means the verifier or environment could not be validated, not that the challenge was solved.

```python
import re
import subprocess
import sys

# Inputs are fictional training data from this private officer guide.
cases = [
    ("incorrect", ["The blue lantern waits by the harbor"], False),
    ("correct", ["The red lantern waits by the harbor"], True),
]
rejection_text = "That message did not match the recovered evidence."
status = 0

for label, answers, should_accept in cases:
    try:
        result = subprocess.run(
            ["nyitsec-answer"],
            input="\n".join(answers) + "\n",
            text=True,
            capture_output=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        print(f"BLOCKED: {label} probe could not execute or timed out")
        status = max(status, 2)
        continue

    if result.returncode != 0:
        print(f"BLOCKED: {label} verifier exited with status {result.returncode}")
        status = max(status, 2)
        continue

    lines = result.stdout.splitlines()
    success_lines = [i for i, line in enumerate(lines) if line.startswith("Correct!")]

    if should_accept:
        if not success_lines:
            if rejection_text in result.stdout:
                print("FAIL: documented correct answer was rejected")
                status = max(status, 1)
            else:
                print("BLOCKED: correct probe had no recognized verifier response")
                status = max(status, 2)
        else:
            position = success_lines[-1] + 1
            flag = lines[position].strip() if position < len(lines) else ""
            if re.fullmatch(r"pwn\.college\{[^{}\s]+\}", flag):
                print("PASS: correct answer accepted and platform flag produced (redacted)")
            else:
                print("BLOCKED: success marker present but expected flag missing or malformed")
                status = max(status, 2)
    elif success_lines:
        print("FAIL: deliberately incorrect answer was accepted")
        status = max(status, 1)
    elif rejection_text in result.stdout:
        print("PASS: deliberately incorrect answer rejected")
    else:
        print("BLOCKED: incorrect probe had no recognized rejection response")
        status = max(status, 2)

# 0: all checks passed; 1: verification failed; 2: environment/transport blocked.
sys.exit(status)
```

Keep this literal solution in the **private officer guide only**, never in the student-facing challenge directory or logs. Do not record platform flag values.
