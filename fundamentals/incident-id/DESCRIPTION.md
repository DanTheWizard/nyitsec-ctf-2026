# First Incident: SSH Log Investigation

Welcome to your first NYITSec investigation!

**Your terminal should open inside `/challenge`.** If it does not, enter `cd /challenge` to move there.

The security team has provided a fictional log file called `events.log`.

Find the **event ID** for the **SSH** login attempt that was **external** and **blocked**.

### Start investigating

You can begin with these commands:

```bash
pwd
ls
cat events.log
grep 'service=ssh' events.log
```

Pay close attention to the `service`, `source`, and `status` fields.

### Submit your answer

Once you identify the event ID, run:

```bash
nyitsec-answer
```

Enter the event ID when prompted. A correct answer will reveal your **unique pwn.college flag**, which you can submit on this page.

If the shortcut is unavailable, the original command still works:

```bash
/challenge/verify
```

**Reminder:** All log events and IP addresses in this challenge are fictional.
