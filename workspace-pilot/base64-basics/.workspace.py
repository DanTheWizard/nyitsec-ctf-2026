#!/usr/local/bin/python
"""Copy lab assets into a disposable, student-owned /nyitsec-ctf directory.

Only used by NYITSec Workspace Pilot challenges. This script runs as root via
/challenge/.init; never follow source symlinks or overwrite an existing target.
It does not grant any extra privileges to the student's copied files.
"""

import fnmatch
import os
from pathlib import Path
import pwd
import shutil
import stat

SOURCE = Path("/challenge")
TARGET = Path("/nyitsec-ctf")

# These mandatory exclusions apply even if .ctfignore is missing/modified.
# Never copy privileged executables, author notes, or setup implementation.
PROTECTED_NAMES = frozenset({
    ".init", ".workspace.py", ".ctfignore",
    "verify", "bin", "README.md", "DESCRIPTION.md",
})


def load_patterns(source):
    """Read extra, simple .gitignore-like exclusions (no negation rules)."""
    path = source / ".ctfignore"
    if path.is_symlink():
        raise ValueError("The ignore configuration cannot be a symlink")
    if not path.is_file():
        return []
    patterns = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        item = raw.strip()
        if item and not item.startswith("#"):
            if item.startswith("!") or item.startswith("/") or ".." in item.split("/"):
                raise ValueError("Invalid exclusion pattern: " + item)
            patterns.append(item)
    return patterns


def excluded(relative, patterns):
    """Check mandatory names, then simple name/path wildcard exclusions."""
    parts = relative.parts
    if any(part in PROTECTED_NAMES for part in parts):
        return True
    value = relative.as_posix()
    for pattern in patterns:
        if pattern.endswith("/"):
            prefix = pattern.rstrip("/")
            if value == prefix or value.startswith(prefix + "/"):
                return True
        elif "/" in pattern:
            if fnmatch.fnmatchcase(value, pattern):
                return True
        elif any(fnmatch.fnmatchcase(p, pattern) for p in parts):
            return True
    return False


def prepare_workspace(source, destination, uid=None, gid=None):
    """Stage regular data files, stripping source permissions and symlinks.

    Destination must not already exist. This refuses destructive cleanup:
    each new pwn.college challenge container starts with a fresh root filesystem.
    uid/gid may be None for offline tests run as the current user.
    """
    source = Path(source)
    destination = Path(destination)
    if not destination.is_absolute() or str(destination) == "/":
        raise ValueError("Destination must be a non-root absolute path")
    if not source.is_dir() or source.is_symlink():
        raise ValueError("Source must be a real challenge directory")
    if os.path.lexists(destination):
        raise FileExistsError("Refusing to overwrite existing workspace: " + str(destination))

    patterns = load_patterns(source)
    destination.mkdir(mode=0o700)
    copied = []

    def chown_if_requested(path):
        if uid is not None and gid is not None:
            os.chown(path, uid, gid)

    def populate(folder, relative):
        for entry in sorted(os.scandir(folder), key=lambda e: e.name):
            item = relative / entry.name
            if excluded(item, patterns) or entry.is_symlink():
                continue
            output = destination / item
            if entry.is_dir(follow_symlinks=False):
                output.mkdir(mode=0o700)
                populate(entry.path, item)
                os.chmod(output, 0o700)
                chown_if_requested(output)
            elif entry.is_file(follow_symlinks=False):
                # Regular files only; do not preserve setuid bits or owner.
                with open(entry.path, "rb") as source_file, open(output, "xb") as target_file:
                    shutil.copyfileobj(source_file, target_file)
                os.chmod(output, 0o600)
                chown_if_requested(output)
                copied.append(item.as_posix())
            # Symlinks, devices, sockets, and other special files are not staged.

    populate(source, Path())
    os.chmod(destination, 0o700)
    chown_if_requested(destination)
    return copied


def main():
    hacker = pwd.getpwnam("hacker")
    files = prepare_workspace(SOURCE, TARGET, hacker.pw_uid, hacker.pw_gid)
    print("NYITSec pilot workspace:", TARGET)
    print("Staged:", ", ".join(files) if files else "(no files)")


if __name__ == "__main__":
    main()
