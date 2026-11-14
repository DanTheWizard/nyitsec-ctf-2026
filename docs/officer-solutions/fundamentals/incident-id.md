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

Run these commands **inside the active challenge container** (the local Codex/SSH session can invoke them remotely). They check for the fixed `Correct!` success marker without printing or recording the student-specific pwn.college flag.

```bash
if printf '%s\n' 'NY-105' | nyitsec-answer | grep -Fq 'Correct!'; then
  echo 'FAIL: wrong input was accepted'
else
  echo 'PASS: wrong input rejected'
fi
if printf '%s\n' 'NY-106' | nyitsec-answer | grep -Fq 'Correct!'; then
  echo 'PASS: known correct input accepted'
else
  echo 'FAIL: known correct input rejected'
fi
```

The literal answer above is synthetic challenge data stored **only in private officer documentation**, never in student-facing `DESCRIPTION.md`, `/challenge/README.md`, or the writable workspace. Do not save actual platform flags in QA reports.
