# First Incident: SSH Log Investigation

Welcome to your first NYITSec investigation!

**Your terminal should open inside the writable `/nyitsec-ctf` workspace.** If it does not, run `cd /nyitsec-ctf`. The original files and protected checker remain under `/challenge`.

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

**Temporary workspace notice:** `/nyitsec-ctf` is part of the current challenge container and is not persistent. Copy any scripts or notes you want to keep to `~/` before restarting or switching challenges.
