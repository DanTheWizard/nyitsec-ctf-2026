#!/usr/local/bin/python
"""Build a genuine, synthetic Git history for an isolated NYITSec exercise.

This source is reviewed in GitHub but root-only under /challenge. It is not
copied to /nyitsec-ctf; only its generated Git working tree is student-owned.
"""
import os
from pathlib import Path
import pwd
import subprocess

DESTINATION = Path("/nyitsec-ctf/night-relay")
GIT_COMMAND = str(Path(__file__).resolve().parent / "bin" / "git")
LEDGER = "config/recovery-ledger.toml"
RECOVERY_PHRASE = "Paper satellites still orbit"

PEOPLE = (
    ("Mara Holt", "mara.holt@example.test"),
    ("Noah Vale", "noah.vale@example.test"),
    ("Quinn Lee", "quinn.lee@example.test"),
    ("Riley Chen", "riley.chen@example.test"),
)


def git(repo, *args, environment=None):
    env = os.environ.copy()
    env.update({
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_CONFIG_COUNT": "2",
        "GIT_CONFIG_KEY_0": "commit.gpgsign",
        "GIT_CONFIG_VALUE_0": "false",
        "GIT_CONFIG_KEY_1": "core.hooksPath",
        "GIT_CONFIG_VALUE_1": os.devnull,
    })
    if environment:
        env.update(environment)
    proc = subprocess.run(
        [GIT_COMMAND, "-C", str(repo), *args], check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=8,
    )
    return proc.stdout.strip()


def write(root, name, content):
    target = root / name
    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def commit(repo, number, message, person):
    author, email = PEOPLE[person]
    date = f"2026-09-{number + 2:02d}T12:00:00 +0000"
    env = {
        "GIT_AUTHOR_NAME": author, "GIT_AUTHOR_EMAIL": email,
        "GIT_COMMITTER_NAME": author, "GIT_COMMITTER_EMAIL": email,
        "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date,
    }
    git(repo, "add", "-A", environment=env)
    git(repo, "commit", "--no-verify", "-m", message, environment=env)


def build_history(repo: Path, uid=None, gid=None):
    """Generate a real, ten-commit project without rewriting existing files."""
    repo = Path(repo)
    if not repo.is_absolute() or repo == Path("/") or repo.is_symlink():
        raise ValueError("The project path must be absolute and safe")
    if repo.exists():
        raise FileExistsError("Refusing to overwrite an existing Git project")
    if not Path(GIT_COMMAND).is_file():
        raise RuntimeError("The bundled Git launcher must be present")
    repo.mkdir(mode=0o700, parents=True)
    git(repo, "init", "--initial-branch=main", "-q")
    write(repo, ".gitignore", "*.tmp\n__pycache__/\n")
    write(repo, "README.md", """# Night Relay

Fictional amateur-satellite status dashboard for an offline training case.
No stations or people here are real, and nothing contacts the internet.

Investigators: begin with docs/incident-204.md.
Each Git commit is a historical snapshot, even if its files are gone now.
""")
    write(repo, "src/status.py", """#!/usr/bin/env python3
stations = {"north-beacon": "online", "east-beacon": "monitoring",
            "west-beacon": "maintenance"}
if __name__ == "__main__":
    print("Night Relay: offline status")
    for station, status in stations.items():
        print(station, status)
""")
    write(repo, "docs/architecture.md",
          "# Architecture\nOnly fictional sensors and an offline status script.\n")
    commit(repo, 1, "chore: initialize the Night Relay demo", 0)

    write(repo, "data/beacons.csv", """station,signal,voltage,status
north-beacon,-51,12.2,online
east-beacon,-66,12.0,online
west-beacon,-89,11.7,maintenance
""")
    write(repo, "docs/temporary-contacts.md", """# Old contacts (fictional)
A fake test desk and a simulated operator. No real contact information.
""")
    commit(repo, 2, "feat: add example station observations", 1)

    write(repo, LEDGER, """# Draft recovery ledger (synthetic)
[handoff]
release = "NR-24-ALPHA"
state = "draft"
recovery_phrase = "pending sign-off"
reviewer = "Mara Holt"
""")
    commit(repo, 3, "ops: add draft recovery ledger", 2)

    write(repo, "docs/release-process.md", """# Release handoffs
Each launch requires an approved recovery ledger signed before cleanup.
The Git commit graph preserves the previous state of tracked files.
""")
    write(repo, "config/console.ini", "[view]\ntheme = midnight\nrefresh_seconds = 30\n")
    commit(repo, 4, "docs: describe release and handoff practices", 3)

    write(repo, LEDGER, """# Approved Night Relay recovery ledger (fictional)
[handoff]
release = "NR-24-ALPHA"
state = "approved"
recovery_phrase = "Paper satellites still orbit"
reviewer = "Quinn Lee"
signoff = "confirmed before cleanup"
""")
    commit(repo, 5, "ops: approve the beacon handoff ledger", 2)

    write(repo, "data/maintenance.csv", """station,date,note
west-beacon,2026-09-07,antenna inspection
north-beacon,2026-09-12,battery calibration
east-beacon,2026-09-19,simulated relay test
""")
    commit(repo, 6, "chore: schedule routine maintenance", 1)

    (repo / "docs/temporary-contacts.md").unlink()
    write(repo, "docs/contact-policy.md",
          "# Contact policy\nOnly fictional records are permitted in this repo.\n")
    commit(repo, 7, "cleanup: remove obsolete mock contact list", 0)

    write(repo, "docs/status-notes.md", """# Status report
The offline beacon console is stable. Authorization details live
in the separately tracked handoff ledger.
""")
    commit(repo, 8, "docs: update the operations status summary", 3)

    (repo / LEDGER).unlink()
    commit(repo, 9, "cleanup: remove retired handoff ledger", 1)

    write(repo, "docs/incident-204.md", """# Incident 204: Missing sign-off record

During an audit of the fictional Night Relay project, the team discovered
that an important recovery ledger had been removed during cleanup.

The current working tree no longer contains the approved handoff phrase.
Find the most recent APPROVED version of the deleted document, not the
earlier draft. The repository still has its complete local Git history.

Retrieve the recovery_phrase from the handoff section and report it.
""")
    commit(repo, 10, "docs: record audit issue for missing handoff", 2)

    if (repo / LEDGER).exists():
        raise AssertionError("The current checkout must not contain the ledger")
    if len(git(repo, "log", "--format=%s").splitlines()) != 10:
        raise AssertionError("Expected exactly ten commits")
    deleted = git(
        repo, "log", "--format=%H", "--diff-filter=D", "--", LEDGER,
    ).splitlines()[0]
    recovered = git(repo, "show", f"{deleted}^:{LEDGER}")
    if f'recovery_phrase = "{RECOVERY_PHRASE}"' not in recovered:
        raise AssertionError("Git history does not contain the approved phrase")

    # Check Git history before changing ownership; Git refuses repos owned by
    # another account unless explicitly marked safe.
    for path in sorted(repo.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        if path.is_symlink():
            raise ValueError("Symlinks are not allowed in the training project")
        path.chmod(0o700 if path.is_dir() else 0o600)
        if uid is not None and gid is not None:
            os.chown(path, uid, gid)
    repo.chmod(0o700)
    if uid is not None and gid is not None:
        os.chown(repo, uid, gid)

    return repo


def main():
    account = pwd.getpwnam("hacker")
    build_history(DESTINATION, uid=account.pw_uid, gid=account.pw_gid)
    print("NYITSec: Git project ready at /nyitsec-ctf/night-relay")


if __name__ == "__main__":
    main()
