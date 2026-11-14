# pwn.college post-deployment review checklist (officers only)

Use this checklist **after** merging the officer-notes migration and after the `Update NYITSec Dojo` GitHub Actions workflow has succeeded. This file stays in private GitHub under `docs/officer-solutions/` and must never be included in a deployed challenge directory.

## 1. Deployment and access

- [ ] The PR was reviewed and merged into `main`; all CI checks passed.
- [ ] The pwn.college dojo update GitHub Actions workflow succeeded for the actual merge commit (a green PR alone does not prove deployment).
- [ ] Capture the merge SHA, deployment workflow URL, date and reviewer below.
- [ ] As a student, confirm the expected Fundamentals, Level 2, and Level 3 challenge names appear, and the optional Linux & CLI intro remains ungraded.
- [ ] Launch a **new** instance for each check; do not reuse an existing container created before the update.
- [ ] Ensure neither `docs/officer-solutions/` nor `docs/its-review/` is accidentally mounted or published into any challenge.

## 2. For each of the 15 challenges: normal mode

Open a fresh, **non-privileged** challenge instance. Run:

```bash
pwd
id
ls -la /nyitsec-ctf
ls -la /challenge
type -a nyitsec-answer
test ! -e /challenge/README.md && echo "PASS: officer README is absent"
test ! -e /nyitsec-ctf/README.md && echo "PASS: no workspace officer README"
test ! -d /challenge/docs && echo "PASS: no docs tree in challenge"
```

- [ ] Default interactive working directory is `/nyitsec-ctf`; the intended evidence is present and readable.
- [ ] Student can create a scratch file in `/nyitsec-ctf`; no unexpected protected files were copied there.
- [ ] `/challenge/DESCRIPTION.md` remains student-facing, and `nyitsec-answer` is on PATH.
- [ ] No officer solutions or ITS review documents are exposed within `/challenge` or `/nyitsec-ctf`.
- [ ] An incorrect answer does **not** reveal `/flag`; multi-part challenges keep their intended generic error.
- [ ] Following the private officer solution, the correct answer succeeds and reveals only the expected instance-specific platform flag.
- [ ] `nyitsec-answer` works after changing directories.
- [ ] Restarting/replacing the challenge resets its disposable workspace, with no unexpected changes to persistent `~/` files.
- [ ] Challenge startup shows no missing-file, permissions, or runtime errors.

## 3. For each of the 15 challenges: privileged audit

Create a **separate fresh privileged** instance and inspect the **actual runtime filesystem**. Do not assume Linux file permissions conceal files from a root shell. Privileged mode is for auditing, not for obtaining a redeemable flag.

```bash
id
find /challenge /nyitsec-ctf -type f \( -iname 'README.md' -o -iname '*officer*' \) -print
test ! -e /challenge/README.md
test ! -d /challenge/docs
test ! -d /challenge/officer-solutions
test ! -d /nyitsec-ctf/docs
```

- [ ] No moved officer guide is present, including through alternate filenames, backup copies, mounts, or archives.
- [ ] Neither `docs/officer-solutions/` nor `docs/its-review/` is deployed in the container.
- [ ] Necessary verifier and server files remain present, where required; distinguish intended recoverable student evidence from unintended shortcut disclosures.
- [ ] Inspect remaining runtime files for independent static-answer shortcuts (a separate challenge design/security review, not solved solely by moving notes).

## 4. Per-challenge live checks

For **every row**: confirm normal-mode startup, intended solve, wrong-answer behavior, privileged-mode absence of officer notes, and a fresh-instance reset. Read actual answers from `docs/officer-solutions/<module>/<challenge>.md` in private GitHub, not from pwn.college.

| Complete | Challenge | Specific things to verify |
| --- | --- | --- |
| [ ] | `fundamentals/incident-id` | `events.log` exists; inspect logs and submit the intended answer |
| [ ] | `fundamentals/base64-basics` | `message.b64` exists; one-layer decoding and checker work |
| [ ] | `fundamentals/base64-layers` | `message.b64` exists; repeated decoding works |
| [ ] | `fundamentals/base64-more` | `message.b64` exists; required decode process works |
| [ ] | `fundamentals/password-audit` | `audit_record.txt`, `common_passwords.txt`; writable scratch script and hash match |
| [ ] | `level-2/cookie-metadata` | `document.txt` exists; inspect metadata and solve |
| [ ] | `level-2/forgotten-file` | Generated file layout is searchable; repeat on another fresh start |
| [ ] | `level-2/inspect-source` | Fictional localhost website starts; inspect the served page |
| [ ] | `level-2/misnamed-image` | `notice.txt` exists; investigate actual file data |
| [ ] | `level-2/steg-photo` | `evidence.jpg`, `case-note.txt`, and bundled steganography tooling work |
| [ ] | `level-3/broken-login` | Fictional forum resolves to loopback and starts; intended SQL injection and reset work |
| [ ] | `level-3/dns-treasure-hunt` | Local DNS service responds to bundled `dig` without external DNS |
| [ ] | `level-3/forgotten-commit` | Startup succeeds **without** `/challenge/README.md`; bundled Git and recoverable history work |
| [ ] | `level-3/packet-detective` | `traffic.pcap` and `incident-brief.txt`; offline analysis and two-part checker |
| [ ] | `level-3/suspicious-script` | `audit_sync.py` staged; localhost payload endpoint, safe static decode, and two-part checker |

## 5. Sign-off

- [ ] All 15 challenges were reviewed in both normal and privileged modes, with no officer note leaks.
- [ ] All intended student-side solving and wrong-answer tests passed.
- [ ] `docs/its-review/` remains in GitHub and out of runtime challenge containers.
- [ ] Record every failed test as an issue, apply a fix through a new reviewed PR, then repeat the affected live checks.
- [ ] Declare completion only after testing the **updated deployed dojo**, not solely the local Python tests.

**Reviewer:**  
**Review date:**  
**Dojo URL:**  
**Merge SHA:**  
**Update workflow URL:**  
**Failures/retest notes:**  
