# NYITSec CTF 2026

Source code for the NYITSec pwn.college dojo. The new dojo URL will be published after registering the `nyitsec-ctf-2026` dojo. The previous testing dojo has its own reference and is not renamed by changing this repository.

## Training modules

- **Linux & CLI Quick Start (Optional):** Three short, ungraded guides to terminal commands, reading files, and responsible AI assistance.
- **Beginner:** Five beginner challenges covering SSH logs, Base64 decoding, and a synthetic password-strength audit.
- **Easy:** File-format investigation, concealed evidence, image steganography, a fictional localhost website, and a randomized archive-search challenge.
- **Intermediate:** The Forgotten Commit (Git history recovery), Packet Detective (HTTP capture analysis), DNS Treasure Hunt, The Suspicious Script, and The Broken Login, progressing from local repository investigation to networking, Python analysis, and a fictional SQL injection forum.

The event's custom leaderboard is planned to report overall points and completed challenges alongside separate Beginner, Easy, and Intermediate rankings. AI tools are permitted and encouraged for learning and problem-solving; students are not expected to finish every challenge during the session. The dojo also introduces [SENSAI](https://pwn.college/sensai), pwn.college's optional, challenge-aware AI assistant, accessed through the top **Help** navigation while a challenge is running. These exercises introduce topics for future NYITSec events.

Students work in a writable, temporary `/nyitsec-ctf` directory. Each challenge provides a `nyitsec-answer` command to check their answer and reveal their own pwn.college flag. The protected verifier stays under `/challenge`.

Student-facing instructions are in each challenge's `DESCRIPTION.md`; officer-only solutions and smoke tests are kept outside deployed challenge directories under `docs/officer-solutions/<module>/<challenge>.md`. Technical ITS reviews stay in `docs/its-review/`.

## Create another NYITSec challenge

Install the small development dependency and use the generator:

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/new_challenge.py --module fundamentals --id new-challenge --name "New Challenge"
```

For a new module, add `--new-module-name "Module Name"`. The generator registers the new challenge and supplies the standard `.init`, `.workspace.py`, `.ctfignore`, `verify`, and `bin/nyitsec-answer` files. Implement the generated fail-closed verifier and replace the student instructions before submitting.

See [CONTRIBUTING.md](./CONTRIBUTING.md) for officer instructions and [AGENTS.md](./AGENTS.md) for AI coding assistants.

## Validate and deploy

```bash
python3 scripts/validate_dojo.py
python3 -m unittest discover -s tests -v
```

Pull requests automatically run these checks. Merging into `main` triggers validation. Deployment is intentionally disabled until the new dojo is registered and its update settings are configured.

The dojo's base YAML ID is `nyitsec-ctf-2026`. When the new dojo is created on pwn.college, it will receive a registered reference ID, which may contain a suffix. The prior testing dojo (`example~36e653d5`) remains separate; its URL and records are not automatically migrated.

After creating the new dojo and testing its challenges, configure the GitHub Actions repository variables `DOJO_REF` (the **full** new dojo reference ID) and `DOJO_DEPLOY_ENABLED` (`true`), and replace the repository secret `UPDATE_CODE` with the **new dojo's** update code. The workflow can then deploy on a push to `main` or via **Run workflow**. Until those variables are configured, pushes only validate; they do not update either dojo.

Keep `type: hidden` until the club intentionally makes the dojo publicly listed. Hidden does not mean password protected; only share access links with the intended participants. **Never commit or share the update code, private update URL, or student flags.**
