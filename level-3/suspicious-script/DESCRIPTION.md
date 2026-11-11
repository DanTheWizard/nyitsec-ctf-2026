# The Suspicious Script

An investigator discovered a Python script with confusing variable names, encoded text, and an unknown download. The script might do something unexpected.

**Goal:** Explain what the script actually does and recover an answer hidden inside the downloaded, encoded data. **Do not execute unfamiliar code merely to see what happens.**

Your terminal begins in the writable `/nyitsec-ctf` directory.

### Start with static analysis

```bash
ls
cat audit_sync.py
```

Follow the imports, look for transformations of strings or bytes, and find where the data comes from. The script contacts a **fictional service on this challenge's localhost**, so you can investigate the resource without contacting an outside system.

**Hints:**
- Encoded strings can hide a URL, but encoding is not encryption.
- A short XOR operation may transform downloaded bytes before another decoding step.
- Ask yourself whether the script **reads**, **writes**, **imports**, or **executes** the recovered content.
- The script contains a decoding helper you can study and reuse in your *own safe analysis program*. Inspect its behavior before importing or invoking anything. Reading decoded Python source is different from executing it.

When ready, run `nyitsec-answer`. You must provide **both** the most accurate behavior description (multiple choice) and the recovered answer string. The checker will not tell you which part is wrong.

**Temporary workspace:** Files in `/nyitsec-ctf` disappear when the challenge restarts. Copy important notes to `~/` to keep them.
