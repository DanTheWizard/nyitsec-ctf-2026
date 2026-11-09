# Contributing NYITSec CTF Challenges

This guide is for club officers, other students contributing challenges, and AI code assistants.

## Create a challenge in an existing module

Install Python 3 and the small YAML development dependency:

~~~bash
python3 -m pip install -r requirements-dev.txt
~~~

Generate the standard challenge structure:

~~~bash
python3 scripts/new_challenge.py --module fundamentals --id find-the-clue --name "Find the Clue"
~~~

This **automatically registers** the new challenge in `fundamentals/module.yml` and creates the standard startup script, writable workspace copier, optional exclusion file, protected verifier, `nyitsec-answer` shortcut, and documentation.

To create a **new module and its first challenge**:

~~~bash
python3 scripts/new_challenge.py --module web-basics --new-module-name "Web Security Basics" --id first-request --name "Your First HTTP Request"
~~~

That also registers `web-basics` in `dojo.yml`.

## What you need to customize

- `DESCRIPTION.md`: objective and instructions for students, including `nyitsec-answer`. Student files are staged in writable `/nyitsec-ctf`. Teach `nano audit.sh` (Ctrl+O, Enter, Ctrl+X) followed by `bash audit.sh`. Warn that this is a temporary, nonpersistent directory; students may copy finished work to `~/` for safekeeping.
- `verify`: implement `is_correct(answer)`. The generated stub **always returns False** until you implement your solution check. Read `/flag` only after validation succeeds.
- Add fictional challenge files (logs, data, code, etc.), and document any dependencies in the author `README.md`.

Avoid plaintext secrets, real-world target data, and hardcoded reusable flags. Never commit the dojo updater URL or its update code. pwn.college generates the real per-student `/flag`.

## What is already handled for you

New challenges open interactive terminals in writable `/nyitsec-ctf`, populated with ordinary student-facing files copied from `/challenge`. The startup script excludes protected implementation files and honors optional `.ctfignore` patterns. `nyitsec-answer` stays on the terminal command search path and the original verifier remains callable as `/challenge/verify`.

The startup hook is **challenge-container local**, not a change to student persistent shell settings. The workspace is reset when its challenge container is replaced; student work there is **not persistent**. Do not put real secrets or privileged programs into copied assets.

To customize the files being staged, add extra patterns to the challenge's `.ctfignore`. This supports simple filename globs and directory exclusions, not full Gitignore syntax or negation rules. The core protected exclusions cannot be overridden.

## Checks and deployment

~~~bash
python3 scripts/validate_dojo.py
python3 -m unittest discover -s tests -v
~~~

These checks also run automatically in GitHub Actions. They catch invalid/duplicate YAML keys, missing helper files, missing executable permissions, drift from the shared workspace template, unfinished TODOs, and student instructions missing the writable workspace location.

Work on a feature branch and submit a PR. Once it is reviewed and merged into `main`, validation must pass before GitHub Actions updates the dojo. Then test the new challenge in a fresh pwn.college workspace, using both wrong and correct answers.

The former pwn.college template modules are retained as references and excluded from the NYITSec convenience enforcement. The `workspace-pilot` module remains available as a temporary live-test comparison until the Fundamentals migration is verified.

**Limitation:** The setup happens automatically when you run the generator. If you create a custom challenge manually, the CI validation will require you to add the same files before merge. This avoids modifying upstream examples and challenges that intentionally need another workflow.
