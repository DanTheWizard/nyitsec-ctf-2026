# First Incident: SSH Log Investigation

Welcome to your first NYITSec investigation!

The security team has provided a fictional log file at `/challenge/events.log`.

Find the **event ID** for the **SSH** login attempt that was **external** and **blocked**.

When you have the correct event ID, run `/challenge/verify` and type in your answer. The program will provide your unique pwn.college flag.

Some commands that might help:

```bash
ls /challenge
cat /challenge/events.log
grep 'service=ssh' /challenge/events.log
```

Pay close attention to the `service`, `source`, and `status` fields. All event details are fictional.
