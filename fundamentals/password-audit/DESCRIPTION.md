# Weak Password Audit

**Difficulty:** Beginner+ | **Skill:** Bash loops, password hashes, and defensive testing

## The assignment

The NYITSec security team is reviewing the password policy for a **fictional training account** before a new system is released. The development team has supplied a **synthetic test record** and a small list of predictable candidate passwords.

**Your goal:** Determine whether the example password can be recovered from the provided candidate list. This is an **authorized, offline password-strength audit**, not an attempt to log into an account.

Understanding how a password can be guessed helps defenders identify what needs to be improved.

The files in this lab were created for training. **They are not from a real person, account, organization, or breach.**

## Explore the audit materials

Your terminal should start in the writable `/nyitsec-ctf` directory. If it does not, use `cd /nyitsec-ctf`.

```bash
ls
cat audit_record.txt
head common_passwords.txt
wc -l common_passwords.txt
```

- `audit_record.txt` contains the fictional account name and a **SHA-256 digest** of its test password.
- `common_passwords.txt` contains a small, **synthetic** list of candidates. One matches the digest.
- The plaintext password is **not** stored in the audit record. You must test candidates against the digest.

**Your writable workspace:** The two synthetic files were copied to `/nyitsec-ctf`, where you can create `audit.sh` alongside them. The protected originals and answer verifier remain in `/challenge`. **Do not use `sudo` or change permissions on `/challenge`.**

## Use AI to help you write a Bash script

You can write the script yourself, or ask an AI assistant to help you understand each part. Try a prompt like this:

> I'm learning Bash through an authorized offline password-strength audit using **synthetic files only**. My terminal starts in the writable `/nyitsec-ctf` directory, alongside `common_passwords.txt` (one candidate per line) and `audit_record.txt` (which contains a `sha256=` line). Teach me **step by step how to create `audit.sh` using `nano audit.sh`, save it with Ctrl+O and Enter, exit with Ctrl+X, and run `bash audit.sh`**. Help me write a `while IFS= read -r` loop that hashes each candidate using `printf '%s'` and `sha256sum`, compares it with the recorded digest, prints the matching candidate, and stops. Explain each command rather than just giving me the answer. Do not make network requests or attempt any logins.

Useful building blocks include:

```bash
grep '^sha256=' audit_record.txt
printf '%s' 'example123' | sha256sum
```

### Create, save, and run your script

Since the terminal starts in **`/nyitsec-ctf`**, you can save a script directly in the current directory:

1. Run `nano audit.sh` to open the editor.
2. Type or paste your script. Ask AI to explain any parts you do not understand.
3. Press **Ctrl+O**, then **Enter** to save. Press **Ctrl+X** to exit.
4. Run `bash audit.sh`. You do not need `chmod +x` when launching a script through Bash.
5. If something fails, use `nano audit.sh` again to inspect and correct it.

```bash
pwd
nano audit.sh
# After saving and exiting nano:
bash audit.sh
```

The data files are already in the same working directory, so your Bash loop can read `common_passwords.txt` and `audit_record.txt` directly. **Do not edit `/challenge/verify` or use privileged commands.**

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

**Temporary workspace notice:** `/nyitsec-ctf` is part of the current challenge container and is not persistent. Copy any scripts or notes you want to keep to `~/` before restarting or switching challenges.
