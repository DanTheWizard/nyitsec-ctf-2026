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
