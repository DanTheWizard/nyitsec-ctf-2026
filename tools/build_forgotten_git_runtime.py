#!/usr/bin/env python3
"""Bundle Ubuntu's genuine Git executable and non-glibc dependencies offline."""

from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "level-3" / "forgotten-commit"
EXCLUDED = (
    "libc.so", "libm.so", "libpthread.so", "libdl.so",
    "libresolv.so", "librt.so", "ld-linux", "linux-vdso",
)


def main():
    binary = shutil.which("git")
    if binary is None:
        raise SystemExit("Git must be installed on the Ubuntu packaging runner")
    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp)
        (stage / "lib").mkdir()
        (stage / "libexec").mkdir()
        (stage / "templates").mkdir()
        shutil.copy2(binary, stage / "git")
        libraries = []
        for line in subprocess.check_output(["ldd", binary], text=True).splitlines():
            match = re.search(r"(?:=>\s*)?(/[^ ]+)", line)
            if not match:
                continue
            dependency = Path(match.group(1))
            if not dependency.is_file() or dependency.name.startswith(EXCLUDED):
                continue
            shutil.copyfile(dependency, stage / "lib" / dependency.name)
            libraries.append((dependency.name, str(dependency)))
        if not libraries:
            raise AssertionError("Expected at least one non-glibc Git library")
        archive = OUT / ".git-runtime.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(stage / "git", arcname="git")
            for item in sorted((stage / "lib").iterdir()):
                tar.add(item, arcname="lib/" + item.name)
            tar.add(stage / "templates", arcname="templates")
            tar.add(stage / "libexec", arcname="libexec")
        (OUT / ".git-runtime-packages.txt").write_text(
            "Ubuntu 24.04 Git portable runtime\n"
            + "Source executable: " + binary + "\n"
            + "".join(f"{name}\t{source}\n" for name, source in sorted(libraries)),
            encoding="utf-8",
        )
        print(f"Built {archive} ({archive.stat().st_size} bytes)")
        print(f"Included {len(libraries)} shared libraries")


if __name__ == "__main__":
    main()
