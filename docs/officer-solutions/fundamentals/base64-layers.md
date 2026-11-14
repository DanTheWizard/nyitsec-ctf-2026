# Author notes: Base64 Layers

**Module:** fundamentals | **ID:** base64-layers

This exercise follows Base64 Basics. The text was encoded with Base64 **three times**. The final readable plaintext contains an answer code, but the static code is not a platform flag. pwn.college provides a different `/flag` for each student.

- `.init`, `bin/nyitsec-answer`, and `verify` follow the standard NYITSec challenge template.
- `message.b64` is a deliberately triple-encoded synthetic message; no live secrets are present.
- The verifier checks a one-way digest of the decoded answer code and only then reveals the student's real flag.

### Test after deployment

1. Run `base64 -d message.b64`. Output should still resemble Base64.
2. Decode again; output should still resemble Base64.
3. Decode a third time and confirm the answer code is visible.
4. Check `nyitsec-answer` rejects incorrect codes and accepts the decoded code.
5. Submit the printed flag and confirm a solve is registered.

The offline CI tests verify all three decoding layers and the answer checker.

## Writable workspace standard

The `.init` startup script prepares `/nyitsec-ctf` by running `.workspace.py` and opens interactive terminals there. Challenge input copies are writable by `hacker`; protected files remain in `/challenge`. The blacklist in `.ctfignore` may add exclusions, but protected core names cannot be copied. The workspace is disposable across challenge restarts. Check `pwd`, `ls -la`, `touch scratch.txt`, `nyitsec-answer`, and correct/wrong solution submissions after deployment.

## Officer QA: verified answer and repeatable solution

**Exact correct answer (in prompt order):** `NYITSEC-THREE-LAYERS-26`  
**Deliberately incorrect test input:** `NYITSEC-THREE-LAYERS-25`  
**Input policy:** The checker ignores surrounding whitespace and case.

### Reproduce the intended solution

Decode **three** layers, keeping stdout as the next layer's input:

```bash
cd /nyitsec-ctf
base64 -d message.b64 | base64 -d | base64 -d
```

Read the final `Answer code:` line.

### Noninteractive checker test over SSH

Run this self-contained Python probe **inside a fresh SSH-connected challenge instance**. It executes the existing `nyitsec-answer` command twice, one known-wrong and one known-correct submission. It checks exit status, the exact rejection message, and the presence of a correctly shaped platform flag, but **never prints or saves the flag**. `BLOCKED` means the verifier or environment could not be validated, not that the challenge was solved.

```python
import re
import subprocess
import sys

# Inputs are fictional training data from this private officer guide.
cases = [
    ("incorrect", ["NYITSEC-THREE-LAYERS-25"], False),
    ("correct", ["NYITSEC-THREE-LAYERS-26"], True),
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
