# NYITSec CTF 2026

Source code for the private [NYITSec pwn.college dojo](https://pwn.college/example~36e653d5/).

## Training modules

- **Linux & CLI Quick Start (Optional):** Three short, ungraded guides to terminal commands, reading files, and responsible AI assistance.
- **CTF Fundamentals:** Five beginner challenges covering SSH logs, Base64 decoding, and a synthetic password-strength audit.
- **CTF Level 2 - Easy:** File-format investigation, concealed evidence, image steganography, a fictional localhost website, and a randomized archive-search challenge.
- **CTF Level 3 - Intermediate:** DNS Treasure Hunt: use a real local DNS server, follow record references, and decode an assembled TXT-record message.

Students work in a writable, temporary `/nyitsec-ctf` directory. Each challenge provides a `nyitsec-answer` command to check their answer and reveal their own pwn.college flag. The protected verifier stays under `/challenge`.

Student-facing instructions are in each challenge's `DESCRIPTION.md`; officer notes are in `README.md` in the challenge folder.

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

Pull requests automatically run these checks. Merging into `main` triggers the dojo update workflow.

The dojo's base YAML ID is `example` and its assigned pwn.college reference is `example~36e653d5`. Deployments require the GitHub Actions repository secret `UPDATE_CODE`. **Never commit or share the update code, private update URL, or student flags.**

## Operation Blackout progression-lock pilot (not live until merged)

A temporary, three-stage module in `blackout-pilot/` exercises pwn.college's `progression_locked: true` gating. See [the pilot test plan](./blackout-pilot/PILOT_TEST_PLAN.md). The pilot is unweighted; tournament scoring and completion bonuses are not implemented here.
