# Officer notes: Inspect the Source

**Module:** `level-2` | **ID:** `inspect-source` | **Difficulty:** Easy

## Purpose

Students learn that a website can expose information through its **HTML source**, including comments that are not rendered in the visible page. This is a fictional, isolated web-service exercise, not an exercise involving a public website.

The browser-visible site is a polished fictional Harborview Learning Center landing page. An internal QA comment contains the synthetic answer code; the student sees it only when inspecting the HTML source, not in the rendered page. The protected checker stores a SHA-256 digest and reveals pwn.college's per-student `/flag` after an exact match.

## Challenge startup

- Standard `.init` staging and Bash startup remain **byte-for-byte identical to the shared template**, except for an approved, validated two-line extension to call `/challenge/.website-start.sh`.
- `.website-start.sh` locks down `/challenge/.website.py` to mode `0600`, launches a local Python HTTP server in the background, and waits until an HTTP health check passes. This protects the source file from ordinary filesystem inspection while leaving the public HTML accessible through HTTP.
- `.website.py` binds only to **127.0.0.1:8765**, serves **GET / or /index.html** and a 204 favicon, has no uploads or dynamic parameters, sets basic security headers, and **drops to the `hacker` UID after binding**. The HTML is generated in memory; no `.html` file is copied into the student workspace.
- `.ctfignore` explicitly excludes the server implementation and its startup script from `/nyitsec-ctf`.
- The student's `/nyitsec-ctf` starts empty for this challenge. Their intended investigation path is **Workspace → Desktop → Firefox → http://127.0.0.1:8765/**.

**Important limitation:** No ordinary web server can guarantee that only Firefox can inspect HTTP source; a student could also use `curl` or another HTTP client. The exercise makes the browser the expected learning workflow, without fragile user-agent filters or artificial access restrictions.

## Live smoke tests

1. Launch the challenge and check `pwd` shows `/nyitsec-ctf`, with no website implementation files staged.
2. Open Workspace → Desktop → Firefox and load **http://127.0.0.1:8765/**. Confirm the fictional page renders without errors or external content.
3. Use **View Page Source** or **Ctrl+U**. Confirm the internal publishing comment contains the review code.
4. Verify `ls -la /nyitsec-ctf` has no `.website.py` and `cat /challenge/.website.py` reports permission denied.
5. Confirm `nyitsec-answer` rejects incorrect input and accepts the exact code from the HTML source, revealing the unique platform flag.
6. Verify old Fundamentals and Level 2 exercises remain unchanged.

The root-owned initialization script's web-service suffix is checked by the repository validator, and the Python unit tests exercise HTTP serving, HTML source, permissions conventions, workspace copy exclusions, and answer validation.

## Officer QA: verified answer and repeatable solution

**Exact correct answer:** `NYITSEC-SOURCE-26`  
**Deliberately incorrect input:** `NYITSEC-SOURCE-27`  
**Input policy:** Case-sensitive; leading/trailing whitespace is stripped.

### Reproduce the intended solution

With the challenge's localhost service running, use Desktop → Firefox → `http://127.0.0.1:8765/` and View Page Source / Ctrl+U. The HTML comment contains `Training review code: NYITSEC-SOURCE-26`.

For headless officer QA via SSH, the equivalent safe local request is:

```bash
curl --fail --silent http://127.0.0.1:8765/ | grep 'Training review code'
```

Only localhost is contacted. No external website is involved.

### Noninteractive checker test over SSH

Run this self-contained Python probe **inside a fresh SSH-connected challenge instance**. It executes the existing `nyitsec-answer` command twice, one known-wrong and one known-correct submission. It checks exit status, the exact rejection message, and the presence of a correctly shaped platform flag, but **never prints or saves the flag**. `BLOCKED` means the verifier or environment could not be validated, not that the challenge was solved.

```python
import re
import subprocess
import sys

# Inputs are fictional training data from this private officer guide.
cases = [
    ("incorrect", ["NYITSEC-SOURCE-27"], False),
    ("correct", ["NYITSEC-SOURCE-26"], True),
]
rejection_text = "That code is not correct. Inspect the site's HTML source and try again."
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
