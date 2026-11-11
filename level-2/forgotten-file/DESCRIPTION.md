# The Forgotten File

The NYITSec team has received a fictional office archive. It contains **dozens of ordinary documents** across many folders, but one file holds a forgotten investigation note.

**Goal:** Find that note and recover its case code.

Your terminal opens in the writable `/nyitsec-ctf` directory. The clue is placed in a **random subfolder each time you start the challenge**, so don't rely on a particular path.

### Start searching

```bash
pwd
ls
find . -type f
```

Most files are unrelated. You do not need to open every document manually.

**Hint:** `grep` can search **inside** files, including those in subdirectories. Try looking for words associated with an investigation, such as *case* or *review*. You can use `grep --help` if needed.

When you find the case code, run:

```bash
nyitsec-answer
```

Enter the code exactly and submit your unique pwn.college flag.

**Temporary workspace:** Files in `/nyitsec-ctf` disappear when the challenge restarts. Copy anything important to `~/` first.
