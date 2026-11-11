# NYITSec ITS review: The Suspicious Script

**Purpose:** Source-level review of the Level 3 training challenge, including the exact Python source embedded in its obfuscated binary.

**Scope:** NYITSec's fictional, self-contained pwn.college challenge `level-3/suspicious-script`. This document and the readable payload source are **review-only GitHub files, deliberately located outside all deployed challenge directories**. They are not copied into `/challenge` or the student's writable `/nyitsec-ctf` directory.

**Important:** This information supports ITS/security review. It is not a determination that the exercise has been approved by ITS or meets any particular institutional policy.

## Source files and execution path

| Repository path | Purpose | Visible to students |
| --- | --- | --- |
| `level-3/suspicious-script/audit_sync.py` | The deliberately obscured starter script students examine | **Yes:** copied into `/nyitsec-ctf` |
| `level-3/suspicious-script/.payload-service.py` | Serves only the synthetic binary payload over HTTP | Not copied; mode `0600` under `/challenge` |
| `level-3/suspicious-script/.payload-start.sh` | Configures file permissions, launches service, runs health check | Not copied; mode `0600` under `/challenge` |
| `level-3/suspicious-script/.payload.bin` | XOR-obfuscated, zlib-compressed Python source with `LAB1` header | Not copied; available only through the local HTTP endpoint |
| `docs/its-review/suspicious-script/recovered_payload.py` | **Exact readable source decoded from the binary** | **No:** repository review folder, outside the deployed challenge |
| `level-3/suspicious-script/verify` | Two-part privileged answer checker; reads `/flag` only when both answers match | Not copied; invoked via `nyitsec-answer` |

The student-facing file uses a reversed Base64-encoded URL and misleading short names. `_r()` decodes the URL, `_q()` XOR-decodes and decompresses the bytes **without evaluating them**, and `_w()` performs the download and optional execution. It imports standard-library modules only.

### What the script does if executed

1. Connects to **`http://127.0.0.1:8876/assets/payload.bin`** inside its own challenge container.
2. Reads up to 65,536 bytes; the service responds with the prepared `LAB1` binary.
3. Writes the downloaded data to **`/tmp/payload.bin`** in that container.
4. Removes the four-byte header, XORs the remaining data with the repeating key `43 21 79 2e 59 13 73` (hex), and decompresses it using `zlib`.
5. Calls **`exec(compile(...))`** on that recovered source in the same Python process. The recovered script defines a fixed `analysis_note` string and, when executed, only prints: **`You had one job... Not to execute the script lol`**.

**No external hosts, credential theft, persistence, privilege escalation, shell commands, or additional payload stages** occur in this authored version. The server binds to `127.0.0.1` only, serves a single fixed path, and disables request logging. It drops from root to the unprivileged `hacker` account before serving requests.

The use of `exec` is **intentionally presented as suspicious**, to teach students why they should not run unfamiliar code. It is not required to solve the exercise; the decoded Python is intended to be read as text. The demonstration payload itself has no imports or network calls.

### Answer checker

`nyitsec-answer` requires **both** a correct behavior explanation (multiple choice) **and** the extracted case-sensitive answer string, within the same run. Any incorrect combination produces an identical, non-specific error. Only the successful combination reads the student's existing pwn.college `/flag`; no static platform flag is committed.

## Reproducibility and integrity

The review file `recovered_payload.py` is the **byte-for-byte original source** recovered from `.payload.bin`, not a paraphrase. Its SHA-256 digest is:

`2d3b191c0db4bda2b59c2396a2ba38455471e5db4b7fab9373fcf09e3eeb7042`

The binary payload's SHA-256 digest is:

`b97384863de80d84b7b011943d220df3e2e23f55e4e0d266fc0cfe9f752e1cd8`

The repository test `tests/test_suspicious_script.py` invokes only the decoder, confirms **exact byte equality** with this review source, verifies both hashes, and checks that the student workspace copies only `audit_sync.py`. It also tests the optional harmless run in a controlled subprocess.

These review files are not imported by the challenge startup, not part of its module manifest, and have no reason to be inside the runtime container. Any edit to the encoded payload should require updating the review copy and re-running CI.

## Reviewer note

A student with administrator access to the **GitHub repository** could view this review copy, but normal pwn.college students do not receive it. Keep repository access appropriately restricted. GitHub files are not a secret-storage mechanism.
