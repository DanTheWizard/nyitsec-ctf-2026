# Weak Password Audit

**Difficulty:** Beginner+ | **Skill:** Bash loops, password hashes, and defensive testing

## The assignment

The NYITSec security team is reviewing the password policy for a **fictional training account** before a new system is released. The development team has supplied a **synthetic test record** and a small list of predictable candidate passwords.

**Your goal:** Determine whether the example password can be recovered from the provided candidate list. This is an **authorized, offline password-strength audit**, not an attempt to log into an account.

Understanding how a password can be guessed helps defenders identify what needs to be improved.

The files in this lab were created for training. **They are not from a real person, account, organization, or breach.**

## Explore the audit materials

Your terminal should start in `/challenge`. If it does not, use `cd /challenge`.

```bash
ls
cat audit_record.txt
head common_passwords.txt
wc -l common_passwords.txt
```

- `audit_record.txt` contains the fictional account name and a **SHA-256 digest** of its test password.
- `common_passwords.txt` contains a small, **synthetic** list of candidates. One matches the digest.
- The plaintext password is **not** stored in the audit record. You must test candidates against the digest.

## Use AI to help you write a Bash script

You can write the script yourself, or ask an AI assistant to help you understand each part. Try a prompt like this:

> I'm learning Bash as part of an authorized, offline cybersecurity training exercise. I have a local file named `common_passwords.txt` with one candidate per line and a local `audit_record.txt` containing a line starting with `sha256=`. Help me write a Bash script that reads every candidate, computes its SHA-256 digest using `printf '%s'` and `sha256sum`, compares it with the recorded digest, prints the matching candidate, and stops. Explain each command and how I can safely test it. Do not use any network requests or login attempts.

Useful building blocks include:

```bash
grep '^sha256=' audit_record.txt
printf '%s' 'example123' | sha256sum
```

Your script can be saved as `audit.sh` in your working directory. You may run it with `bash audit.sh`, so changing executable permissions is optional.

**Important:** `printf '%s'` avoids adding a newline to a candidate. Hashes depend on the exact input bytes, so using `echo` may give a different result.

If a script does not work, ask the AI to explain the error or suggest one correction at a time rather than simply requesting the answer.

## Submit your audit result

Once you identify the matching **synthetic password**, run:

```bash
nyitsec-answer
```

Enter the matched password exactly, including capitalization and punctuation. A correct result reveals your **unique pwn.college flag**.

## What does this teach a defender?

Consider these questions after completing the audit:

- Why was the matching password easy to recover from a small list?
- What would happen if an attacker could try far more guesses against a real, leaked password hash?
- Why should real applications use **unique salts** and a **dedicated, slow password-hashing algorithm such as Argon2id**, rather than plain SHA-256?

**Scope:** This exercise uses local, synthetic files only. Do not test actual accounts, websites, university systems, or anyone else's passwords.
