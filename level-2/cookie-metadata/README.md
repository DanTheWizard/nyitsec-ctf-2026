# Officer Notes: More Than a Cookie Recipe

**Module:** `level-2` | **ID:** `cookie-metadata` | **Difficulty:** Easy

## Design
`document.txt` contains a complete, readable chocolate chip cookie recipe, followed by an **ANSI-concealed trailer** containing a fictional case-code field.

- In an ANSI-compatible terminal, `cat document.txt` displays the recipe. The trailer's characters use the ANSI SGR *conceal* style (`ESC[8m`), followed by the reset sequence (`ESC[0m`).
- `strings document.txt` shows the printable trailer entries, including the `RECOVERY-CODE` field.
- Commands such as `cat -v`, `xxd`, or other binary inspection tools may also expose the data. All are valid investigative approaches.
- This is **embedded metadata-like text**, not actual filesystem extended attributes or EXIF metadata. Avoid describing it as file-system metadata.
- We intentionally **do not name the `strings` command in the student-facing description**.

**Important:** Some terminal implementations may handle ANSI conceal differently. Live-test `cat document.txt` in pwn.college's own terminal, not just offline tests. The student answer is the exact, case-sensitive code in the trailer.

The `verify` program compares a SHA-256 digest and reveals the student's own pwn.college flag only after the correct answer. Never expose a reusable platform flag.

## Smoke tests
1. `pwd` starts in `/nyitsec-ctf` and the file is present.
2. `cat document.txt` displays only the recipe in the standard pwn.college terminal.
3. `strings document.txt` reveals the case metadata and recovery code.
4. A wrong `nyitsec-answer` is rejected, and the correct code returns the unique student flag.
