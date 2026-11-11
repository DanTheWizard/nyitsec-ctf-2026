# The Forgotten Commit

**Mission:** A fictional satellite-monitoring team deleted an important recovery ledger during repository cleanup. The current files no longer contain the approved handoff phrase, but the project's **Git history** may still preserve it.

**Goal:** Recover the **approved** recovery phrase from the missing ledger and submit it.

This is a fully **fictional, offline Git investigation inside your specially prepared pwn.college challenge VM**. No external GitHub access or real credentials are needed.

### Start here

The project is in your writable `/nyitsec-ctf` workspace:

```bash
cd /nyitsec-ctf/night-relay
cat docs/incident-204.md
git status
git log --oneline
```

**Hints:**
- A deleted file disappears from the latest working tree, but earlier commits may still include it.
- Git records which files were changed or removed in each commit. `git log --stat` and `git show` are useful investigation tools.
- The ledger had both a draft and an **approved** revision. Recover the final approved phrase, not the draft.
- You can inspect historical files without changing the current branch.

Once you find the phrase, run:

```bash
nyitsec-answer
```

If you accidentally damage the repository's history or cannot continue, use **Reset Challenge** to generate a fresh copy.

**Temporary workspace:** Files in `/nyitsec-ctf` disappear when the challenge restarts. Copy important notes to `~/` first.
