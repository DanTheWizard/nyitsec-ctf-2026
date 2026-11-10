# Bundled steghide runtime: provenance and licenses

This challenge includes a redistributable runtime bundle built using the standard
Ubuntu 24.04 packages for **steghide** and its non-glibc shared library dependencies.
The archive is extracted and run *without root permissions* by the
`/challenge/bin/steghide` wrapper. It is not part of the student-facing data.

Steghide is third-party free software licensed under the GNU GPL. This repository
does not claim authorship of it or of the runtime libraries. The tool and its
dependencies are installed using Ubuntu's distribution packages by
`tools/build_stego_photo.py` in an Ubuntu 24.04 build environment.

Upstream source and license references:
- Steghide project: https://steghide.sourceforge.net/
- Ubuntu package source: https://launchpad.net/ubuntu/+source/steghide
- Debian steghide sources: https://sources.debian.org/src/steghide/
- Ubuntu package source index: https://packages.ubuntu.com/

When distributing or rebuilding the archive, use the corresponding distribution
source packages and adhere to each included package's license terms. If distributing
binaries to third parties, make the complete matching source code available through
a compliant distribution mechanism.

To build the training artifacts with an already-installed steghide binary:
```bash
python3 -m pip install pillow
python3 tools/build_stego_photo.py
```

The build tool verifies extraction after embedding. CI subsequently verifies
extraction with the bundled nonprivileged command. This package is solely for
authorized, fictional training; it has no network activity.
