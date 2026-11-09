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

**Where can you save your own work?** The `/challenge` directory is owned by `root`, so you can read the provided files but cannot create or edit files there. Your own home directory (`/home/hacker`, also written as `~`) is writable. Save your scripts there instead. **Do not use `sudo` or change permissions on `/challenge`.**

## Use AI to help you write a Bash script

You can write the script yourself, or ask an AI assistant to help you understand each part. Try a prompt like this:

> I'm new to Linux and Bash, and I'm completing an authorized, offline password-strength audit using **synthetic files only**. The supplied files are `/challenge/common_passwords.txt` (one candidate per line) and `/challenge/audit_record.txt` (with a line starting `sha256=`). `/challenge` is read-only to me, but my home directory is writable. Please teach me **step by step how to create a Bash script using `nano ~/audit.sh`, save it, exit nano, and run it with `bash ~/audit.sh`**. Help me write a `while IFS= read -r` loop that checks every candidate's SHA-256 digest using `printf '%s'` and `sha256sum`, compares the result with the local recorded digest, prints the matching candidate, and stops. Use full `/challenge/...` file paths so the script works from any directory. Explain the commands instead of just giving me the final answer. Do not make network requests or attempt any logins.

Useful building blocks include:

```bash
grep '^sha256=' audit_record.txt
printf '%s' 'example123' | sha256sum
```

### Create, save, and run your script

Even if your terminal prompt shows `/challenge`, **save your script in your home directory**, not inside `/challenge`.

1. Run `nano ~/audit.sh` to open a new, writable script file in the terminal text editor.
2. Type or paste your Bash script into the editor. If you need help, ask your AI assistant to explain how `nano` works before continuing.
3. Press **Ctrl+O**, then **Enter**, to save the file. Press **Ctrl+X** to exit.
4. Run the saved script with `bash ~/audit.sh`. You do not need `chmod +x` when using `bash` to run it.
5. If your script prints an error, open it again with `nano ~/audit.sh` and investigate the error message.

```bash
nano ~/audit.sh
# After saving and exiting nano:
bash ~/audit.sh
```

**Important:** In your Bash script, read the source files from `/challenge/common_passwords.txt` and `/challenge/audit_record.txt`, because your script lives in a different directory. You do **not** need to copy or modify the provided files.

If you see **`Error writing audit.sh: Permission denied`**, you likely tried to save it in `/challenge`. Exit the editor without replacing protected files, and use `nano ~/audit.sh` instead.

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
