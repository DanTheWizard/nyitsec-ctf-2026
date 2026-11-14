# The Suspicious Script — Officer notes

**Module:** `level-3` | **ID:** `suspicious-script` | **Difficulty:** Intermediate

## Learning objective

Students should inspect a seemingly suspicious Python script statically, determine the source of downloaded data, understand an encoded URL, and reverse a simple **XOR + zlib** transformation to read another Python source file **without executing it**.

The student-visible `audit_sync.py` has obfuscated variable names and a reversed Base64-encoded HTTP URL. Its `_r()` function constructs the URL. Its `_q(blob)` function removes the binary header, XORs bytes with a short repeating key, and decompresses them. `_w()` downloads the byte blob from the isolated localhost HTTP service, writes it to a file under `/tmp`, and **executes the recovered source with `exec(compile(...))` inside the same Python process**. The recovered Python source contains:

```python
analysis_note = "Your flag answer: IKnowPythonDeobfuscation#404"
```

If the student runs the original script despite the warning, the decoded source simply prints:

```text
You had one job... Not to execute the script lol
```

That execution path is harmless, but the lesson is not to rely on executing unknown programs to assess their behavior.

## Recommended officer solution

1. Inspect `audit_sync.py` without running it, particularly `_r()`, `_q()`, and the `if __name__ == "__main__"` guard.
2. Decode the reversed Base64 string to discover the loopback HTTP endpoint.
3. Download the binary blob using a separate, minimal local-only tool, such as `urllib.request.urlopen` or `curl`, saving it under `/nyitsec-ctf` or `/tmp`.
4. After reviewing the source and confirming `_q()` is pure and has no execution effects, use its implementation (or manually reproduce the XOR and zlib logic) to decode the binary. **Do not call `_w()` or the final `exec` operation.**
5. Read the resulting Python source as text. Recover the answer string from `analysis_note` and choose the description of **download → decode → in-process execution**.
6. Run `nyitsec-answer` and provide **option B** plus `IKnowPythonDeobfuscation#404`. Test an incorrect selection with correct string, correct selection with incorrect string, and both incorrect. All must produce the **same generic error**.

## Institutional security/ITS source review

The **exact decoded payload** and a full explanation of the program's
download, deobfuscation, temporary-file, and execution behavior are committed
under [`docs/its-review/suspicious-script/`](../../its-review/suspicious-script/README.md).
These officer/ITS files are deliberately outside `level-3/suspicious-script/`,
so pwn.college does not stage them into `/challenge` or `/nyitsec-ctf`.
The automated tests require the GitHub review source to match the embedded
binary **byte for byte**.

This documentation is provided to facilitate an ITS review, not to assert
that ITS has approved the activity.

## Service and safety

- The server binds only to HTTP `127.0.0.1:8876` and serves a single binary path. No external requests, uploads, remote commands, or logging.
- The server reads encrypted binary bytes *before* dropping privileges to the unprivileged `hacker` account. The source `.payload-service.py`, start script `.payload-start.sh`, and encrypted `.payload.bin` are made root-only with `chmod 600` and excluded from `/nyitsec-ctf` using `.ctfignore`.
- `audit_sync.py` is the only file copied into the writable student workspace. The server and answer checker remain protected under `/challenge`.
- The deliberate execution path is only a print statement and writes the downloaded bytes into `/tmp/payload.bin`. No network targets outside the container exist. This is a safe synthetic example, **not an actual malicious payload**.
- Both inputs are required simultaneously by the privileged verifier. It checks separate SHA-256 digests and only reveals the platform-specific `/flag` after both match.

## Live smoke tests

1. Launch the challenge; confirm `pwd` reports `/nyitsec-ctf` and `ls` shows only `audit_sync.py`.
2. Confirm the local endpoint responds with a binary file, and the hidden server source remains unreadable to `hacker`.
3. Use static analysis to decode the blob without invoking `exec`; recover the `analysis_note` variable and its exact case-sensitive answer.
4. (Officer-only) Run `python audit_sync.py` in the disposable challenge container, confirm the **joke message**, confirm `/tmp/payload.bin` is created, and check it does not reveal the answer as output.
5. Check wrong option / correct phrase, correct option / wrong phrase, and both wrong all produce the same error. Only the correct pair unlocks the unique `/flag`.
6. Confirm other modules and the standard NYITSec workspace still work.

## Officer QA: verified answer and repeatable solution

**Exact correct inputs (prompt order):** `B` → `IKnowPythonDeobfuscation#404`  
**Deliberately incorrect test inputs:** `A` → `IKnowPythonDeobfuscation#404`  
**Input policy:** Part 1 selection is normalized to uppercase; Part 2 phrase is case-sensitive with trimming. Both are required simultaneously; wrong combinations return the same generic error.

### Reproduce the intended solution

Inspect the synthetic client `audit_sync.py` statically. `_r()` recovers the localhost payload URL; `_q(blob)` applies XOR and zlib to recover Python source, while `_w()` would execute it. **Do not execute the unknown-looking client for QA.** The private review source at `docs/its-review/suspicious-script/recovered_payload.py` contains the recovered string `IKnowPythonDeobfuscation#404`.

The correct behavior option is **B**, describing download → decode → execute inside the current Python process. For answer-checker-only QA, use the documented two inputs; no payload execution or reverse engineering is necessary.

### Noninteractive checker test over SSH

Run this self-contained Python probe **inside a fresh SSH-connected challenge instance**. It executes the existing `nyitsec-answer` command twice, one known-wrong and one known-correct submission. It checks exit status, the exact rejection message, and the presence of a correctly shaped platform flag, but **never prints or saves the flag**. `BLOCKED` means the verifier or environment could not be validated, not that the challenge was solved.

```python
import re
import subprocess
import sys

# Inputs are fictional training data from this private officer guide.
cases = [
    ("incorrect", ["A","IKnowPythonDeobfuscation#404"], False),
    ("correct", ["B","IKnowPythonDeobfuscation#404"], True),
]
rejection_text = "One or more answers are incorrect. Review the evidence and try again."
status = 0

for label, answers, should_accept in cases:
    try:
        result = subprocess.run(
            ["nyitsec-answer"],
            input="\n".join(answers) + "\n",
            text=True,
            capture_output=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        print(f"BLOCKED: {label} probe could not execute or timed out")
        status = max(status, 2)
        continue

    if result.returncode != 0:
        print(f"BLOCKED: {label} verifier exited with status {result.returncode}")
        status = max(status, 2)
        continue

    lines = result.stdout.splitlines()
    success_lines = [i for i, line in enumerate(lines) if line.startswith("Correct!")]

    if should_accept:
        if not success_lines:
            if rejection_text in result.stdout:
                print("FAIL: documented correct answer was rejected")
                status = max(status, 1)
            else:
                print("BLOCKED: correct probe had no recognized verifier response")
                status = max(status, 2)
        else:
            position = success_lines[-1] + 1
            flag = lines[position].strip() if position < len(lines) else ""
            if re.fullmatch(r"pwn\.college\{[^{}\s]+\}", flag):
                print("PASS: correct answer accepted and platform flag produced (redacted)")
            else:
                print("BLOCKED: success marker present but expected flag missing or malformed")
                status = max(status, 2)
    elif success_lines:
        print("FAIL: deliberately incorrect answer was accepted")
        status = max(status, 1)
    elif rejection_text in result.stdout:
        print("PASS: deliberately incorrect answer rejected")
    else:
        print("BLOCKED: incorrect probe had no recognized rejection response")
        status = max(status, 2)

# 0: all checks passed; 1: verification failed; 2: environment/transport blocked.
sys.exit(status)
```

Keep this literal solution in the **private officer guide only**, never in the student-facing challenge directory or logs. Do not record platform flag values.
