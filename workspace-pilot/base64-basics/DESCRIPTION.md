# PILOT: Base64 Basics

**Experimental workspace test.** This is a copy of the existing Base64 Basics exercise. The original challenge remains unchanged.

Your terminal should open in **`/nyitsec-ctf`**, a temporary directory where you can create and edit files.

Read and decode the provided message:

```bash
pwd
ls
cat message.b64
base64 -d message.b64
```

Find the **answer code** in the decoded message. You can try saving a decoded copy inside your writable directory:

```bash
base64 -d message.b64 > decoded.txt
cat decoded.txt
```

Run `nyitsec-answer` and enter the decoded answer code. The protected checker remains at `/challenge/verify` and reveals a unique pwn.college flag when you solve the challenge.

**Temporary workspace notice:** Files in `/nyitsec-ctf`, including `decoded.txt`, are not preserved after the challenge container is replaced or restarted. Save important work in `~/` first.
