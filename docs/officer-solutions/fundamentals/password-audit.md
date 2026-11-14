# Weak Password Audit — Officer Notes

**Module:** `fundamentals` | **Challenge ID:** `password-audit`

## Defensive learning goal

This is a **synthetic, authorized, offline password-strength audit**. The fictional development team provided a test credential hash and the synthetic candidate list intentionally contains a weak matching password. The student experiences a very small, controlled version of **offline dictionary guessing** to understand why predictable passwords and fast, unsalted password hashes are unsafe.

There are **no real usernames, accounts, authentication endpoints, stolen credentials, or external targets**.

The student should use AI to understand or help construct a Bash loop that:

1. Reads `sha256=` from `audit_record.txt`.
2. Reads `common_passwords.txt` one candidate per line (using `while IFS= read -r`).
3. Hashes each candidate *without a trailing newline* using `printf '%s' "$candidate" | sha256sum`.
4. Compares the result to the target digest and prints the first match.
5. Exits without attempting to authenticate anywhere.

The result is entered via `nyitsec-answer`, which delegates to the privileged `verify` script. The verifier reads pwn.college's unique `/flag` only for the correct synthetic test password.

## Important security concepts

SHA-256 here is intentionally **unsalted and fast** to make the exercise accessible for beginner Bash scripting. It is **not appropriate for password storage**. The teaching discussion should cover unique salts, slow password hashing (such as Argon2id), strong unique passwords, and MFA as layered defenses.

No real password or pwn.college flag is stored in this challenge. The fictional matching candidate appears in the synthetic wordlist by design.

## Where students should write scripts

**The writable directory is now `/nyitsec-ctf`.** At startup, `.workspace.py` copies the two synthetic input files there while keeping the protected originals in `/challenge`.

Students can run:

```bash
nano audit.sh
# Press Ctrl+O and Enter to save; Ctrl+X to exit.
bash audit.sh
```

The AI prompt explicitly requests both editor instructions and an offline Bash loop. A fixed `candidate="..."` checks only one guess; the objective is iterating over the entire synthetic list with `while IFS= read -r candidate`.

The temporary workspace is destroyed when the challenge container is restarted or replaced. Students who want to keep their work should copy it to `~/` first.

## Standard NYITSec conveniences

- Executable `.init` configures interactive Bash to start in `/nyitsec-ctf`.
- Executable `bin/nyitsec-answer` appears on the challenge PATH.
- Executable `verify` compares the supplied password's exact bytes and reveals `/flag` on a match.
- Student instructions are in `DESCRIPTION.md`.

## Smoke test

1. Launch a fresh workspace. Verify `pwd` shows `/nyitsec-ctf`.
2. Read `audit_record.txt` and `common_passwords.txt`.
3. Confirm `nano audit.sh` and `bash audit.sh` work in `/nyitsec-ctf` and an offline loop finds exactly one match.
4. Verify the matching answer succeeds with `nyitsec-answer`; a wrong guess or a case-changed guess must fail.
5. Submit the resulting pwn.college flag and confirm the solve is recorded.
6. Discuss mitigations without implying that any real incident occurred.

The offline test suite checks the local wordlist, SHA-256 data integrity, Bash demonstration logic, and answer verifier without touching `/flag`.

## Writable workspace standard

The `.init` startup script prepares `/nyitsec-ctf` by running `.workspace.py` and opens interactive terminals there. Challenge input copies are writable by `hacker`; protected files remain in `/challenge`. The blacklist in `.ctfignore` may add exclusions, but protected core names cannot be copied. The workspace is disposable across challenge restarts. Check `pwd`, `ls -la`, `touch scratch.txt`, `nyitsec-answer`, and correct/wrong solution submissions after deployment.

## Officer QA: verified answer and repeatable solution

**Exact correct answer (in prompt order):** `Welcome2026!`  
**Deliberately incorrect test input:** `Welcome2026`  
**Input policy:** Password matching is **case-sensitive** and whitespace-sensitive. Do not trim or casefold the candidate.

### Reproduce the intended solution

Read the synthetic hash and calculate SHA-256 for each local wordlist entry without a trailing newline:

```bash
cd /nyitsec-ctf
target=$(sed -n 's/^sha256=//p' audit_record.txt)
while IFS= read -r candidate; do
  actual=$(printf '%s' "$candidate" | sha256sum)
  if [ "${actual%% *}" = "$target" ]; then
    printf 'Matching synthetic password: %s\n' "$candidate"
  fi
done < common_passwords.txt
```

Exactly one candidate matches: `Welcome2026!`. No real account is accessed.

### Noninteractive checker test over SSH

Run this self-contained Python probe **inside a fresh SSH-connected challenge instance**. It executes the existing `nyitsec-answer` command twice, one known-wrong and one known-correct submission. It checks exit status, the exact rejection message, and the presence of a correctly shaped platform flag, but **never prints or saves the flag**. `BLOCKED` means the verifier or environment could not be validated, not that the challenge was solved.

```python
import re
import subprocess
import sys

# Inputs are fictional training data from this private officer guide.
cases = [
    ("incorrect", ["Welcome2026"], False),
    ("correct", ["Welcome2026!"], True),
]
rejection_text = "Not a match. Review the candidate hashes and try again."
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
