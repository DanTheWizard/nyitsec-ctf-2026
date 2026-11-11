# Git executable for the NYITSec history lab

A **genuine Git command-line executable**, obtained from Ubuntu 24.04's
`git` package, is bundled so the isolated pwn.college environment does
not depend on a system installation or internet access.

The one-time packaging script is `tools/build_forgotten_git_runtime.py`.
It copies the Ubuntu Git executable and relevant non-glibc shared libraries.
Bundled library paths are listed in
`level-3/forgotten-commit/.git-runtime-packages.txt`.

Git is free software licensed under the GNU General Public License,
version 2. Bundled runtime libraries may have different licenses.
Distributors should retain the necessary notices and provide applicable
sources as required by those licenses.

Useful upstream sources:
- Git source repository: https://github.com/git/git
- Git software license information: https://git-scm.com/about/free-and-open-source
- Ubuntu Git package/source: https://launchpad.net/ubuntu/+source/git
- Ubuntu package license documentation: https://packages.ubuntu.com/

Students run the real command via `/challenge/bin/git` with a temporary
read-only-ish executable extraction at `/run/nyitsec-git`. Runtime execution
does not install anything or require network access.
