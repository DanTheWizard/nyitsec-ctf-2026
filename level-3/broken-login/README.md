# The Broken Login — NYITSec officer notes

**Module:** `level-3` | **Challenge ID:** `broken-login` | **Difficulty:** Intermediate

## What students should experience

A fictional NYITSec Underground forum is available at **http://nyitsecwebsite.test:8890/** through Firefox inside the challenge Desktop. The intentionally misleading badge says **SUPER SECURE™**. The forum includes 12 seeded discussions, five fake waiting-list emails, five test users, an ordinary login and a search screen.

The mission is to recover the **Nuke authorization password**, then submit it with `nyitsec-answer`. This is an **authorized CTF demonstration**; the simulated nuke deletes only its own fictional posts in an isolated SQLite database. It never shuts down a server, kills processes, deletes external files, or accesses real NYIT systems.

## Runtime setup

- The pwn.college `.init` includes the standard `/nyitsec-ctf` staging and an exact extra suffix invoking `/challenge/.forum-start.sh`.
- The startup script appends `127.0.0.1 nyitsecwebsite.test` to the **container-local** `/etc/hosts` if absent, then starts `/challenge/.forum-app.py` and health-checks HTTP plus hostname resolution.
- The server binds only to **127.0.0.1:8890**. It uses Python's standard-library `ThreadingHTTPServer` and an SQLite database under **`/run/nyitsec-forum/forum.sqlite3`**.
- Startup makes `.forum-app.py` root-only (`0600`), creates the runtime SQLite database, assigns the database and directory to the unprivileged **`nobody`** account (`0600`/ `0700`), and drops server privileges to that account.
- `.ctfignore` excludes `.forum-app.py` and `.forum-start.sh` from the student workspace. **`/nyitsec-ctf` is empty** for this browser-based exercise. The protected `verify` and `bin/nyitsec-answer` follow the standard NYITSec scaffold.
- Neither server nor students require any downloaded packages. Only localhost traffic is used; there are no network calls to outside systems, email sends, or request logs.

## Intended SQL injection solution

1. Visit the **Join waitlist** page. It uses a deliberately insecure `sqlite3.executescript` construction, allowing multiple SQL statements via the email field. An example training-only input that removes the waiting-list table is:
   ```sql
   a@example.test', '2026-11-11'); DROP TABLE signup_queue; --
   ```
   This changes **only the private synthetic SQLite database**.
2. Visit **Log in**. Enter `admin` as the username, then use a password-field SQL injection such as:
   ```text
   ' OR '1'='1' --
   ```
   The intentionally concatenated SQL may treat the attacker-supplied condition as true and return the seeded administrator row.
3. As admin, click the **Nuke Forum** button at the top right. Read the simulated impact and press the **confirmation** button.
4. The nuke action checks that the **signup_queue table no longer exists**, checks that the user is admin, then deletes fictional `posts` and marks `settings.status` as `nuked`. It displays the challenge answer: `OrbitingToaster#73`.
5. Enter `OrbitingToaster#73` with `nyitsec-answer` to receive the student's own pwn.college `/flag`.

The order of dropping the queue and admin authentication is not enforced. If the queue still exists, the Nuke action safely refuses. A challenge reset restores the entire synthetic database.

## Alternative routes (allowed)

- The forum's Search screen contains a separate intentionally vulnerable string-constructed query. A test-only UNION injection can expose the fictional `users` table's two text columns and reveal the seeded admin password:
  ```text
  x%' UNION SELECT username, password FROM users --
  ```
  Log in using the genuine fictional admin password and finish the nuke flow.
- The waitlist's stacked-statement flaw can also modify test account fields. Any route that reaches admin through the deliberately vulnerable local app is valid.
- The answer checker accepts only the final Nuke password. It does not require students to enter a particular injection payload or complete every optional technique.

## Security scope and ITS review

See [`docs/its-review/broken-login/README.md`](../../../docs/its-review/broken-login/README.md) for the deliberately insecure SQL queries, service isolation, reset boundaries, and data inventory. Source code is committed to GitHub for officer/ITS inspection. This documentation **does not constitute ITS authorization** and must not be deployed beyond the isolated training VM.

## Live smoke-test checklist

1. Open **Desktop → Firefox → http://nyitsecwebsite.test:8890/**. Verify the URL resolves locally, the styled forum loads and the SUPER SECURE badge appears.
2. Browse posts and search. Verify no outside URLs or real user information appear.
3. Verify the Nuke URL is unavailable before admin login and ordinary wrong credentials do not authenticate.
4. Submit a harmless normal signup, then the synthetic stacked-statement input to drop the queue. Confirm waitlist status becomes unavailable.
5. Log in as admin using password SQL injection. Confirm the top-right Nuke button appears.
6. Confirm Nuke requires a second click, the queue must be gone, the fictional posts disappear and the displayed password works with `nyitsec-answer`.
7. Reset Challenge. Verify the fictional accounts, queue and posts are restored.
8. Test alternate UNION-based credential discovery and genuine admin login.
9. Verify `cat /challenge/.forum-app.py` fails for the normal `hacker` user, and `/run/nyitsec-forum/` is not readable by `hacker`.
