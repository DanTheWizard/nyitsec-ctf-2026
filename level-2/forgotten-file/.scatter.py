#!/usr/local/bin/python
"""Populate a fresh NYITSec workspace with a randomized synthetic archive.

Invoked once per challenge container after the standard .workspace.py copies
approved files into /nyitsec-ctf. The ordinary decoys are intentionally
unrelated. One random regular document contains the requested case message.
"""

from pathlib import Path
import os
import pwd
import random
import stat

WORKSPACE = Path("/nyitsec-ctf")
CODE = "NYITSEC-LOST-26"

# Nine departments, four branches each, with varied depth.
BRANCHES = {
    "administration": ("schedules", "correspondence", "forms", "archive/2025"),
    "facilities": ("repairs", "inventory", "supplies", "archive/inspections"),
    "programs": ("workshops", "volunteers", "planning", "archive/2024"),
    "technology": ("helpdesk", "devices", "changes", "logs/desktop"),
    "operations": ("handoffs", "meetings", "requests", "archive/monthly"),
    "records": ("intake", "closed", "indexes", "audit/quarterly"),
    "communications": ("newsletters", "outreach", "flyers", "archive/drafts"),
    "finance": ("purchase-orders", "receipts", "forecasts", "archive/2023"),
    "research": ("surveys", "summaries", "planning", "archive/notes"),
}

FILENAMES = (
    "notes.txt", "summary.md", "daily.log",
    "handoff.txt", "index.txt", "status.txt",
    "tasks.csv", "draft.md",
)

SUBJECTS = (
    "Update workshop calendar",
    "Review routine equipment inventory",
    "Coordinate supplies for the next event",
    "Schedule volunteer orientation",
    "File ordinary meeting notes",
    "Prepare monthly status summary",
    "Follow up on general facility requests",
    "Check archived survey responses",
    "Organize documents for the team",
    "Review unresolved administrative questions",
)


def generate_archive(root: Path, rng=None, uid=None, gid=None) -> Path:
    """Generate varied file placements, returning the relative target path.

    An existing nonempty workspace is never modified or reset. Tests may
    supply a seeded random.Random, but live launches use SystemRandom.
    """
    root = Path(root)
    if not root.is_absolute() or root.is_symlink() or not root.is_dir():
        raise ValueError("Expected an existing, real absolute workspace directory")
    if any(root.iterdir()):
        raise FileExistsError("Refusing to modify a populated workspace")

    rng = rng if rng is not None else random.SystemRandom()
    documents = []

    for department, subfolders in BRANCHES.items():
        for subfolder in subfolders:
            folder = root / department / subfolder
            folder.mkdir(mode=0o700, parents=True)
            filenames = rng.sample(FILENAMES, 3)
            for filename in filenames:
                path = folder / filename
                subject = rng.choice(SUBJECTS)
                reference = f"R-{rng.randrange(1000, 9999)}"
                label = rng.choice(("Ticket", "Case", "Request", "Reference"))
                lines = [
                    f"Subject: {subject}",
                    f"Department: {department}",
                    f"{label}: {reference}",
                    f"Status: {rng.choice(('Closed', 'Filed', 'Pending', 'Reviewed'))}",
                    "This is a synthetic record for a community office.",
                    "No additional action is required for this ordinary record.",
                    "",
                ]
                path.write_text("\n".join(lines), encoding="utf-8")
                documents.append(path)

    chosen = rng.choice(documents)
    with chosen.open("a", encoding="utf-8") as handle:
        handle.write(
            "\n--- Archived investigation note ---\n"
            "NYITSec case review: a forgotten record was located.\n"
            f"Recovered code: {CODE}\n"
            "This is a fictional training message.\n"
        )

    # The initializer runs as root. Make the entire output tree writable by
    # the normal hacker user, without inheriting setuid or executable modes.
    for path in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        mode = 0o700 if path.is_dir() else 0o600
        path.chmod(mode)
        if uid is not None and gid is not None:
            os.chown(path, uid, gid)

    return chosen.relative_to(root)


def main():
    account = pwd.getpwnam("hacker")
    generate_archive(WORKSPACE, uid=account.pw_uid, gid=account.pw_gid)
    # Never print the random target location or answer in startup messages.
    print("NYITSec: fictional archive prepared for searching.")


if __name__ == "__main__":
    main()
