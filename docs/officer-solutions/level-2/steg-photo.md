# Officer Notes: The Photograph's Secret

**Module:** `level-2` | **ID:** `steg-photo` | **Difficulty:** Easy

## Design
`evidence.jpg` is a valid JPEG image containing a **real embedded file created with the genuine `steghide` program** (not an appended plaintext or EXIF comment). The hidden file contains a fictional NYITSec case response code. `case-note.txt` supplies the steghide passphrase, so students practice extraction rather than password guessing.

This is an authorized, synthetic digital-forensics lesson. The answer checker stores a digest of the response code and reveals only the student's pwn.college `/flag` after a correct solution.

## Tool availability
The default pwn.college workspace package list does not explicitly include steghide. To make this lab self-contained, the challenge includes `bin/steghide`, a nonprivileged shell wrapper that extracts an offline tool bundle into a freshly created temporary directory, sets the necessary shared library search path, invokes steghide, and then removes the temporary tool files.

- The bundled tool archive lives at `/challenge/.steghide-runtime.tar.gz` and is excluded from the student workspace via `.ctfignore`.
- `/challenge/bin/steghide` is a shell wrapper; it launches the extracted binary as the student, not as root. No bundled executable is setuid.
- The bundle was produced from Ubuntu packages on GitHub Actions. Preserve package provenance and licensing notes whenever rebuilding it.
- Do not use `apt-get` in the challenge's 30-second `.init` window, and do not change the shared NYITSec workspace initializer.
- If bundled libraries prove incompatible with the pwn.college base image, prefer a published challenge-specific image that includes steghide rather than a network installation at startup.

## Live smoke tests
1. In `/nyitsec-ctf`, confirm `evidence.jpg` and `case-note.txt` are writable student copies.
2. Run `steghide --version` and `steghide info evidence.jpg`. Confirm the tool runs without dependency errors.
3. Read the passphrase from `case-note.txt`, then extract the embedded file with `steghide extract -sf evidence.jpg -p cookie-jar`.
4. Read `hidden-note.txt` and submit its response code with `nyitsec-answer`.
5. Confirm incorrect answers reveal no flag and correct answers reveal the student's unique pwn.college flag.
6. Confirm original Fundamentals challenges remain unchanged.

**Note:** The real steghide extraction is verified in CI against the committed JPEG using the bundled tool before deployment. Also perform this live smoke test after merge.

## Officer QA: verified answer and repeatable solution

**Exact correct answer:** `PHOTO-CRUMB-26`  
**Deliberately incorrect input:** `PHOTO-CRUMB-25`  
**Input policy:** Case-sensitive; leading/trailing whitespace is stripped.

### Reproduce the intended solution

Read the fictional evidence note for the passphrase, then use the supplied offline steghide wrapper:

```bash
cd /nyitsec-ctf
cat case-note.txt
steghide --version
steghide extract -sf evidence.jpg -p cookie-jar -xf hidden-note.txt -f
cat hidden-note.txt
```

The embedded synthetic document says `Response code: PHOTO-CRUMB-26`. A fresh challenge instance is recommended to avoid an existing extracted output file.

### Noninteractive checker test over SSH

The following commands inspect only whether the checker prints its success marker. They do **not** print or store the student's unique pwn.college flag.

```bash
if printf '%s\n' 'PHOTO-CRUMB-25' | nyitsec-answer | grep -Fq 'Correct!'; then
  echo 'FAIL: incorrect input accepted'
else
  echo 'PASS: incorrect input rejected'
fi
if printf '%s\n' 'PHOTO-CRUMB-26' | nyitsec-answer | grep -Fq 'Correct!'; then
  echo 'PASS: known correct input accepted'
else
  echo 'FAIL: known correct input rejected'
fi
```

These are officer-only synthetic answers, not pwn.college flags. Do not add them to student-facing descriptions or record actual flag values in QA reports.
