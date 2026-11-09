# PILOT: Weak Password Audit

**Experimental workspace test.** The same fictional training account and 77 synthetic password candidates are used as in the existing Weak Password Audit.

Your terminal should begin in **`/nyitsec-ctf`**. Unlike `/challenge`, this workspace is **writable** by the student, so you can create a Bash script here with a relative filename.

```bash
pwd
ls -la
cat audit_record.txt
head common_passwords.txt
nano audit.sh
```

In `nano`, press **Ctrl+O**, then **Enter** to save, and **Ctrl+X** to exit. Run the script with:

```bash
bash audit.sh
```

**Defensive task:** Conduct an authorized offline audit. Read each candidate from `common_passwords.txt` with a Bash loop, calculate its SHA-256 digest using `printf '%s' "$candidate" | sha256sum`, compare it with the `sha256=` value in `audit_record.txt`, and stop at the first match. There are no real accounts or network targets.

You can ask AI:

> I'm new to Bash. In my authorized, synthetic training lab, both `common_passwords.txt` and `audit_record.txt` are in the current writable directory, `/nyitsec-ctf`. Explain how to create and save `audit.sh` with nano, write a `while IFS= read -r` loop over the candidates, hash each one without a newline using `printf '%s'` and `sha256sum`, compare it with the digest in the local record, and run `bash audit.sh`. Explain each command. Do not attempt logins or connect to the network.

Once you find the matching **case-sensitive** synthetic password, run `nyitsec-answer` to receive your unique pwn.college flag.

**Temporary workspace notice:** `/nyitsec-ctf` is disposable. Your script will disappear when the challenge container is restarted or replaced. Copy it to `~/audit.sh` before switching if you want to keep it.

**What to learn:** Predictable passwords and fast unsalted SHA-256 digests allow inexpensive offline guessing. Real password storage should use unique salts and dedicated password hashing such as Argon2id.
