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

This **automatically registers** the new challenge in `fundamentals/module.yml` and creates the required executable startup script, `nyitsec-answer` command, verifier, and documentation.

To create a **new module and its first challenge**:

~~~bash
python3 scripts/new_challenge.py --module web-basics --new-module-name "Web Security Basics" --id first-request --name "Your First HTTP Request"
~~~

That also registers `web-basics` in `dojo.yml`.

## What you need to customize

- `DESCRIPTION.md`: objective and instructions for students, including `nyitsec-answer`. If students create scripts, show them how to use a writable path such as `~/audit.sh` with `nano ~/audit.sh` (Ctrl+O, Enter, Ctrl+X) and `bash ~/audit.sh`. Keep provided challenge files under `/challenge` read-only; use absolute paths when reading them from students' scripts.
- `verify`: implement `is_correct(answer)`. The generated stub **always returns False** until you implement your solution check. Read `/flag` only after validation succeeds.
- Add fictional challenge files (logs, data, code, etc.), and document any dependencies in the author `README.md`.

Avoid plaintext secrets, real-world target data, and hardcoded reusable flags. Never commit the dojo updater URL or its update code. pwn.college generates the real per-student `/flag`.

## What is already handled for you

New challenges start interactive terminals in `/challenge` and add `nyitsec-answer` to the terminal command search path. Students can still navigate normally, and the original verifier remains callable as `/challenge/verify`.

The startup hook is **challenge-container local**, not a change to student persistent shell settings.

## Checks and deployment

~~~bash
python3 scripts/validate_dojo.py
python3 -m unittest discover -s tests -v
~~~

These checks also run automatically in GitHub Actions. They catch invalid/duplicate YAML keys, missing files, missing executable permissions, and unfinished TODOs.

Work on a feature branch and submit a PR. Once it is reviewed and merged into `main`, validation must pass before GitHub Actions updates the dojo. Then test the new challenge in a fresh pwn.college workspace, using both wrong and correct answers.

The former pwn.college template modules are retained as references and are excluded from the NYITSec convenience enforcement.

**Limitation:** The setup happens automatically when you run the generator. If you create a custom challenge manually, the CI validation will require you to add the same files before merge. This avoids modifying upstream examples and challenges that intentionally need another workflow.
