# NYITSec CTF — Instructions for AI coding agents

These instructions apply to the entire repository, including code produced by ChatGPT, Codex, and other AI coding assistants.

## Goals and environment

- We maintain the NYITSec 2026 **hidden** pwn.college dojo in this GitHub repository.
- The YAML ID is now `nyitsec` and the display name is `NYITSec CTF 2026`. The previous testing dojo (`example~36e653d5`) is a distinct registered dojo, not an alias; do not assume its URL or student records transfer to the new dojo.
- Do not update the old testing dojo while preparing the new registration. The deployment job must stay gated until the new dojo's full `DOJO_REF`, `DOJO_DEPLOY_ENABLED=true`, and a fresh `UPDATE_CODE` secret are configured.
- Keep the five working Fundamentals challenges and their protected verification logic intact.
- Keep the optional Linux & CLI introduction (`linux-cli-intro`) ungraded; do not reintroduce removed sample or pilot modules.
- Never put dojo update codes, private SSH keys, API tokens, actual passwords, student records, or reusable static pwn.college flags in source control.

## How to author a new challenge

**Always use the generator rather than copying challenge folders by hand:**

~~~bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/new_challenge.py --module fundamentals --id example-task --name "Example Task"
~~~

For a new module, also provide `--new-module-name "Display Name"`. The generator registers new challenges in `module.yml` and new modules in `dojo.yml`.

The generator automatically creates:

- Executable `/challenge/.init` creates a disposable, writable `/nyitsec-ctf` workspace and opens new interactive terminals there.
- `/challenge/.workspace.py` copies only allowed regular lab files and directories into `/nyitsec-ctf`. It refuses to overwrite an existing destination.
- `/challenge/.ctfignore` provides extra exclusions. Mandatory exclusions protect `.init`, `.workspace.py`, `.ctfignore`, `verify`, `bin/`, and internal README/DESCRIPTION files.
- Executable `/challenge/bin/nyitsec-answer` delegates to `/challenge/verify` without copying the protected verifier.
- Executable `/challenge/verify` is a **fail-closed** Python verifier; replace `is_correct()` before publication.
- Student `DESCRIPTION.md` in challenge folders and officer notes at `docs/officer-solutions/<module>/<challenge>.md` (never deployed).

**Do not alter students' persistent `~/.bashrc`.** The challenge's temporary container-local startup hook uses `/etc/bashrc`. Only interactive shells starting from the default home directory should auto-cd.

## Security and pedagogy

- `/flag` belongs to pwn.college, is student-specific, and is only revealed after the actual solve condition.
- Keep the answer wrapper non-privileged; the protected verifier alone may read `/flag`.
- Use synthetic data and authorized lab targets only. Make exercise goals clear, keep difficulty appropriate for beginners, and teach reasoning instead of giving away flags.
- Students create and edit files inside the writable `/nyitsec-ctf` workspace: `nano script.sh`, save with Ctrl+O and Enter, exit with Ctrl+X, then `bash script.sh`. Challenge input copies can be read by relative filename. Protected originals remain in `/challenge`; do not instruct students to edit them.
- Warn students `/nyitsec-ctf` is temporary; copy important scripts or notes outside it into `~/` before replacing the challenge container. Never automatically clean persistent home data.
- Avoid shell commands and startup behavior that break legitimate student navigation; the auto-cd pattern is a default convenience, not a forced directory lock.
- When a challenge deliberately teaches directory navigation or requires a different solve workflow, document the exception and discuss changing the template/validator rather than silently omitting required files.

## Before creating a PR

~~~bash
python3 scripts/validate_dojo.py
python3 -m unittest discover -s tests -v
~~~

Check that `dojo.yml` and every relevant `module.yml` parse, `.init`, `verify`, and the command wrapper are executable (`100755`), `.workspace.py` and `.ctfignore` exist, standard startup/copy files match the shared template, no scaffold TODOs remain, officer notes exist outside challenge folders, no challenge-local `README.md` exists, and documentation says `nyitsec-answer` and `/nyitsec-ctf`. Preserve the working verifiers and their student-specific `/flag` behavior.

Changes go to a feature branch and pull request, not directly to `main`. After merge, GitHub Actions validates sources; it triggers the dojo updater only when the new dojo's deployment variables have been configured. Test the new dojo's student experience in a fresh workspace before sharing the official link.
