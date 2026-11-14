# Officer-only answer index and SSH QA procedure

**Repository scope:** The synthetic answers and reproducible solution instructions for all 15 graded challenges are stored in `docs/officer-solutions/<module>/<challenge>.md`. They are intentionally **not** part of the challenge files deployed under pwn.college's `/challenge`.

## How to use these guides

1. In the authenticated ChatGPT browser, start the desired pwn.college challenge in normal mode.
2. From **local** Codex/PowerShell, connect using the configured personal SSH key (do not share or upload that key).
3. Read the matching private officer guide. Its section **Officer QA: verified answer and repeatable solution** provides the known correct input, a wrong input, and a reproducible student solution path. Do **not** derive answers by solving when running answer-checker-only QA.
4. Run the guide's Python snippet via `python3` in the active SSH-connected instance (for example, paste it into `python3 -` and end input with Ctrl+D, or use an SSH heredoc). It checks verifier exit status, the exact error/success response, and the presence of a correctly shaped platform flag without printing or saving the flag. A crash, timeout, SSH transport failure, or incomplete flag retrieval is **BLOCKED**, never PASS.
5. Check workspace/file isolation and restart behavior separately using [the pwn.college checklist](PWNCOLLEGE-REVIEW-CHECKLIST.md). Restart the challenge when moving between tests that alter synthetic app state.
6. For multi-input challenges, provide every line in the specified prompt order. Distinguish a real PASS from a transport error; an SSH or command failure is **BLOCKED**, not PASS.
7. Record only `PASS`, `FAIL`, or `BLOCKED` and relevant non-secret evidence. Do not copy the pwn.college flag into a report.

## Known-answer coverage

| Module | Challenge | Correct input available? |
| --- | --- | --- |
| `fundamentals` | [`incident-id`](fundamentals/incident-id.md) | Yes |
| `fundamentals` | [`base64-basics`](fundamentals/base64-basics.md) | Yes |
| `fundamentals` | [`base64-layers`](fundamentals/base64-layers.md) | Yes |
| `fundamentals` | [`base64-more`](fundamentals/base64-more.md) | Yes |
| `fundamentals` | [`password-audit`](fundamentals/password-audit.md) | Yes |
| `level-2` | [`cookie-metadata`](level-2/cookie-metadata.md) | Yes |
| `level-2` | [`forgotten-file`](level-2/forgotten-file.md) | Yes |
| `level-2` | [`inspect-source`](level-2/inspect-source.md) | Yes |
| `level-2` | [`misnamed-image`](level-2/misnamed-image.md) | Yes |
| `level-2` | [`steg-photo`](level-2/steg-photo.md) | Yes |
| `level-3` | [`broken-login`](level-3/broken-login.md) | Yes |
| `level-3` | [`dns-treasure-hunt`](level-3/dns-treasure-hunt.md) | Yes |
| `level-3` | [`forgotten-commit`](level-3/forgotten-commit.md) | Yes |
| `level-3` | [`packet-detective`](level-3/packet-detective.md) | Yes (two inputs) |
| `level-3` | [`suspicious-script`](level-3/suspicious-script.md) | Yes (two inputs) |

**Dynamic behavior:** `level-2/forgotten-file` randomizes the file containing the clue on every new container instance, not the answer itself. `level-3/forgotten-commit` generates deterministic synthetic Git history, but commit identifiers should be discovered rather than hardcoded.

**Safety boundary:** All challenge answers are synthetic values. They are not passwords for real accounts, real targets, reusable platform flags, or the SSH key used for testing. This documentation remains in the private officer portion of the repository.
