# Weak Password Audit — Officer Notes

**Module:** `fundamentals` | **Challenge ID:** `password-audit`

## Defensive learning goal

This is a **synthetic, authorized, offline password-strength audit**. The fictional development team provided a test credential hash and the synthetic candidate list intentionally contains a weak matching password. The student experiences a very small, controlled version of **offline dictionary guessing** to understand why predictable passwords and fast, unsalted password hashes are unsafe.

There are **no real usernames, accounts, authentication endpoints, stolen credentials, or external targets**.

The student should use AI to understand or help construct a Bash loop that:

1. Reads `sha256=` from `audit_record.txt`.
2. Reads `common_passwords.txt` one candidate per line (using `while IFS= read -r`).
3. Hashes each candidate *without a trailing newline* using `printf '%s' "$candidate" | sha256sum`.
4. Compares the result to the target digest and prints the first match.
5. Exits without attempting to authenticate anywhere.

The result is entered via `nyitsec-answer`, which delegates to the privileged `verify` script. The verifier reads pwn.college's unique `/flag` only for the correct synthetic test password.

## Important security concepts

SHA-256 here is intentionally **unsalted and fast** to make the exercise accessible for beginner Bash scripting. It is **not appropriate for password storage**. The teaching discussion should cover unique salts, slow password hashing (such as Argon2id), strong unique passwords, and MFA as layered defenses.

No real password or pwn.college flag is stored in this challenge. The fictional matching candidate appears in the synthetic wordlist by design.

## Standard NYITSec conveniences

- Executable `.init` configures interactive Bash to start in `/challenge`.
- Executable `bin/nyitsec-answer` appears on the challenge PATH.
- Executable `verify` compares the supplied password's exact bytes and reveals `/flag` on a match.
- Student instructions are in `DESCRIPTION.md`.

## Smoke test

1. Launch a fresh workspace. Verify `pwd` shows `/challenge`.
2. Read `audit_record.txt` and `common_passwords.txt`.
3. Run a student-created local-only Bash loop and confirm it finds exactly one match.
4. Verify the matching answer succeeds with `nyitsec-answer`; a wrong guess or a case-changed guess must fail.
5. Submit the resulting pwn.college flag and confirm the solve is recorded.
6. Discuss mitigations without implying that any real incident occurred.

The offline test suite checks the local wordlist, SHA-256 data integrity, Bash demonstration logic, and answer verifier without touching `/flag`.
