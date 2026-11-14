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

## Officer QA: verified answer and repeatable solution

**Exact correct answer (in prompt order):** `Super Cool`  
**Deliberately incorrect test input:** `Super Cool!`  
**Input policy:** The checker ignores surrounding whitespace and case, but the two-word content must match.

### Reproduce the intended solution

Decode the outer forwarded message, then its second line:

```bash
cd /nyitsec-ctf
base64 -d message.b64
base64 -d message.b64 | sed -n '2p' | base64 -d
```

The inner reply contains the Base64 substring `TXkgbWVzc2FnZTogU3VwZXIgQ29vbA==`. Decode that substring:

```bash
printf '%s' 'TXkgbWVzc2FnZTogU3VwZXIgQ29vbA==' | base64 -d
```

It reads `My message: Super Cool`; submit only `Super Cool`.

### Noninteractive checker test over SSH

Run these commands **inside the active challenge container** (the local Codex/SSH session can invoke them remotely). They check for the fixed `Correct!` success marker without printing or recording the student-specific pwn.college flag.

```bash
if printf '%s\n' 'Super Cool!' | nyitsec-answer | grep -Fq 'Correct!'; then
  echo 'FAIL: wrong input was accepted'
else
  echo 'PASS: wrong input rejected'
fi
if printf '%s\n' 'Super Cool' | nyitsec-answer | grep -Fq 'Correct!'; then
  echo 'PASS: known correct input accepted'
else
  echo 'FAIL: known correct input rejected'
fi
```

The literal answer above is synthetic challenge data stored **only in private officer documentation**, never in student-facing `DESCRIPTION.md`, `/challenge/README.md`, or the writable workspace. Do not save actual platform flags in QA reports.
