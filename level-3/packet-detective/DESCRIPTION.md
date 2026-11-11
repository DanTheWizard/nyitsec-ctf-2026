# Packet Detective

A fictional helpdesk suspects someone submitted login credentials **over unencrypted HTTP**. You have been given a packet capture with several different web sessions.

**Mission:** Identify the login associated with **CASE-417**, reconstruct the relevant HTTP request, and recover its **username and password**.

Everything here is **synthetic evidence made for this authorized NYITSec CTF VM**. The domains, addresses, accounts, and credentials are invented. No live server or external network access is required.

### Start investigating

Your temporary workspace is `/nyitsec-ctf`:

```bash
cd /nyitsec-ctf
cat incident-brief.txt
ls -lh traffic.pcap
```

You may open `traffic.pcap` in **Wireshark** through the Desktop, or use **`tshark`** in the terminal. Both are preinstalled.

One useful way to list HTTP requests is:

```bash
tshark -r traffic.pcap -Y http.request -T fields -e tcp.stream -e http.request.method -e http.request.uri
```

**Hints:** Find the captured support ticket first. Its response contains a reference to a different HTTP request. There are several unrelated logins, so avoid submitting the first password you see. A password may span multiple TCP packets, and HTTP form values can use percent-encoding.

To examine a complete conversation, Wireshark provides **Follow → TCP Stream**. The equivalent `tshark` feature is `-z follow,tcp,ascii,<stream-number>`.

When you recover both fields, run:

```bash
nyitsec-answer
```

If you accidentally alter or lose the capture, use **Reset Challenge** to restore a clean copy. Files under `/nyitsec-ctf` are temporary, so copy notes to `~/` if needed.
