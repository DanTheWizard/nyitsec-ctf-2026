# ITS review — The Broken Login (fictional SQL injection forum)

**Scope:** NYITSec Level 3 CTF challenge `level-3/broken-login/`, hosted inside an isolated, disposable pwn.college challenge container.

This document provides transparent source-level context for NYITSec officers and institutional information security reviewers. **It is not a claim of ITS approval.**

## What is intentionally vulnerable

All vulnerabilities are deliberate teaching devices and must **never** be reused in real applications. The exact, reviewable implementation is [`level-3/broken-login/.forum-app.py`](../../../level-3/broken-login/.forum-app.py).

| Operation | Deliberate flaw | Boundaries |
| --- | --- | --- |
| Signup queue | A raw email string is concatenated into an `INSERT` executed with `sqlite3.executescript`, permitting stacked statements such as `DROP TABLE signup_queue` | Synthetic SQLite database only |
| Login | Username and password are concatenated into a `SELECT`, enabling password-field Boolean SQL injection and administrator authentication bypass | Fictional accounts only |
| Search | User-controlled search text is concatenated into a `SELECT` of two columns, permitting UNION-based recovery of the fictional `users` table | The seeded demonstration database only |

The application **intentionally** uses these unsafe SQL operations. For actual production code the correct solution would be parameterized SQL statements (never `executescript` with user input), salted and password-hashed credentials, least-privilege database accounts, input validation, server-side authorization and security monitoring.

## Runtime boundary and actual effects

- Local test hostname: `nyitsecwebsite.test`, explicitly mapped to **127.0.0.1** in the **ephemeral container's** `/etc/hosts` file.
- Local service: Python `ThreadingHTTPServer` bound to **127.0.0.1:80**, with no network requests to external hosts and no email sending.
- Data: a newly seeded synthetic SQLite database at `/run/nyitsec-forum/forum.sqlite3`, created for the specific challenge container; five fake accounts, five fake waitlist emails, twelve fictional forum posts.
- Process privilege: startup is performed by the challenge initializer; the HTTP server runs as **`nobody`** (not root) and the database files are owned by that unprivileged account. Students are the separate `hacker` user. The server source is protected with file mode `0600`, and the DB directory is `0700`.
- The word **Nuke** is a fictional storyline: the button requires administrator authentication and a second confirmation. Only after the waiting-list table has been dropped does it execute `DELETE FROM posts` and update one status field in that local DB. It displays an invented password for the existing pwn.college answer checker.
- No system processes are killed, no other application data is removed, and no actual student accounts or NYIT services are contacted. The player can reset the container to restore the seeded data.
- Student-visible directory `/nyitsec-ctf`: **no app source files are copied**. The server and startup remain under `/challenge` and cannot be read by the normal user.
- The standard protected `/challenge/verify` checks the case-sensitive synthetic Nuke password hash and reads the per-student platform `/flag` only after a correct answer.

## Review and maintenance

The server, SQLite initialization data, deliberate injection functions, HTML views, admin authorization checks, and simulated nuke logic are all committed to GitHub. The lab's `README.md` documents its intended and alternate solution paths and the reset procedure.

`tests/test_broken_login.py` exercises the real local HTTP server on a random port, confirms SQL injection can drop the local queue, checks the admin password-field bypass, tests the optional search-based credential recovery, ensures nonadmins cannot nuke, verifies the confirmation step, and asserts that the nuke affects only its temporary SQLite database. Tests also check the proper host mapping startup commands and workspace exclusions.

No real personal information, private organizational credentials, static platform flags, or external network targets are included. **Retain this review with the exercise and obtain whatever actual ITS authorization the institution requires before using it in an event.**
