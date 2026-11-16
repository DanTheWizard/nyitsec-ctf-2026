# NYITSec pwn.college — Event Readiness & Retest Checklist

**Officers only.** This checklist is stored in private GitHub under `docs/officer-solutions/`, not in any deployed challenge directory. Use the [officer guide index](README.md) for all 15 challenge-specific solutions and SSH checker probes.

## QA baseline — November 14, 2026

The secondary-account live QA report **reported** the following results across all 15 graded challenges:

| Check | Reported result |
| --- | --- |
| Normal-mode launch and SSH access | 15/15 PASS |
| Expected workspace files, write access, and startup | 15/15 PASS |
| Wrong-answer rejection and known-correct-answer acceptance | 15/15 PASS |
| Workspace restart/reset | 15/15 PASS |
| Officer/ITS documentation absent in normal and privileged instances | 15/15 PASS |
| Platform flag submission / leaderboard recording | Not tested (flags intentionally not submitted) |

No confirmed challenge failures or officer-document leaks were reported. Some QA probes required output-format workarounds; those were **test harness limitations**, not verified challenge defects.

**Scope limitation:** Answer-checker success does not by itself prove every intended educational solution path works. The full fictional Broken Login exploit/Nuke sequence and Suspicious Script's path-specific payload retrieval were not exercised in that QA run. A `night-relay/README.md` appeared in the generated student Git project; it is not evidence of an officer-document leak merely because its filename is `README.md`.

## Final pre-event checks

- [ ] Review the pending repository security/reliability audit. Triage confirmed high-impact findings before the event; defer nonessential changes that could destabilize working challenges.
- [ ] Verify the latest `main` revision and its [dojo update workflow](https://github.com/DanTheWizard/nyitsec-ctf-2026/actions/workflows/update.yml) succeeded after **any** final merge. A passing PR check alone does not confirm deployment.
- [ ] From the secondary account, open the [NYITSec dojo](https://pwn.college/example~36e653d5/) and confirm the expected modules and 15 challenges appear.
- [ ] Spot-check a fresh normal-mode launch and SSH connection in each difficulty section. Check expected input files and that `nyitsec-answer` responds. Use the [officer guide index](README.md) if checker testing is needed.
- [ ] Confirm officers can access private guide material and have a way to record reports during the event. Do not distribute guide answers, SSH private keys, update codes, or platform flags to students.

## Optional targeted end-to-end checks

These are **not blockers based solely on the existing QA report**, but are useful if time permits or if the code audit flags the relevant area.

- [ ] **Broken Login:** Perform the intended fictional waitlist/login/Nuke workflow and reset the disposable database afterward.
- [ ] **Suspicious Script:** Check the *specific* localhost payload endpoint and safe static-decode workflow, not just HTTP `/` (which may legitimately return 404).
- [ ] **Forgotten Commit:** Review the student project's generated `night-relay/README.md` to confirm it contains only intended project documentation.
- [ ] **Leaderboard:** If event scoring must be verified, submit **one** valid test-account flag and confirm the solve is recorded. This changes that account's solve history; no flag value should be copied into reports.

## If a challenge or deployment changes

Retest **the affected challenge** on a fresh instance rather than repeating all 15 by default:

- [ ] Launch normal mode, verify the workspace/startup and writable student inputs, and run both wrong/correct answer probes from its private [officer guide](README.md). Flag output must stay redacted; verifier crashes/timeouts are **BLOCKED**, not PASS.
- [ ] Check `/challenge/README.md`, `/challenge/docs`, and `/nyitsec-ctf/README.md` are absent. If deployable files or startup/isolation rules changed, inspect a **separate privileged instance** for officer/ITS documentation as well.
- [ ] Restart the instance and confirm disposable workspace state resets without affecting persistent home files.
- [ ] Log any failure with the challenge ID, tested commit, brief non-secret evidence, and a proposed fix; retest after deployment.

For a change affecting the shared `.init`, `.workspace.py`, `verify` template, or `dojo.yml`, expand the retest across relevant modules or all 15 challenges.

## Event sign-off

- **Reviewed commit / deployment workflow:** 
- **Officer / date:** 
- **Audit findings requiring action:** 
- **Optional checks completed or deferred:** 
- **Open issues and retest results:** 

**Ready for event when:** the latest deployment is healthy, the code audit has no unresolved event-blocking findings, and officers have reviewed any outstanding issues. Retain the November 14 QA baseline as historical evidence rather than treating previous PASS results as proof after a subsequent functional change.
