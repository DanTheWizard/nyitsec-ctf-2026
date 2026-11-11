# DNS Treasure Hunt

An investigator suspects that an unusual message is scattered across the DNS records of a **fictional organization**.

**Goal:** Follow the record references, reconstruct the hidden message, and submit it.

Your terminal opens in the writable `/nyitsec-ctf` workspace. The DNS server is **local to this challenge**, not a public website.

### Get started

```bash
cat dns-briefing.txt
dig -v
dig @127.0.0.1 -p 5300 archive.nyitsec.test TXT
```

The DNS tool **`dig` is already provided**, so there is nothing to install.

**Hints:** DNS has more than one type of record. A hostname can lead you to other hostnames, and not every TXT record contains a useful clue. Some evidence may need to be combined or decoded.

When you recover a readable message, run `nyitsec-answer` and submit the flag it prints.

**Temporary workspace:** Files saved in `/nyitsec-ctf` disappear when the challenge restarts. Copy important notes to `~/`.
