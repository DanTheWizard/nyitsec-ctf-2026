# First Incident: SSH Log Investigation

The NYITSec security team received a **fictional authentication log**, `events.log`.

**Goal:** Find the event ID of the SSH attempt that was **external** and **blocked**.

### Investigate

Your terminal opens in `/nyitsec-ctf`. Try:

```bash
ls
cat events.log
grep 'service=ssh' events.log
```

Check the `service`, `source`, and `status` fields. Then enter the event ID:

```bash
nyitsec-answer
```

Submit the flag printed for a correct answer.

**Temporary workspace notice:** Work saved in `/nyitsec-ctf` is lost when the challenge restarts. Copy anything you want to keep to `~/`.
