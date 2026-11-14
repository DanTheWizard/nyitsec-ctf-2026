# Author notes: Base64 Layers

**Module:** fundamentals | **ID:** base64-layers

This exercise follows Base64 Basics. The text was encoded with Base64 **three times**. The final readable plaintext contains an answer code, but the static code is not a platform flag. pwn.college provides a different `/flag` for each student.

- `.init`, `bin/nyitsec-answer`, and `verify` follow the standard NYITSec challenge template.
- `message.b64` is a deliberately triple-encoded synthetic message; no live secrets are present.
- The verifier checks a one-way digest of the decoded answer code and only then reveals the student's real flag.

### Test after deployment

1. Run `base64 -d message.b64`. Output should still resemble Base64.
2. Decode again; output should still resemble Base64.
3. Decode a third time and confirm the answer code is visible.
4. Check `nyitsec-answer` rejects incorrect codes and accepts the decoded code.
5. Submit the printed flag and confirm a solve is registered.

The offline CI tests verify all three decoding layers and the answer checker.

## Writable workspace standard

The `.init` startup script prepares `/nyitsec-ctf` by running `.workspace.py` and opens interactive terminals there. Challenge input copies are writable by `hacker`; protected files remain in `/challenge`. The blacklist in `.ctfignore` may add exclusions, but protected core names cannot be copied. The workspace is disposable across challenge restarts. Check `pwd`, `ls -la`, `touch scratch.txt`, `nyitsec-answer`, and correct/wrong solution submissions after deployment.
