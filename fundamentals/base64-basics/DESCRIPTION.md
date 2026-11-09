# Base64 Basics: Decode a Message

**Difficulty:** Beginner | **Skill:** Recognizing and decoding Base64

A member of the NYITSec team found a message stored in `message.b64`. It looks unreadable, but the contents are simply **encoded**, not encrypted.

**Your task:** Decode the message, find the **answer code** in the decoded text, and enter that code into the NYITSec answer checker.

Your terminal should start in the writable `/nyitsec-ctf` directory. If it does not, run `cd /nyitsec-ctf`.

### Start here

```bash
pwd
ls
cat message.b64
```

Base64 is an *encoding*, not a secure way to hide information. On Linux, try:

```bash
base64 --decode message.b64
```

The shorter `base64 -d message.b64` does the same thing.

### Submit

```bash
nyitsec-answer
```

Enter the answer code shown **inside the decoded message**, then submit the unique pwn.college flag that the checker prints.

**Tip:** If your terminal reports "No such file or directory", run `pwd` and check that you are in `/challenge`.

**Temporary workspace notice:** `/nyitsec-ctf` is part of the current challenge container and is not persistent. Copy any scripts or notes you want to keep to `~/` before restarting or switching challenges.
