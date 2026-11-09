# NYITSec Workspace Pilot — incident-id

This exercise is a **copy** of `fundamentals/incident-id` for controlled testing of the writable workspace. The original challenge must remain unchanged.

- `.init` invokes `/challenge/.workspace.py` as root to prepare `/nyitsec-ctf`, then appends a guarded Bash start-directory rule to the container's `/etc/bashrc`. It does not modify persistent `~/.bashrc`.
- `.workspace.py` stages only regular files and directories (never symlinks or special files). It strips inherited file modes, makes copies owned by `hacker`, and never overwrites an existing workspace.
- The mandatory exclude list protects `.init`, `verify`, `bin/`, `README.md`, `DESCRIPTION.md`, and workspace setup/config files. `.ctfignore` adds optional simple glob exclusions.
- `/challenge/verify` and `/challenge/bin/nyitsec-answer` are unchanged from the original example. Checkers remain privileged and use pwn.college's per-student `/flag`.
- The workspace is **temporary and NOT persistent**. No data is copied to `/home/hacker` during setup.

## Live smoke test

1. Open a fresh workspace and confirm `pwd` is `/nyitsec-ctf`; `ls -la` shows only the expected lab input files.
2. Create, edit, and execute a simple script or file as `hacker`. Verify `touch pilot-test.txt` succeeds.
3. Confirm `/challenge/verify` remains executable and `nyitsec-answer` works without copying either file.
4. Open another terminal in the same instance and verify startup still works without deleting student files.
5. Restart the instance and confirm the old scratch file is absent, showing container isolation.
6. Verify original `fundamentals/incident-id` has not changed.

If these checks pass for all three pilot exercises, update the standard template, generator, and checker validation in a **separate** subsequent PR.
