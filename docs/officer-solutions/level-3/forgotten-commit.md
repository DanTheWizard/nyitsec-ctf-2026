# The Forgotten Commit — Officer notes

**Module:** `level-3` | **Challenge ID:** `forgotten-commit` | **Difficulty:** Early Intermediate

## Story and generated repository

Students investigate **Night Relay**, an entirely fictional amateur-satellite monitoring project. At challenge startup, `.history-builder.py` initializes a genuine `/nyitsec-ctf/night-relay` Git repository, creates **10 authored commits** spanning a simulated September 2026 development history, and leaves the current checkout missing an important file.

The history contains meaningful decoys: sample telemetry, maintenance notes, a mock contact list deleted during a different cleanup, console settings, and an earlier **draft** version of the recovery ledger that does not contain the final phrase. The correct file's last approved version was deleted in a later commit.

All Git authors and email addresses use fictional identities and the reserved `example.test` namespace. The project is offline and its sample `src/status.py` reads static data only.

## Intended solution

1. `cd /nyitsec-ctf/night-relay`
2. `cat docs/incident-204.md` and `git status`.
3. `git log --oneline --all` to explore ten commits.
4. `git log --all --diff-filter=D --summary` to find deleted paths. There are two, one unrelated.
5. Find the deletion of **`config/recovery-ledger.toml`**. It appears in the commit titled `cleanup: remove retired handoff ledger`.
6. Recover the file from the deletion commit's parent with `git show <delete-commit>^:config/recovery-ledger.toml`. Another option is `git log --all -- config/recovery-ledger.toml` followed by `git show <approved-commit>:config/recovery-ledger.toml`.
7. The approved ledger has `recovery_phrase = "Paper satellites still orbit"` in its `[handoff]` section.
8. Run `nyitsec-answer` with **Paper satellites still orbit**. Matching ignores case and surrounding whitespace; the protected checker reveals only the student's per-user pwn.college `/flag` after success.

If desired, students may use `git restore --source=<approved-commit> -- config/recovery-ledger.toml`, but inspecting with `git show` avoids changing the checkout.

## Startup and isolation

- Canonical `.workspace.py` first creates the writable `/nyitsec-ctf` directory. The precise approved `HISTORY_INIT_SUFFIX` then locks `.history-builder.py` and the remaining runtime resources to `0600`, and invokes the generator as root. The officer notes are not present inside `/challenge`.
- The generator refuses to overwrite an existing `night-relay` directory. It uses the **genuine offline Git executable** installed at startup from the bundled Ubuntu 24.04 runtime, scripted fixed commits, and fake authors; all operations are restricted to the newly created repository. Generated files **including the full `.git` directory** are assigned to `hacker` with mode `0600` for files and `0700` for directories.
- The builder, bundled Git archive, provenance manifest, and preparatory script are excluded via `.ctfignore`, so its source (and plaintext expected phrase) is not copied to the student workspace. The source is nevertheless fully reviewable in the connected GitHub repository.
- No local server, privileged runtime network service, external clone, SSH, or real organizational data is involved.
- A fresh challenge instance rebuilds the same fictional Git history. Another terminal within one instance does not regenerate or overwrite it. **Reset Challenge** restores the repo.
- `verify` stores the SHA-256 digest, not a static platform flag. `bin/nyitsec-answer` is the canonical shortcut.

## Live smoke tests

1. Launch the challenge and verify `git --version` works using the bundled tool. No `apt` or network access is required.
2. `cd /nyitsec-ctf/night-relay`; `git status` should report a clean checkout on `main`.
3. `git log --oneline` should list ten commits; the recent entry records incident 204.
4. `ls config/` should show `console.ini` but not the recovery ledger.
5. `git log --diff-filter=D --summary` should reveal two deletions.
6. Recover the approved ledger using `git show <deleting-commit>^:config/recovery-ledger.toml`.
7. Verify `nyitsec-answer` rejects the draft phrase and accepts the approved phrase.
8. Try `cat /challenge/.history-builder.py` as `hacker`; it should fail with permission denied.
9. Reset and verify the deleted file is again absent from HEAD and the Git history is intact.

## Offline Git dependency

The published pwn.college package profile does not list Git by default, so this challenge bundles **genuine Git**, not a simulated command. `.git-prepare.sh` extracts the executable and libraries to disposable `/run/nyitsec-git`, then `/challenge/bin/git` exposes ordinary Git commands on the student PATH. `tools/build_forgotten_git_runtime.py` reproduces the bundle. Third-party provenance is documented in `tools/FORGOTTEN_GIT_RUNTIME_LICENSES.md` and the hidden runtime manifest. The startup and bundle are excluded from the working directory, and the exact source history generator is committed for NYITSec and ITS inspection.

## Officer QA: verified answer and repeatable solution

**Exact correct inputs (prompt order):** `Paper satellites still orbit`  
**Deliberately incorrect test inputs:** `Not the recovery phrase`  
**Input policy:** Case-insensitive; leading/trailing whitespace is stripped.

### Reproduce the intended solution

Inspect the fictional generated Git repository, without changing it:

```bash
cd /nyitsec-ctf/night-relay
git status
git log --oneline --all
git log --all --diff-filter=D --summary
git log --all -- config/recovery-ledger.toml
```

Find the deletion commit titled `cleanup: remove retired handoff ledger`, then use the parent revision (replace the placeholder with the actual hash):

```bash
git show <deletion-commit>^:config/recovery-ledger.toml
```

The approved ledger contains `recovery_phrase = "Paper satellites still orbit"`. The old draft phrase is not accepted. No static Git commit SHA is assumed.

### Noninteractive checker test over SSH

Run this self-contained Python probe **inside a fresh SSH-connected challenge instance**. It executes the existing `nyitsec-answer` command twice, one known-wrong and one known-correct submission. It checks exit status, the exact rejection message, and the presence of a correctly shaped platform flag, but **never prints or saves the flag**. `BLOCKED` means the verifier or environment could not be validated, not that the challenge was solved.

```python
import re
import subprocess
import sys

# Inputs are fictional training data from this private officer guide.
cases = [
    ("incorrect", ["Not the recovery phrase"], False),
    ("correct", ["Paper satellites still orbit"], True),
]
rejection_text = "That is not the approved recovery phrase. Check the repository history."
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

Keep this literal solution in the **private officer guide only**, never in the student-facing challenge directory or logs. Do not record platform flag values.
