# Operation Blackout: progress-lock pilot test plan

## Scope

This pilot validates the **built-in pwn.college `progression_locked`** feature, not tournament scoring or leaderboard updates. It is intentionally self-contained and separate from the five existing Fundamentals challenges and ungraded CLI introduction.

**Important:** Test using a **regular participant account**, not the dojo administrator, because pwn.college administrators bypass progression locks.

## Expected participant behavior

1. Open the Operation Blackout pilot module. Stage 1 is available; Stages 2 and 3 appear locked.
2. Try to start Stage 2 before any solve. The platform should reject it as locked (not merely hide the launch button).
3. Start Stage 1; confirm `pwd` is `/nyitsec-ctf`. Decode `transmission.b64`; test an incorrect answer with `nyitsec-answer` (no flag), then the correct one (unique flag).
4. **Before submitting** Stage 1's flag, refresh the module page. Stage 2 should still be locked.
5. Submit Stage 1's unique flag on pwn.college; refresh. Stage 2 should now be available, while Stage 3 stays locked.
6. Start Stage 2; inspect `access.log`; use the specified criteria to locate the one suspicious `event_id`. Submit its unique flag.
7. Verify Stage 3 unlocks only after Stage 2 is recorded. Decode `recovery.rot13`, answer, submit the final unique flag, and verify the whole module shows solved.
8. Log out or use a separate **unsolved** participant account and verify its stages are independently locked, even after the first participant finishes.

## Non-admin pass criteria

- [ ] First stage initially launchable
- [ ] Second and third stages initially locked
- [ ] Direct Stage 2 launch rejected prior to Stage 1 solve
- [ ] Correct Stage 1 answer alone does not unlock Stage 2
- [ ] Stage 1 flag submission unlocks Stage 2 only
- [ ] Stage 2 flag submission unlocks Stage 3
- [ ] Independent participant retains independent progression
- [ ] Incorrect `nyitsec-answer` responses do not reveal a flag
- [ ] All three challenges preserve the /nyitsec-ctf writable workspace standard

## What this does not test

- Time-based competition start/stop or access codes
- Score weights, full completion bonuses, polling, or leaderboards
- Multi-module unlocking (the flag only gates the previous challenge **within the same module**)

## Deployment safeguards

Keep this on a **draft PR** until reviewed. Do **not** merge just to test CI: the repository's `main` push workflow automatically updates the connected testing dojo. Once reviewed, merging the pilot will make it appear in the testing dojo; verify from a non-admin account before using the feature in the main event.
