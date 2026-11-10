# Base64 Basics: Decode a Message

**Goal:** Decode `message.b64` to discover the answer code.

Base64 is an **encoding**, not encryption. Your terminal starts in `/nyitsec-ctf`.

```bash
ls
cat message.b64
base64 -d message.b64
```

Find the answer code in the decoded text, then run:

```bash
nyitsec-answer
```

Enter the code and submit the flag it prints.

**Temporary workspace notice:** Files saved in `/nyitsec-ctf` disappear when the challenge restarts. Copy important work to `~/`.
