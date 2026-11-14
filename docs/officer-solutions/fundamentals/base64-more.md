# Author notes: More Base64?

**Module:** `fundamentals` | **ID:** `base64-more`

This challenge uses **the original Base64-encoded forwarded-message payload provided for the NYITSec activity**, copied into `message.b64` without modification.

Students should decode the outer Base64 message and see a forwarded-message header plus another Base64 payload. Decoding the inner payload produces a reply message with a Base64 segment *inside the sentence*, followed by additional ordinary reply text. Decoding that segment reveals a final two-word message, which is the answer accepted by `nyitsec-answer`.

There are **three total Base64 decoding steps**, but the second and third require isolating an encoded substring from human-readable conversation text. The student-facing instructions intentionally do not reveal the final answer.

### Standard NYITSec challenge mechanics

- `.init` (executable): interactive Bash starts in `/nyitsec-ctf`.
- `bin/nyitsec-answer` (executable): delegates to `/challenge/verify` via the provided challenge PATH.
- `verify` (executable): compares the submitted original message's SHA-256 digest and reveals the student's unique root-protected `/flag` only after a correct match.
- `message.b64`: the fictional forwarded conversation in Base64, not a real secret or flag.

### Smoke test after merge and deployment

1. Open a fresh workspace; `pwd` should show `/nyitsec-ctf`.
2. Run `base64 -d message.b64`, identify the inner Base64 string, and decode it.
3. Find the encoded substring inside the reply, decode it, and confirm it reveals the original two-word message.
4. Enter an incorrect answer into `nyitsec-answer`, which must not reveal the flag.
5. Enter the original two-word message and submit the resulting platform-generated flag.
6. Check that the existing Base64 Basics and Base64 Layers challenges still work.

The offline unit test independently decodes each stage, verifies that the message wrappers remain intact, and tests both accepted and rejected answer submissions without reading `/flag`.

## Writable workspace standard

The `.init` startup script prepares `/nyitsec-ctf` by running `.workspace.py` and opens interactive terminals there. Challenge input copies are writable by `hacker`; protected files remain in `/challenge`. The blacklist in `.ctfignore` may add exclusions, but protected core names cannot be copied. The workspace is disposable across challenge restarts. Check `pwd`, `ls -la`, `touch scratch.txt`, `nyitsec-answer`, and correct/wrong solution submissions after deployment.
