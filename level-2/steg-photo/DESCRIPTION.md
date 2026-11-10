# The Photograph's Secret

The NYITSec team received a JPEG photograph as part of a fictional evidence review. The picture appears ordinary, but the investigator believes an **entire file may be hidden inside it**.

**Goal:** Recover the hidden note from `evidence.jpg` and submit the response code inside.

Your files are in `/nyitsec-ctf`. Start by reading `case-note.txt` and examining the picture:

```bash
ls
cat case-note.txt
file evidence.jpg
```

**Hint:** This technique is called *steganography*. The image was prepared using a tool called **steghide**, which is provided in this challenge. Try `steghide --help` to learn how to extract embedded files. The passphrase is in `case-note.txt`.

Once you recover the note, read it, run `nyitsec-answer`, and enter the response code. Submit the unique pwn.college flag you receive.

**Temporary workspace:** Files in `/nyitsec-ctf` disappear when the challenge restarts. Save important work to `~/`.
