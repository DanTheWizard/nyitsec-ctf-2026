# Officer Notes: The Forgotten File

**Module:** `level-2` | **ID:** `forgotten-file` | **Difficulty:** Easy

## Objective

Students practice recursive file discovery and content searches rather than manually checking guessed filenames. This is a fictional, authorized digital-evidence exercise.

Each fresh pwn.college challenge container generates a tree of **nine top-level areas, 36 nested branches, and 108 ordinary files**. File names and everyday document contents vary. One ordinary document is selected randomly to include a short investigation note and a synthetic case code; the filename gives no special indication that it contains the clue.

There is no fixed target path in the challenge or student instructions. `random.SystemRandom()` selects the location on every new container launch, but two unrelated launches could coincidentally select the same path. A new terminal within the same container does not regenerate the tree.

## Startup and protected implementation

- The standard `.workspace.py` creates `/nyitsec-ctf` as usual.
- `.init` extends the shared initializer with the approved `RANDOM_ARCHIVE_INIT_SUFFIX`; the root-owned `/challenge/.scatter.py` runs once **after** workspace creation.
- `.init` changes `.scatter.py` to mode `0600` before running it. The `.ctfignore` also excludes it from the student workspace.
- `.scatter.py` refuses to overwrite a nonempty workspace, writes synthetic decoys, appends one clue, then sets directory and file ownership to the unprivileged `hacker` account. New files are nonexecutable.
- The protected `verify` compares an answer digest and reveals only the student's pwn.college `/flag` on success. `bin/nyitsec-answer` is unchanged.

The answer phrase is purposefully present in the root-owned generation code and in the generated random document. The private repository is an **authoring source**, not a secret store.

## Manual live tests

1. Start Level 2 → The Forgotten File, confirm `pwd` is `/nyitsec-ctf`, and `find . -type f | wc -l` reports 108.
2. Try `grep -Rni 'case' .` and `grep -Rni 'review' .`; these should return both noise and the actual clue.
3. Run `nyitsec-answer` with a wrong code (no flag) and the recovered code (student-specific flag).
4. Open another terminal in the same container. The files should remain unchanged.
5. Start a fresh challenge container, run `find`/`grep` again, and check the clue path can vary.
6. Confirm `cat /challenge/.scatter.py` is permission denied for `hacker`, while documents under `/nyitsec-ctf` are readable and writable.

Unit tests cover many seeded random layouts, exactly one clue, permission behavior, and the rejected-overwrite guard.
