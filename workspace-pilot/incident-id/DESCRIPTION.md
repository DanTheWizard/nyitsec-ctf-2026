# PILOT: SSH Log Investigation

**Experimental workspace test.** This is a copy of the existing SSH investigation, with the same fictional event log and answer checker. The original challenge is unchanged.

When you open the terminal, it should start in the **writable** `/nyitsec-ctf` directory, not in `/challenge`.

```bash
pwd
ls -la
cat events.log
grep 'service=ssh' events.log
```

Find the event ID for the **external**, **blocked** SSH attempt. You can create and edit your own files here:

```bash
printf 'testing writable workspace\n' > my-notes.txt
cat my-notes.txt
```

Then run `nyitsec-answer` and submit the unique flag it prints after a correct answer.

**Protected originals:** `/challenge/verify` and `/challenge/bin/` stay outside this workspace. The verifier reads the original `/challenge/events.log`, so changing your working copy will not change the correct answer.

**Temporary workspace notice:** Files in `/nyitsec-ctf` are lost when this challenge container is replaced or restarted. Save important notes to `~/` first. The standard `fundamentals` challenge behaves as before.
