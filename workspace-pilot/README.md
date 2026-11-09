# NYITSec Writable Workspace Pilot (Experimental)

This module is a temporary parallel test of the proposed student experience. Do **not** migrate existing fundamentals challenges or the shared `scripts/new_challenge.py` template yet.

## Why three copies?

- `incident-id`: simple log-reading exercise (source data must stay untouched under `/challenge` for verifier integrity).
- `base64-basics`: demonstrates writing decoded output into the working directory.
- `password-audit`: demonstrates authoring a Bash script alongside the copied data.

Each pilot challenge starts in writable **`/nyitsec-ctf`**. Files staged from `/challenge` are copied into the workspace as regular files, not links. The protected `/challenge/verify` and `bin/nyitsec-answer` continue working via the existing path.

## Hardcoded exclusions and optional ignore file

The mandatory Python exclusions are: `.init`, `.workspace.py`, `.ctfignore`, `verify`, `bin`, `README.md`, and `DESCRIPTION.md`, including nested occurrences. Each pilot has a `.ctfignore` for extra filename, path, or directory-prefix exclusion rules. This is a **small subset** of Gitignore syntax and has no negation rules. Copying is non-following for source symlinks and never copies special files.

## Persistence

The workspace is container-local and disappears when the challenge instance is replaced. It is **not linked to the student's home directory**. Warn students to copy any scripts they want to keep into `~/` before leaving.

The pilot's startup intentionally fails if `/nyitsec-ctf` already exists, instead of removing or overwriting anything. It should be a fresh path in an ordinary new challenge container.

## Testing checklist

Try all three exercises with the official pwn.college terminal. Confirm:
- `pwd` opens at `/nyitsec-ctf`.
- Expected challenge input files are present and writable.
- `verify`, `bin/`, and hidden initialization files are absent from the staged workspace.
- `touch scratch.txt` and `nano scratch.sh` work without permission errors.
- `nyitsec-answer` correctly reports wrong/correct answers and displays the student-specific flag on success.
- Another terminal in the **same** challenge instance does not reset any student work.
- Restart/replacement brings up a fresh workspace without old scratch files.
- The existing fundamentals module retains its original `/challenge` behavior.

Only after live verification should the shared generator and validators be migrated.

## Post-pilot migration

The writable workspace system has now been adopted in the five regular Fundamentals challenges and the shared generator/template. This pilot is retained temporarily as a known-good comparison while officers verify the live migration. Remove this module from `dojo.yml` only after the real Fundamentals challenges pass their smoke tests.
