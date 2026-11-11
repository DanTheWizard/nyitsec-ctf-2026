#!/bin/sh
# Prepare the offline Git executable for the duration of this CTF container.
set -eu

chmod 600 /challenge/.history-builder.py /challenge/README.md \
    /challenge/.git-prepare.sh /challenge/.git-runtime.tar.gz

if [ -e /run/nyitsec-git ]; then
    echo "NYITSec: Git runtime path already exists" >&2
    exit 1
fi
mkdir -m 755 /run/nyitsec-git
tar -xzf /challenge/.git-runtime.tar.gz -C /run/nyitsec-git
test -x /run/nyitsec-git/git
/challenge/bin/git --version
