# {{CHALLENGE_TITLE}} — Author Notes

**Module:** `{{MODULE_ID}}`
**Challenge ID:** `{{CHALLENGE_ID}}`

## Setup included automatically

- `/challenge/.init`: executes the workspace staging tool, then opens interactive terminals in `/nyitsec-ctf`.
- `/challenge/.workspace.py`: copies non-excluded regular challenge files into `/nyitsec-ctf`, makes them writable to `hacker`, and refuses to overwrite an existing workspace.
- `/challenge/.ctfignore`: extra exclude patterns; `.init`, `.workspace.py`, `.ctfignore`, `verify`, `bin/`, `README.md`, and `DESCRIPTION.md` are always excluded.
- `/challenge/bin/nyitsec-answer`: protected shortcut on pwn.college's challenge `PATH`.
- `/challenge/verify`: protected answer verifier. **Its `is_correct()` is a fail-closed stub and must be implemented.**
- `DESCRIPTION.md`: instructions visible to students.

The three executable files (`.init`, `verify`, `bin/nyitsec-answer`) must retain Git mode `100755`. The workspace setup files and student data use regular file mode `100644` in Git.

## Before merging

- [ ] Implement the verification logic in `verify` and check it does not reveal `/flag` prematurely.
- [ ] Replace the student-facing TODOs.
- [ ] Test wrong and correct answers in the live pwn.college challenge.
- [ ] Confirm `pwd` starts at `/nyitsec-ctf`, the expected input files appear, and `nyitsec-answer` runs.
- [ ] Confirm `touch test.txt` works; restarting the challenge creates a new temporary workspace.
- [ ] Confirm `verify`, `bin/`, and `.init` were not copied into `/nyitsec-ctf`.
- [ ] Confirm the checker still works if a student intentionally changes directory.
- [ ] Never commit secrets, reusable static flags, or updates to personal persistent shell settings.

**Temporary workspace notice:** Work in `/nyitsec-ctf` is lost when the challenge container is replaced. Tell students to save important work under `~/` before switching challenges.
