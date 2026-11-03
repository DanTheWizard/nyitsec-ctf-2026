# More Base64?

**Difficulty:** Beginner+ | **Skill:** Base64 decoding and extracting data from mixed messages

You've received a forwarded conversation from the NYITSec message system. Someone has repeatedly encoded a message with Base64, but it is **not just one long Base64 string anymore**.

Some decoded layers include ordinary chat text, such as message headers or replies, mixed with the next encoded section.

**Your mission:** Follow the conversation back to the original message. Find the **two-word message** at the very end and enter those two words into the NYITSec answer checker.

### Step 1: Read and decode

Your terminal should start in `/challenge`. If not, enter `cd /challenge`.

```bash
ls
cat message.b64
base64 -d message.b64
```

### Step 2: Look carefully at the output

After the first decode, not everything you see will be Base64. Identify the *encoded portion*, then decode **only that portion** to continue.

One option is to copy the Base64 section and use:

```bash
printf '%s' 'PASTE_BASE64_HERE' | base64 -d
```

You can also use `grep`, `cut`, or other Linux text-processing tools to isolate the encoded section without copying it by hand.

If the output contains more conversation text, repeat the process until you recover the original message.

### Step 3: Check your answer

```bash
nyitsec-answer
```

Enter the **final two-word message**, not an intermediate message or a Base64 string. A correct answer reveals your unique pwn.college flag.

**Hint:** A successful Base64 decode does not always mean you have reached the final answer. Read each result before decoding again.

**Reminder:** Base64 is encoding, not encryption, and normal message text should not be treated as Base64 data.
