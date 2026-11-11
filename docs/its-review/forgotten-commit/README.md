# ITS source review: The Forgotten Commit

**Challenge:** NYITSec Level 3, The Forgotten Commit.

**Status:** Repository documentation for review only. This file does not constitute approval by NYIT or ITS.

## Purpose and exact behavior

Students investigate a genuine, fictional local Git repository, not a remote website. The authoring implementation is fully available in GitHub at `level-3/forgotten-commit/.history-builder.py`.

At each new pwn.college container start:

1. The standard, temporary, student-owned `/nyitsec-ctf` workspace is created.
2. The protected `.git-prepare.sh` extracts a packaged **genuine Git executable** with its required non-glibc libraries into `/run/nyitsec-git`. The `bin/git` wrapper exposes the usual Git CLI.
3. The protected Python generator creates `/nyitsec-ctf/night-relay` with 10 ordinary Git commits. The repository includes fictional code, synthetic station telemetry, fake commit authors with `example.test` emails, a draft recovery document, an approved version, and the later deletion of that document.
4. The generator confirms that the approved recovery phrase can be restored through Git history. It then grants the user account `hacker` ownership of the project, including all Git object files.
5. Students use `git log`, `git show`, and optionally `git restore` to recover the historical document and submit the final phrase to the existing protected `nyitsec-answer` checker.

**There are no outbound network connections, external Git remotes, personal records, real institutional passwords, or malicious programs.** Git operations target only the fresh fictional repository inside the container. An intentional reset recreates the repository. The generator fails closed rather than overwrite a preexisting project.

The source generator, startup script, bundled package archive, and package inventory are committed to GitHub for officer/security review, but are excluded from the student's `/nyitsec-ctf`. The generator and officer notes are protected by the root-run initializer; the student can examine the generated Git working tree and history normally.

## Package and code provenance

- Original authoring code: `level-3/forgotten-commit/.history-builder.py`
- Local deployment setup: `level-3/forgotten-commit/.git-prepare.sh`
- Local Git command wrapper: `level-3/forgotten-commit/bin/git`
- Reproducible package builder: `tools/build_forgotten_git_runtime.py`
- Third-party license and provenance: `tools/FORGOTTEN_GIT_RUNTIME_LICENSES.md`
- Hidden package inventory: `level-3/forgotten-commit/.git-runtime-packages.txt`
- Challenge test coverage: `tests/test_forgotten_commit.py`
- Student-visible instructions: `level-3/forgotten-commit/DESCRIPTION.md`

The generated historical ledger is deliberately absent from the current working tree, but exists in Git history for the exercise. Its recovery phrase is fictional; the individual pwn.college `/flag` is not committed.

## Safety checks

CI validates that the Git project has 10 commits and a clean HEAD, includes both the correct file deletion and an unrelated deletion, retains the final approved phrase only in the historical ledger, refuses to overwrite student work, exposes no remote configuration, and provides an executable genuine Git. The normal student workspace contains no review-only generator source.

Please review and obtain institutional authorization as appropriate before including this in a public event.
