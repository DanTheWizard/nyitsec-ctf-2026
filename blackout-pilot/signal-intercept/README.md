# 1. Signal Intercept — Author Notes

**Module:** `blackout-pilot` | **Challenge:** `signal-intercept`

This exercise was created with the NYITSec standard generator structure: its `.init` and `.workspace.py` match the shared template; protected verifier and bin wrapper remain outside the writable `/nyitsec-ctf` workspace. Student input file: `transmission.b64`.

**Verifier:** Computes the expected answer from the root-owned challenge artifact and only reads `/flag` after a correct answer; no reusable flag is stored. Test wrong then correct answers.

**Progression:** Stage 1 opens freely; Stages 2 and 3 use `progression_locked: true` in `module.yml`. Test with a participant account, because dojo admins bypass locks.

**Deployment:** Draft PR only until reviewed. Read `blackout-pilot/PILOT_TEST_PLAN.md` before merging.

**Temporary workspace:** Copy important student scripts from `/nyitsec-ctf` into `~/` before restarting.
