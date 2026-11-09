# Author notes: Base64 Basics

**Module:** fundamentals | **ID:** base64-basics

A self-contained simulated message is stored in `message.b64`. The student must decode it **once** and enter the answer code from the plaintext. Do not publish the plaintext answer in the student description.

- `.init`: shared NYITSec startup hook that sets initial interactive shell directory to `/nyitsec-ctf`.
- `bin/nyitsec-answer`: executable alias for `/challenge/verify`.
- `verify`: executable Python `exec-suid` checker; it compares a hash of the entered answer code and reads pwn.college's student-specific `/flag` only when correct.
- `message.b64`: Base64-encoded practice material. No real credentials or secrets.

### Test after deployment

1. Start a new workspace and check `pwd` is `/nyitsec-ctf`.
2. Confirm `base64 -d message.b64` reveals a readable message containing the answer code.
3. Run `nyitsec-answer` and enter a wrong code; it must not reveal the flag.
4. Re-run with the decoded code; confirm it reveals the unique flag and pwn.college accepts it.

The offline CI tests independently decode the artifact and check the verifier for both correct and incorrect inputs.

## Writable workspace standard

The `.init` startup script prepares `/nyitsec-ctf` by running `.workspace.py` and opens interactive terminals there. Challenge input copies are writable by `hacker`; protected files remain in `/challenge`. The blacklist in `.ctfignore` may add exclusions, but protected core names cannot be copied. The workspace is disposable across challenge restarts. Check `pwd`, `ls -la`, `touch scratch.txt`, `nyitsec-answer`, and correct/wrong solution submissions after deployment.
