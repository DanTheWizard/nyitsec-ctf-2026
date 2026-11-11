# Stage 2: Incident Investigation

**Goal:** Identify the suspicious SSH incident in the provided **fictional** audit log.

This stage should remain locked until you **submit the Stage 1 flag** to pwn.college.

In the writable `/nyitsec-ctf` workspace, look at `access.log`. Find the **event_id** for the one entry that meets **all three conditions**:

- `service=ssh`
- `network=external` and `outcome=blocked`
- `attempts` is at least **10**

Suggested commands:

```bash
cat access.log
grep 'service=ssh' access.log
```

When you find its `event_id`, run `nyitsec-answer`. Submit the unique pwn.college flag on the challenge page to unlock Stage 3.

**Temporary workspace notice:** Work in `/nyitsec-ctf` is lost when the challenge restarts. Copy anything you want to keep into `~/`.

**Scope:** The log is synthetic; investigate only the provided lab assets.