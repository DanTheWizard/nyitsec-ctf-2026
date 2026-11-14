# Officer Notes: The Forgotten File

**Module:** `level-2` | **ID:** `forgotten-file` | **Difficulty:** Easy

## Objective

Students practice recursive file discovery and content searches rather than manually checking guessed filenames. This is a fictional, authorized digital-evidence exercise.

Each fresh pwn.college challenge container generates a tree of **nine top-level areas, 36 nested branches, and 108 ordinary files**. File names and everyday document contents vary. One ordinary document is selected randomly to include a short investigation note and a synthetic case code; the filename gives no special indication that it contains the clue.

There is no fixed target path in the challenge or student instructions. `random.SystemRandom()` selects the location on every new container launch, but two unrelated launches could coincidentally select the same path. A new terminal within the same container does not regenerate the tree.

## Startup and protected implementation

- The standard `.workspace.py` creates `/nyitsec-ctf` as usual.
- `.init` extends the shared initializer with the approved `RANDOM_ARCHIVE_INIT_SUFFIX`; the root-owned `/challenge/.scatter.py` runs once **after** workspace creation.
- `.init` changes `.scatter.py` to mode `0600` before running it. The `.ctfignore` also excludes it from the student workspace.
- `.scatter.py` refuses to overwrite a nonempty workspace, writes synthetic decoys, appends one clue, then sets directory and file ownership to the unprivileged `hacker` account. New files are nonexecutable.
- The protected `verify` compares an answer digest and reveals only the student's pwn.college `/flag` on success. `bin/nyitsec-answer` is unchanged.

The answer phrase is purposefully present in the root-owned generation code and in the generated random document. The private repository is an **authoring source**, not a secret store.

## Manual live tests

1. Start Level 2 → The Forgotten File, confirm `pwd` is `/nyitsec-ctf`, and `find . -type f | wc -l` reports 108.
2. Try `grep -Rni 'case' .` and `grep -Rni 'review' .`; these should return both noise and the actual clue.
3. Run `nyitsec-answer` with a wrong code (no flag) and the recovered code (student-specific flag).
4. Open another terminal in the same container. The files should remain unchanged.
5. Start a fresh challenge container, run `find`/`grep` again, and check the clue path can vary.
6. Confirm `cat /challenge/.scatter.py` is permission denied for `hacker`, while documents under `/nyitsec-ctf` are readable and writable.

Unit tests cover many seeded random layouts, exactly one clue, permission behavior, and the rejected-overwrite guard.

## Officer QA: verified answer and repeatable solution

**Exact correct answer:** `NYITSEC-LOST-26`  
**Deliberately incorrect input:** `NYITSEC-LOST-25`  
**Input policy:** Case-sensitive; leading/trailing whitespace is stripped. The answer code remains fixed, but the clue's document location is randomized on each launch.

### Reproduce the intended solution

Run a recursive content search over the generated 108-document archive:

```bash
cd /nyitsec-ctf
find . -type f | wc -l
grep -Rni 'Recovered code:' .
```

Exactly one document includes `Recovered code: NYITSEC-LOST-26`; its path may change after restarting the challenge. The generator's `CODE` constant is stable, not a new per-instance secret.

### Noninteractive checker test over SSH

Run this self-contained Python probe **inside a fresh SSH-connected challenge instance**. It executes the existing `nyitsec-answer` command twice, one known-wrong and one known-correct submission. It checks exit status, the exact rejection message, and the presence of a correctly shaped platform flag, but **never prints or saves the flag**. `BLOCKED` means the verifier or environment could not be validated, not that the challenge was solved.

```python
import re
import subprocess
import sys

# Inputs are fictional training data from this private officer guide.
cases = [
    ("incorrect", ["NYITSEC-LOST-25"], False),
    ("correct", ["NYITSEC-LOST-26"], True),
]
rejection_text = "That code is not correct. Search the archived documents and try again."
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

These are officer-only synthetic answers, not pwn.college flags. Do not add them to student-facing descriptions or record actual flag values in QA reports.
