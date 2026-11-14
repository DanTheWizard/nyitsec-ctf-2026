# Author notes: SSH Log Investigation

**Learning goal:** inspect fictional authentication logs and identify the unique row where `service=ssh`, `source=external`, and `status=blocked`.

## Student-friendly conveniences

- `/challenge/.init` runs as root when the instance starts. It installs a small, idempotent Bash startup snippet into this container's `/etc/bashrc`.
- On a new **interactive** Bash terminal launched in `/home/hacker`, the snippet moves to `/nyitsec-ctf`. A student who navigated elsewhere is not redirected.
- `/challenge/bin/nyitsec-answer` is an executable wrapper around the existing `/challenge/verify` program.
- pwn.college automatically includes `/run/challenge/bin` in `PATH` and normally links it to `/challenge/bin`, so students can run `nyitsec-answer` from any directory.
- The wrapper never reads `/flag` directly. Only the original protected `exec-suid` verifier can access it after a correct answer.
- The hook changes only the temporary challenge container's `/etc/bashrc`; it does **not** modify the student's persistent `~/.bashrc`.

Do not add auto-directory-changing startup files to navigation-learning challenges where directory position is part of the learning objective.

## Files

- Student instructions: `DESCRIPTION.md`
- Fictional log data: `events.log`
- Original verifier: `verify` (must remain executable)
- Shell startup: `.init` (must be executable)
- Friendly command: `bin/nyitsec-answer` (must be executable)
- Flag: student-specific, root-protected pwn.college `/flag`; no static flags are committed

The IP addresses belong to RFC 5737 documentation-only ranges.

## Smoke test after deployment

1. Launch **First Incident** and open a **new** terminal.
2. Run `pwd`; expect `/nyitsec-ctf`.
3. Run `type -a nyitsec-answer`; it should resolve via `/run/challenge/bin`.
4. Run `cat events.log`; it should show the simulated events.
5. Run `nyitsec-answer` with an incorrect ID; no flag should print.
6. Run `nyitsec-answer` with the unique matching ID; the program should print the student's flag.
7. Submit the flag to confirm pwn.college records the solve.
8. Run `cd /tmp` and `pwd`; confirm students can still navigate freely.
9. Relaunch another unrelated dojo challenge; the NYITSec-specific auto-cd must not persist.

## Writable workspace standard

The `.init` startup script prepares `/nyitsec-ctf` by running `.workspace.py` and opens interactive terminals there. Challenge input copies are writable by `hacker`; protected files remain in `/challenge`. The blacklist in `.ctfignore` may add exclusions, but protected core names cannot be copied. The workspace is disposable across challenge restarts. Check `pwd`, `ls -la`, `touch scratch.txt`, `nyitsec-answer`, and correct/wrong solution submissions after deployment.

## Officer QA: verified answer and repeatable solution

**Exact correct answer (in prompt order):** `NY-106`  
**Deliberately incorrect test input:** `NY-105`  
**Input policy:** The event ID must match exactly, including case and hyphen.

### Reproduce the intended solution

Inspect `events.log` and filter by all three conditions, not just one:

```bash
cd /nyitsec-ctf
grep 'service=ssh source=external status=blocked' events.log
```

The only matching row is `event=NY-106` (external SSH, blocked).

### Noninteractive checker test over SSH

Run this self-contained Python probe **inside a fresh SSH-connected challenge instance**. It executes the existing `nyitsec-answer` command twice, one known-wrong and one known-correct submission. It checks exit status, the exact rejection message, and the presence of a correctly shaped platform flag, but **never prints or saves the flag**. `BLOCKED` means the verifier or environment could not be validated, not that the challenge was solved.

```python
import re
import subprocess
import sys

# Inputs are fictional training data from this private officer guide.
cases = [
    ("incorrect", ["NY-105"], False),
    ("correct", ["NY-106"], True),
]
rejection_text = "Not quite. Check the service, source, and status."
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

The literal answer above is synthetic challenge data stored **only in private officer documentation**, never in student-facing `DESCRIPTION.md`, `/challenge/README.md`, or the writable workspace. Do not save actual platform flags in QA reports.
