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
