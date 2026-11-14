# Packet Detective — Officer Notes

**Module:** `level-3` | **ID:** `packet-detective` | **Difficulty:** Intermediate
**Order:** Second in Level 3, immediately after The Forgotten Commit

## Synthetic incident and intended investigation

A genuine classic `.pcap` file named `traffic.pcap` contains **20 simulated TCP/HTTP conversations** using documentation IPs and fictional `.test` domains. It includes multiple login form submissions, ordinary web traffic, unrelated support tickets, and one incident ticket for `CASE-417`.

The incident's HTTP **response** gives the trace reference `LAB-7B`. That reference appears in exactly one portal POST header (`X-Lab-Trace: LAB-7B`). The corresponding `/api/login` HTTP request uses `application/x-www-form-urlencoded` and sends the form body across **four TCP data segments**.

The intended answer is the invented username `bob` and password `Lumen&Branch#47`. The wire representation encodes special characters as `%26` (ampersand) and `%23` (hash). Students must not confuse them with raw literal characters. No real user credentials or actual network interactions are present.

## Officer solution

1. `cd /nyitsec-ctf` and read `incident-brief.txt`.
2. Explore HTTP traffic in Wireshark or:
   ```bash
   tshark -r traffic.pcap -Y 'http.request' -T fields -e tcp.stream -e http.request.method -e http.request.uri
   ```
3. Locate the GET request to `/tickets/CASE-417`. Follow that TCP stream; its HTML **response** contains `X-Lab-Trace: LAB-7B`.
4. Find the separate `POST /api/login` request with request header `X-Lab-Trace: LAB-7B`. Several other `POST /api/login` streams have different trace references and unrelated demo credentials.
5. Reassemble the entire target TCP stream using Wireshark's **Follow → TCP Stream** or `tshark -r traffic.pcap -q -z follow,tcp,ascii,N` (replace `N` with the discovered `tcp.stream` value). The body is divided across **four captured TCP segments**.
6. Read the `username` and `pass` form fields. Decode the special percent-encoded characters, yielding `bob` and `Lumen&Branch#47`. A standard-library check is `python3 -c 'from urllib.parse import unquote_plus; print(unquote_plus("Lumen%26Branch%2347"))'`.
7. Run `nyitsec-answer`, entering **both** values. Incorrect submissions receive one generic error; the correct pair unlocks the per-student pwn.college `/flag`.

Students who use a different valid investigative workflow should also receive credit. They do **not** need to execute code or send network traffic.

## Source, deployment and ITS transparency

- The packet file is **generated once in the GitHub authoring workflow** and committed to this repository. A new challenge instance simply copies `traffic.pcap` and `incident-brief.txt` into `/nyitsec-ctf`, using the standard NYITSec template `.init` and `.workspace.py`.
- The dependency-free Node.js authoring generator is `tools/build_packet_detective_pcap.mjs`, **outside** the deployable challenge directory. Its only output is a file on disk, not network packets sent to real hosts.
- The GitHub-only source is not staged for students, but is available for NYITSec and ITS review. See `docs/its-review/packet-detective/README.md`.
- There are no services, open ports, external downloads, package installations, privileged network interfaces, or modifications to student home settings.
- The student VM already provides Wireshark and tshark. The binary capture is fictional and self-contained.
- `verify` uses separate SHA-256 digests and requires both synthetic values before reading the actual per-student `/flag`.

## Live smoke tests

1. Confirm `/nyitsec-ctf` contains exactly `incident-brief.txt` and `traffic.pcap` and the answer is not in the instructions.
2. Run `capinfos traffic.pcap` or open it in Wireshark. Check that it is a valid Ethernet capture with complete TCP/HTTP streams.
3. Follow the `CASE-417` support ticket stream and identify `LAB-7B`.
4. Follow the matching `POST /api/login` stream, reconstruct the split form, and decode its fields.
5. Try a different user's credentials and a wrong password. Both must fail without revealing which part was incorrect.
6. Submit the exact recovered values and verify the flag.
7. Reset Challenge and verify the capture and notes are restored.

## Officer QA: verified answer and repeatable solution

**Exact correct inputs (prompt order):** `bob` → `Lumen&Branch#47`  
**Deliberately incorrect test inputs:** `bob` → `not-the-password`  
**Input policy:** Both values required: username case-insensitive with trimming, password case-sensitive with trimming. The checker gives the same generic error for any wrong combination.

### Reproduce the intended solution

Analyze the synthetic, prerecorded `traffic.pcap` without network requests. Read `incident-brief.txt`; find the `/tickets/CASE-417` request; the ticket response links trace `LAB-7B`; find its matching `POST /api/login` request; reassemble the TCP stream in Wireshark or tshark. Decode the URL-encoded request form (`%26` is `&` and `%23` is `#`). Exact username is `bob` and password `Lumen&Branch#47`.

```bash
cd /nyitsec-ctf
tshark -r traffic.pcap -Y 'http.request' -T fields -e tcp.stream -e http.request.method -e http.request.uri
python3 -c 'from urllib.parse import unquote_plus; print(unquote_plus("Lumen%26Branch%2347"))'
```

For answer-checker-only QA, supply the documented pair; analyzing the PCAP is a separate asset-integrity test.

### Noninteractive checker test over SSH

Run this self-contained Python probe **inside a fresh SSH-connected challenge instance**. It executes the existing `nyitsec-answer` command twice, one known-wrong and one known-correct submission. It checks exit status, the exact rejection message, and the presence of a correctly shaped platform flag, but **never prints or saves the flag**. `BLOCKED` means the verifier or environment could not be validated, not that the challenge was solved.

```python
import re
import subprocess
import sys

# Inputs are fictional training data from this private officer guide.
cases = [
    ("incorrect", ["bob","not-the-password"], False),
    ("correct", ["bob","Lumen&Branch#47"], True),
]
rejection_text = "One or more values do not match the evidence. Keep investigating."
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
