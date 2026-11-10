# Weak Password Audit

The NYITSec team is checking a **fictional test account** before launch. Its password was hashed with SHA-256, and a small list of possible passwords is available.

**Goal:** Use a Bash script to find which candidate matches the test hash. This is an **authorized, offline exercise**, not a real login attempt.

### Explore the files

Your writable workspace is `/nyitsec-ctf`.

```bash
cat audit_record.txt
head common_passwords.txt
```

The record contains a `sha256=` value. The `common_passwords.txt` file has one candidate per line.

### Create your script

You may write the script yourself or ask AI to explain how. For example:

> Help me learn Bash for a synthetic, offline password audit. Show me how to create `audit.sh` with nano, read candidates one at a time from `common_passwords.txt`, hash each using `printf '%s'` and `sha256sum`, compare with the `sha256=` value in `audit_record.txt`, and stop at a match. Explain the commands rather than giving me the answer. Do not use the network.

```bash
nano audit.sh
# Save: Ctrl+O, Enter. Exit: Ctrl+X.
bash audit.sh
```

**Tip:** `printf '%s'` hashes the password without adding a newline. Passwords are case-sensitive.

When you find the matching password, enter it exactly with `nyitsec-answer` and submit your flag.

**Defensive takeaway:** A predictable password and fast, unsalted SHA-256 hashing make offline guessing easier. Real applications should use unique salts and a password-specific algorithm such as Argon2id.

**Temporary workspace notice:** Scripts in `/nyitsec-ctf` disappear when the challenge restarts. Copy your work to `~/` if you want to keep it.
