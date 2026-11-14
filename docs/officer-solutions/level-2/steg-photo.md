# Officer Notes: The Photograph's Secret

**Module:** `level-2` | **ID:** `steg-photo` | **Difficulty:** Easy

## Design
`evidence.jpg` is a valid JPEG image containing a **real embedded file created with the genuine `steghide` program** (not an appended plaintext or EXIF comment). The hidden file contains a fictional NYITSec case response code. `case-note.txt` supplies the steghide passphrase, so students practice extraction rather than password guessing.

This is an authorized, synthetic digital-forensics lesson. The answer checker stores a digest of the response code and reveals only the student's pwn.college `/flag` after a correct solution.

## Tool availability
The default pwn.college workspace package list does not explicitly include steghide. To make this lab self-contained, the challenge includes `bin/steghide`, a nonprivileged shell wrapper that extracts an offline tool bundle into a freshly created temporary directory, sets the necessary shared library search path, invokes steghide, and then removes the temporary tool files.

- The bundled tool archive lives at `/challenge/.steghide-runtime.tar.gz` and is excluded from the student workspace via `.ctfignore`.
- `/challenge/bin/steghide` is a shell wrapper; it launches the extracted binary as the student, not as root. No bundled executable is setuid.
- The bundle was produced from Ubuntu packages on GitHub Actions. Preserve package provenance and licensing notes whenever rebuilding it.
- Do not use `apt-get` in the challenge's 30-second `.init` window, and do not change the shared NYITSec workspace initializer.
- If bundled libraries prove incompatible with the pwn.college base image, prefer a published challenge-specific image that includes steghide rather than a network installation at startup.

## Live smoke tests
1. In `/nyitsec-ctf`, confirm `evidence.jpg` and `case-note.txt` are writable student copies.
2. Run `steghide --version` and `steghide info evidence.jpg`. Confirm the tool runs without dependency errors.
3. Read the passphrase from `case-note.txt`, then extract the embedded file with `steghide extract -sf evidence.jpg -p cookie-jar`.
4. Read `hidden-note.txt` and submit its response code with `nyitsec-answer`.
5. Confirm incorrect answers reveal no flag and correct answers reveal the student's unique pwn.college flag.
6. Confirm original Fundamentals challenges remain unchanged.

**Note:** The real steghide extraction is verified in CI against the committed JPEG using the bundled tool before deployment. Also perform this live smoke test after merge.

## Officer QA: verified answer and repeatable solution

**Exact correct answer:** `PHOTO-CRUMB-26`  
**Deliberately incorrect input:** `PHOTO-CRUMB-25`  
**Input policy:** Case-sensitive; leading/trailing whitespace is stripped.

### Reproduce the intended solution

Read the fictional evidence note for the passphrase, then use the supplied offline steghide wrapper:

```bash
cd /nyitsec-ctf
cat case-note.txt
steghide --version
steghide extract -sf evidence.jpg -p cookie-jar -xf hidden-note.txt -f
cat hidden-note.txt
```

The embedded synthetic document says `Response code: PHOTO-CRUMB-26`. A fresh challenge instance is recommended to avoid an existing extracted output file.

### Noninteractive checker test over SSH

Run this self-contained Python probe **inside a fresh SSH-connected challenge instance**. It executes the existing `nyitsec-answer` command twice, one known-wrong and one known-correct submission. It checks exit status, the exact rejection message, and the presence of a correctly shaped platform flag, but **never prints or saves the flag**. `BLOCKED` means the verifier or environment could not be validated, not that the challenge was solved.

```python
import re
import subprocess
import sys

# Inputs are fictional training data from this private officer guide.
cases = [
    ("incorrect", ["PHOTO-CRUMB-25"], False),
    ("correct", ["PHOTO-CRUMB-26"], True),
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
