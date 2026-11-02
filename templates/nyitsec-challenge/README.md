# {{CHALLENGE_TITLE}} — Author Notes

**Module:** \`{{MODULE_ID}}\`
**Challenge ID:** \`{{CHALLENGE_ID}}\`

## Setup included automatically

- \`/challenge/.init\`: container-local interactive Bash startup logic that opens new terminals in \`/challenge\`.
- \`/challenge/bin/nyitsec-answer\`: convenience command available on pwn.college's challenge \`PATH\`.
- \`/challenge/verify\`: protected answer verifier. **Its \`is_correct()\` is a fail-closed stub and must be implemented.**
- \`DESCRIPTION.md\`: instructions visible to students.

All three executable files must retain the Git executable bit (mode \`100755\`).

## Before merging

- [ ] Implement the verification logic in \`verify\` and check it does not reveal \`/flag\` prematurely.
- [ ] Replace the student-facing TODOs.
- [ ] Test wrong and correct answers in the live pwn.college challenge.
- [ ] Confirm \`pwd\` starts at \`/challenge\` and \`nyitsec-answer\` runs.
- [ ] Confirm the checker still works if a student intentionally changes directory.
- [ ] Never commit secrets, reusable static flags, or updates to personal persistent shell settings.
