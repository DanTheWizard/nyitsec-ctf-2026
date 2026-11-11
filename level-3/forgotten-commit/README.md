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

- Canonical `.workspace.py` first creates the writable `/nyitsec-ctf` directory. The precise approved `HISTORY_INIT_SUFFIX` then locks `.history-builder.py` and these officer notes to `0600`, and invokes the generator as root.
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
