# Officer Notes: More Than a Cookie Recipe

**Module:** `level-2` | **ID:** `cookie-metadata` | **Difficulty:** Easy

## Design
`document.txt` contains a complete, readable chocolate chip cookie recipe, followed by an **ANSI-concealed trailer** containing a fictional case-code field.

- In an ANSI-compatible terminal, `cat document.txt` displays the recipe. The trailer's characters use the ANSI SGR *conceal* style (`ESC[8m`), followed by the reset sequence (`ESC[0m`).
- `strings document.txt` shows the printable trailer entries, including the `RECOVERY-CODE` field.
- Commands such as `cat -v`, `xxd`, or other binary inspection tools may also expose the data. All are valid investigative approaches.
- This is **embedded metadata-like text**, not actual filesystem extended attributes or EXIF metadata. Avoid describing it as file-system metadata.
- We intentionally **do not name the `strings` command in the student-facing description**.

**Important:** Some terminal implementations may handle ANSI conceal differently. Live-test `cat document.txt` in pwn.college's own terminal, not just offline tests. The student answer is the exact, case-sensitive code in the trailer.

The `verify` program compares a SHA-256 digest and reveals the student's own pwn.college flag only after the correct answer. Never expose a reusable platform flag.

## Smoke tests
1. `pwd` starts in `/nyitsec-ctf` and the file is present.
2. `cat document.txt` displays only the recipe in the standard pwn.college terminal.
3. `strings document.txt` reveals the case metadata and recovery code.
4. A wrong `nyitsec-answer` is rejected, and the correct code returns the unique student flag.

## Officer QA: verified answer and repeatable solution

**Exact correct answer:** `COOKIE-TRACE-26`  
**Deliberately incorrect input:** `COOKIE-TRACE-27`  
**Input policy:** Case-sensitive; leading/trailing whitespace is stripped.

### Reproduce the intended solution

Read the recipe normally, then inspect printable file contents to expose the ANSI-concealed trailer:

```bash
cd /nyitsec-ctf
cat document.txt
strings document.txt | grep 'RECOVERY-CODE'
```

The metadata-like trailer contains `RECOVERY-CODE=COOKIE-TRACE-26`. This is text concealed using an ANSI escape sequence, not a filesystem extended attribute.

### Noninteractive checker test over SSH

Run this self-contained Python probe **inside a fresh SSH-connected challenge instance**. It executes the existing `nyitsec-answer` command twice, one known-wrong and one known-correct submission. It checks exit status, the exact rejection message, and the presence of a correctly shaped platform flag, but **never prints or saves the flag**. `BLOCKED` means the verifier or environment could not be validated, not that the challenge was solved.

```python
import re
import subprocess
import sys

# Inputs are fictional training data from this private officer guide.
cases = [
    ("incorrect", ["COOKIE-TRACE-27"], False),
    ("correct", ["COOKIE-TRACE-26"], True),
]
rejection_text = "That code is not correct. Check your evidence and try again."
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
    success_lines = [i for i, line in enumerate(lines) if "Correct!" in line]

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

These are officer-only synthetic answers, not pwn.college flags. Do not add them to student-facing descriptions or record actual flag values in QA reports.
