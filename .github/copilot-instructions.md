# NYITSec Challenge Authoring

Read the repository's \`AGENTS.md\` and \`CONTRIBUTING.md\` before generating challenge files.

Use \`python3 scripts/new_challenge.py\` to create all new NYITSec challenges. It installs the standard \`.init\` interactive \`/challenge\` startup hook, \`bin/nyitsec-answer\`, \`verify\`, and student/author docs. Implement the fail-closed verifier, keep pwn.college \`/flag\` student-specific and protected, and never commit credentials. Run \`python3 scripts/validate_dojo.py\` and the unit tests before opening a pull request.
