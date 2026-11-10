# Base64 Layers: Triple Decode

**Goal:** Decode `message.b64`, which has been Base64-encoded **three times**, and find the final answer code.

Start in `/nyitsec-ctf`:

```bash
cat message.b64
base64 -d message.b64
```

If the result still looks encoded, decode it again.

**Hint:** The pipe symbol (`|`) sends one command's output into another. For example, two decoding steps can be combined:

```bash
base64 -d message.b64 | base64 -d
```

Once you find the readable message, run `nyitsec-answer` and enter its answer code. Submit the flag you receive.

**Temporary workspace notice:** Files saved in `/nyitsec-ctf` disappear when the challenge restarts. Copy important work to `~/`.
