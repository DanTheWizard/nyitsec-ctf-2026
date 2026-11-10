# More Base64?

A forwarded message has been Base64-encoded multiple times. Some decoded layers contain **normal conversation text mixed with another Base64 string**.

**Goal:** Recover the original **two-word message**.

Start in `/nyitsec-ctf`:

```bash
cat message.b64
base64 -d message.b64
```

Each time you decode, read the result carefully. When you see normal text surrounding Base64, copy **only the encoded part** and try:

```bash
printf '%s' 'PASTE_BASE64_HERE' | base64 -d
```

Repeat until you find the original two-word message. Enter those words using `nyitsec-answer`, then submit the flag.

**Temporary workspace notice:** Files saved in `/nyitsec-ctf` disappear when the challenge restarts. Copy important work to `~/`.
