#!/usr/bin/env python3
"""Build a portable ISC dig runtime from distribution packages (officer tool)."""

from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "level-3" / "dns-treasure-hunt"
EXCLUDED_PREFIXES = (
    "libc.so", "libm.so", "libpthread.so", "libdl.so",
    "libresolv.so", "librt.so", "ld-linux", "linux-vdso",
)


def main() -> None:
    binary = shutil.which("dig")
    if not binary:
        raise RuntimeError("Install the Ubuntu bind9-dnsutils package before building")
    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp)
        libs = stage / "lib"
        libs.mkdir()
        shutil.copy2(binary, stage / "dig")
        lines = subprocess.check_output(["ldd", binary], text=True).splitlines()
        bundled = {}
        for line in lines:
            match = re.search(r"(?:=>\s*)?(/[^ ]+)", line)
            if not match:
                continue
            real = Path(match.group(1))
            if not real.is_file() or real.name.startswith(EXCLUDED_PREFIXES):
                continue
            shutil.copyfile(real, libs / real.name)
            bundled[real.name] = str(real)
        if not bundled:
            raise AssertionError("No dig shared libraries were discovered")

        archive = OUT / ".dig-runtime.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(stage / "dig", arcname="dig")
            for file in sorted(libs.iterdir()):
                tar.add(file, arcname="lib/" + file.name)

        packages = []
        packages.append("ISC dig from Ubuntu 24.04 bind9-dnsutils\n")
        packages.append("Build-time binary: " + binary + "\n")
        packages.append("Bundled library paths (transitive ldd results):\n")
        packages.extend(f"{name}\t{path}\n" for name, path in sorted(bundled.items()))
        (OUT / ".dig-runtime-packages.txt").write_text(
            "".join(packages), encoding="utf-8"
        )
        print("Created", archive, archive.stat().st_size, "bytes")
        print("Bundled", len(bundled), "shared libraries")


if __name__ == "__main__":
    main()
