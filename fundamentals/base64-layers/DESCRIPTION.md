# Base64 Layers: Triple Decode

**Difficulty:** Beginner+ | **Skill:** Repeating a decoding step

This time, the NYITSec message has been encoded with Base64 **three times**. Decoding it once will not reveal the final message!

**Your task:** Decode `message.b64` until you can read a normal message containing an **answer code**, then submit that code using the usual NYITSec checker.

Your terminal should start in the writable `/nyitsec-ctf` directory. If it does not, run `cd /nyitsec-ctf`.

### Investigate

```bash
ls
cat message.b64
base64 -d message.b64
```

If the output still looks like Base64, you have only removed one layer. You can repeat the process with intermediate files, or use the **pipe** symbol `|` to send decoded output directly to another command.

For example, the command below removes **two** layers:

```bash
base64 -d message.b64 | base64 -d
```

How could you remove one more layer?

### Submit

When the decoded text is readable and displays the answer code, run:

```bash
nyitsec-answer
```

The checker reveals your own pwn.college flag if the code is correct.

**Reminder:** Base64 encoding is reversible, and repeated encoding does not make data secure.

**Temporary workspace notice:** `/nyitsec-ctf` is part of the current challenge container and is not persistent. Copy any scripts or notes you want to keep to `~/` before restarting or switching challenges.
