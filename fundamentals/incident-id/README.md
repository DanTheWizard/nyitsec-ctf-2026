# NYITSec pilot challenge: SSH Log Investigation

**Learning goal:** use basic shell commands to inspect a fictional authentication log and identify the event that matches three conditions.

- Student description: `DESCRIPTION.md`
- Data file: `events.log`
- Entry point: `verify`
- Correct investigation: the unique row with `service=ssh`, `source=external`, and `status=blocked`
- Flag: pwn.college provides a unique, root-protected `/flag` per student. No static flag is committed.

Addresses are from documentation-only ranges (RFC 5737). This activity does not analyze or contact any real systems.

## Verification

After publishing, start the challenge as a regular student. Confirm `/challenge/events.log` can be read, `/challenge/verify` can run, wrong answers do not reveal flags, and the correct answer prints the pwn.college flag. Submit that flag to confirm the challenge records a solve.
