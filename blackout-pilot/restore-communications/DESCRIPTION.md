# Stage 3: Restore Communications

**Goal:** Decode the simulated recovery note and locate its restoration code.

This stage should remain locked until pwn.college records your Stage 2 flag submission.

Your writable `/nyitsec-ctf` workspace contains `recovery.rot13`. The note uses **ROT13**, a letter substitution that shifts each letter by 13 positions. Decode it with:

```bash
cat recovery.rot13
tr 'A-Za-z' 'N-ZA-Mn-za-m' < recovery.rot13
```

Find the value of `RESTORE_CODE`, run `nyitsec-answer`, and submit your unique pwn.college flag on the challenge page.

This completes the three-stage **progress-lock test**. This pilot has no competition weighting or completion bonus.

**Temporary workspace notice:** Work in `/nyitsec-ctf` is lost when the challenge restarts. Copy anything you want to keep into `~/`.

**Scope:** All content is fictional and remains inside the authorized pwn.college lab.