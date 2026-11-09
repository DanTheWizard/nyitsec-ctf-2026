# NYITSec Challenge Authoring

Read the repository's `AGENTS.md` and `CONTRIBUTING.md` before generating challenge files.

Use `python3 scripts/new_challenge.py` to create all new NYITSec challenges. It installs the standard `.init` interactive `/nyitsec-ctf` startup hook, `.workspace.py` staging helper, `.ctfignore` exclusion rules, protected `bin/nyitsec-answer`, `verify`, and student/author docs. Ensure instructions explain temporary workspace data loss and show scripts being saved in `/nyitsec-ctf`. Implement the fail-closed verifier, keep pwn.college `/flag` student-specific and protected, and never commit credentials. Run `python3 scripts/validate_dojo.py` and the unit tests before opening a pull request.
