# NYITSec CTF 2026

This private repository contains the source for our test [NYITSec pwn.college dojo](https://pwn.college/example~36e653d5/).

## Optional Linux & CLI introduction

- **Linux & CLI Quick Start (Optional):** a short, ungraded reading module with three expandable resources: terminal navigation, file searching, and responsible use of AI for hints and debugging.
- It appears before CTF Fundamentals and contains no challenges or points.
- Edit `linux-cli-intro/module.yml` for the lecture content. A video or slide deck can be added later as an ungraded lecture resource.
- See `linux-cli-intro/README.md` for author and deployment notes.

## Pilot challenge

- **CTF Fundamentals → First Incident - SSH Log Investigation:** inspect a fictional log and use `/challenge/verify` to earn a unique pwn.college flag.
- All student-facing challenge instructions are in the challenge's `DESCRIPTION.md`; officer notes are in `README.md` beside the files.
- The original template modules are preserved as examples.

## Dojo updates

- The YAML base identifier is `example`, while pwn.college assigned the deployed dojo reference `example~36e653d5`.
- The action workflow in `.github/workflows/update.yml` is configured for the deployed reference and runs after pushes to `main`.
- To activate it, create the GitHub Actions **repository secret** `UPDATE_CODE` containing only the secret update code (the final part of the private update URL).
- **Never commit or share the update code or entire secret URL.** The pwn.college SSH deploy key is for reading this private repository, not for authorizing updates.
- Develop changes on feature branches, review pull requests, then merge into `main` to deploy. First deployment must be tested in the actual pwn.college workspace.

---

## Original pwn.college example reference

This repository features an example dojo.

The dojo is defined by [dojo.yml](./dojo.yml).

It contains two modules, `hello` and `world`.

The module `hello` features challenges `apple` and `banana`.

The module `world` features challenges `earth`, `mars`, and `venus`.

Each challenge demonstrates different challenge definition capabilities, in an increasing order of feature complexity.

See each challenge's README for further information:
- [apple](./hello/apple)
- [banana](./hello/banana)
- [earth](./world/earth)
- [mars](./world/mars)
- [venus](./world/venus)

## YAML Structure of `dojo.yml`

### Dojo

The top-level object is the `Dojo`. It consists of six properties:

- `id`: **Required**. A unique identifier for the Dojo.
- `name`: **Required**. The display name of the Dojo.
- `description`: **Optional**. Additional details about the Dojo. This can include formatted markdown text.
- `type`: **Optional**. This field can take the values `course`, `topic`, or `hidden`. `course` places it in the "Courses" section. `topic` places the Dojo in the "Topics" section. `hidden` means the Dojo won't be listed (but is still accessible). If the type field is omitted or contains a value other than these three, the Dojo will appear in the "More" section.
- `password`: **Optional**. A password that users need to join the Dojo. If omitted, the Dojo is open for anyone to join.
- `modules`: **Required**. An array of `Module` objects.

### Module

Each `Module` object within the `modules` array consists of the following properties:

- `id`: **Required**. A unique identifier for the Module.
- `name`: **Required**. The display name of the Module.
- `description`: **Optional**. Additional details about the Module.
- `challenges`: **Required**. An array of `Challenge` objects.

### Challenge

Each `Challenge` object within the `challenges` array of a `Module` consists of the following properties:

- `id`: **Required**. A unique identifier for the Challenge.
- `name`: **Required**. The display name of the Challenge.
- `description`: **Optional**. Additional details about the Challenge.

## Importing Modules and Challenges

For an example of how you can import another dojo's challenges, see: [pwncollege/example-import-dojo](https://github.com/pwncollege/example-import-dojo).

## Automatically Updating Dojo

For instructions on how you can setup automatic dojo updates, using GitHub actions, see: [pwncollege/dojo-update](https://github.com/pwncollege/dojo-update).

## Challenge Writing Laws

### The Flag

The flag is located at `/flag`, and is only readable by `root`. 
The challenge will execute as `root`.
Nothing else is true.

Do not assume any structure to the flag. 
It may or may not have a prefix/suffix. 
It may or may not be 50 bytes long.
These things WILL change, and if you rely on them, your challenge WILL break.

### The Challenge

The challenge is [`setuid`](https://en.wikipedia.org/wiki/Setuid).
This is how your challenge will execute as `root`.

What this *really* means:
- The process will run with an **effective** user of `root`.
- The process will run with a **real** user of `hacker`.

While an **effective** user of `root` is sufficient for opening the flag, there are some caveats.
When `/bin/sh` (which is linked to `/bin/dash`) is run under this, it will immediately set the **effective** user to the **real** user (unless the `-p` flag is provided).
This means that both the **effective** and **real** user will be `hacker`, and the flag will not be accessible.
This affects `system`, which ultimately just runs `/bin/sh`.

The challenge can remedy this by explicitly setting the **real** user to the **effective** user:
```c
setreuid(geteuid(), -1)
```




