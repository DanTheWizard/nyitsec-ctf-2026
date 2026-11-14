# Author notes: Base64 Basics

**Module:** fundamentals | **ID:** base64-basics

A self-contained simulated message is stored in `message.b64`. The student must decode it **once** and enter the answer code from the plaintext. Do not publish the plaintext answer in the student description.

- `.init`: shared NYITSec startup hook that sets initial interactive shell directory to `/nyitsec-ctf`.
- `bin/nyitsec-answer`: executable alias for `/challenge/verify`.
- `verify`: executable Python `exec-suid` checker; it compares a hash of the entered answer code and reads pwn.college's student-specific `/flag` only when correct.
- `message.b64`: Base64-encoded practice material. No real credentials or secrets.

### Test after deployment

1. Start a new workspace and check `pwd` is `/nyitsec-ctf`.
2. Confirm `base64 -d message.b64` reveals a readable message containing the answer code.
3. Run `nyitsec-answer` and enter a wrong code; it must not reveal the flag.
4. Re-run with the decoded code; confirm it reveals the unique flag and pwn.college accepts it.

The offline CI tests independently decode the artifact and check the verifier for both correct and incorrect inputs.

## Writable workspace standard

The `.init` startup script prepares `/nyitsec-ctf` by running `.workspace.py` and opens interactive terminals there. Challenge input copies are writable by `hacker`; protected files remain in `/challenge`. The blacklist in `.ctfignore` may add exclusions, but protected core names cannot be copied. The workspace is disposable across challenge restarts. Check `pwd`, `ls -la`, `touch scratch.txt`, `nyitsec-answer`, and correct/wrong solution submissions after deployment.

## Officer QA: verified answer and repeatable solution

**Exact correct answer (in prompt order):** `NYITSEC-BASE64-START-26`  
**Deliberately incorrect test input:** `NYITSEC-BASE64-START-25`  
**Input policy:** The checker ignores surrounding whitespace and case.

### Reproduce the intended solution

Decode the practice message **once**:

```bash
cd /nyitsec-ctf
base64 -d message.b64
```

Read the line `Answer code: NYITSEC-BASE64-START-26`.

### Noninteractive checker test over SSH

Run this self-contained Python probe **inside a fresh SSH-connected challenge instance**. It executes the existing `nyitsec-answer` command twice, one known-wrong and one known-correct submission. It checks exit status, the exact rejection message, and the presence of a correctly shaped platform flag, but **never prints or saves the flag**. `BLOCKED` means the verifier or environment could not be validated, not that the challenge was solved.

```python
import re
import subprocess
import sys

# Inputs are fictional training data from this private officer guide.
cases = [
    ("incorrect", ["NYITSEC-BASE64-START-25"], False),
    ("correct", ["NYITSEC-BASE64-START-26"], True),
]
rejection_text = "Not quite. Decode the provided file and try again."
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
