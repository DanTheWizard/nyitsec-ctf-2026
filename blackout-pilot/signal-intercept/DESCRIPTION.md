# Stage 1: Signal Intercept

**Goal:** Recover the authorization code from a simulated intercepted transmission.

This is a short **Operation Blackout progress-lock pilot**, not a scored competition round. The first stage is immediately available.

Your terminal starts in the writable `/nyitsec-ctf` workspace. Inspect the provided Base64 transmission:

```bash
ls -la
cat transmission.b64
base64 -d transmission.b64
```

Locate the line beginning `AUTH_CODE=`, then run:

```bash
nyitsec-answer
```

Enter the authorization code (the value after the equals sign), then **submit the unique pwn.college flag on the challenge page**. The next stage unlocks only after that submission is recorded. Refresh the module page if necessary.

**Temporary workspace notice:** Work in `/nyitsec-ctf` is lost when the challenge restarts. Copy anything you want to keep into `~/`.

**Scope:** Use only the provided synthetic files and pwn.college environment; do not attempt anything against real university systems.