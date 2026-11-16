# NYITSec CTF 2026

Source code for the **[NYITSec CTF 2026 dojo](https://pwn.college/nyitsec-ctf-2026~36e653d5/)** on pwn.college. This is the original dojo, renamed from `example~36e653d5` by changing `id` in `dojo.yml`. Its registered suffix, members, and existing solve history remain associated with the same dojo.

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

Pull requests run the repository checks. After changes are reviewed and merged into `main`, GitHub Actions validates the source and updates the **existing** pwn.college dojo at [nyitsec-ctf-2026~36e653d5](https://pwn.college/nyitsec-ctf-2026~36e653d5/) using the repository secret `UPDATE_CODE`. Because this is the original dojo with an updated URL, its existing update code does not need to be replaced solely due to the rename.

The YAML base ID is `nyitsec-ctf-2026`; the `~36e653d5` suffix remains tied to the same registered dojo. If the YAML ID is renamed again, update the dojo reference in `.github/workflows/update.yml` as well.

The dojo remains **hidden** (`type: hidden`) until NYITSec is ready to make it publicly listed. A hidden dojo is not a substitute for access controls, so distribute its link only to intended participants while it is in private testing. Never commit or share the update code, private update URL, or student flags.
