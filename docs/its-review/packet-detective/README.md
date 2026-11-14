# ITS Source Review: Packet Detective

**Scope:** NYITSec Level 3 packet-analysis exercise. **This document supports review and does not imply ITS approval.**

The students receive a **pre-generated synthetic `.pcap` file** plus an incident briefing. No packet capture occurs on the student's real network, and no network services start when the challenge runs.

The authoring program `tools/build_packet_detective_pcap.mjs` constructs fictional HTTP requests and responses using standalone JavaScript, with synthetic form fields, private/documentation IP ranges, fictional `.test` domains, TCP handshakes, split request bodies and normal connection termination. The program writes Ethernet, IPv4, and TCP bytes directly to the repository capture file; it does **not** open network sockets or transmit packets.

The scenario contains 20 simulated browser TCP sessions including several fake logins. The mission requires finding a helpdesk case in an HTTP stream, correlating a trace marker with a second TCP conversation, reconstructing a segmented HTTP form and decoding percent-encoded symbols.

**Actual secrets:** None. All credentials are invented demonstration strings and have no authority on any real system. The protected `verify` compares SHA-256 digests of the two recovered fields and releases only the pwn.college platform's own unique flag after both match.

**Runtime and privacy:** Student workspace contains only `traffic.pcap` and `incident-brief.txt`. The normal NYITSec initializer copies those static inputs without elevated networking permissions. Wireshark/tshark operate on an offline file. No external IPs are contacted, no actual HTTP requests are made, and no real account, email, or institutional record is included.

**Audit materials:** `tools/build_packet_detective_pcap.mjs`, `tests/test_packet_detective.py`, `docs/officer-solutions/level-3/packet-detective.md`, and the checked-in capture document exact behavior. Any changes to the capture-generation logic should regenerate the capture and pass CI checks.
