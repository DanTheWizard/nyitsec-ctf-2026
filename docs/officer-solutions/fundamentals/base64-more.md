# Author notes: More Base64?

**Module:** `fundamentals` | **ID:** `base64-more`

This challenge uses **the original Base64-encoded forwarded-message payload provided for the NYITSec activity**, copied into `message.b64` without modification.

Students should decode the outer Base64 message and see a forwarded-message header plus another Base64 payload. Decoding the inner payload produces a reply message with a Base64 segment *inside the sentence*, followed by additional ordinary reply text. Decoding that segment reveals a final two-word message, which is the answer accepted by `nyitsec-answer`.

There are **three total Base64 decoding steps**, but the second and third require isolating an encoded substring from human-readable conversation text. The student-facing instructions intentionally do not reveal the final answer.

### Standard NYITSec challenge mechanics

- `.init` (executable): interactive Bash starts in `/nyitsec-ctf`.
- `bin/nyitsec-answer` (executable): delegates to `/challenge/verify` via the provided challenge PATH.
- `verify` (executable): compares the submitted original message's SHA-256 digest and reveals the student's unique root-protected `/flag` only after a correct match.
- `message.b64`: the fictional forwarded conversation in Base64, not a real secret or flag.

### Smoke test after merge and deployment

1. Open a fresh workspace; `pwd` should show `/nyitsec-ctf`.
2. Run `base64 -d message.b64`, identify the inner Base64 string, and decode it.
3. Find the encoded substring inside the reply, decode it, and confirm it reveals the original two-word message.
4. Enter an incorrect answer into `nyitsec-answer`, which must not reveal the flag.
5. Enter the original two-word message and submit the resulting platform-generated flag.
6. Check that the existing Base64 Basics and Base64 Layers challenges still work.

The offline unit test independently decodes each stage, verifies that the message wrappers remain intact, and tests both accepted and rejected answer submissions without reading `/flag`.

## Writable workspace standard

The `.init` startup script prepares `/nyitsec-ctf` by running `.workspace.py` and opens interactive terminals there. Challenge input copies are writable by `hacker`; protected files remain in `/challenge`. The blacklist in `.ctfignore` may add exclusions, but protected core names cannot be copied. The workspace is disposable across challenge restarts. Check `pwd`, `ls -la`, `touch scratch.txt`, `nyitsec-answer`, and correct/wrong solution submissions after deployment.

## Officer QA: verified answer and repeatable solution

**Exact correct answer (in prompt order):** `Super Cool`  
**Deliberately incorrect test input:** `Super Cool!`  
**Input policy:** The checker ignores surrounding whitespace and case, but the two-word content must match.

### Reproduce the intended solution

Decode the outer forwarded message, then its second line:

```bash
cd /nyitsec-ctf
base64 -d message.b64
base64 -d message.b64 | sed -n '2p' | base64 -d
```

The inner reply contains the Base64 substring `TXkgbWVzc2FnZTogU3VwZXIgQ29vbA==`. Decode that substring:

```bash
printf '%s' 'TXkgbWVzc2FnZTogU3VwZXIgQ29vbA==' | base64 -d
```

It reads `My message: Super Cool`; submit only `Super Cool`.

### Noninteractive checker test over SSH

Run this self-contained Python probe **inside a fresh SSH-connected challenge instance**. It executes the existing `nyitsec-answer` command twice, one known-wrong and one known-correct submission. It checks exit status, the exact rejection message, and the presence of a correctly shaped platform flag, but **never prints or saves the flag**. `BLOCKED` means the verifier or environment could not be validated, not that the challenge was solved.

```python
import re
import subprocess
import sys

# Inputs are fictional training data from this private officer guide.
cases = [
    ("incorrect", ["Super Cool!"], False),
    ("correct", ["Super Cool"], True),
]
rejection_text = "Not quite. Follow the forwarded messages to their original source."
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

The literal answer above is synthetic challenge data stored **only in private officer documentation**, never in student-facing `DESCRIPTION.md`, `/challenge/README.md`, or the writable workspace. Do not save actual platform flags in QA reports.
