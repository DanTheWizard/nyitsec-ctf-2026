#!/usr/bin/env python3
"""Validate pwn.college YAML and the NYITSec challenge authoring convention."""

import argparse
from pathlib import Path
import stat
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
EXEMPT_MODULES = {"linux-cli-intro"}
EXECUTABLES = (".init", "verify", "bin/nyitsec-answer")
REQUIRED_FILES = (*EXECUTABLES, ".workspace.py", ".ctfignore", "DESCRIPTION.md", "README.md")
# The only approved per-challenge initialization extension currently supported.
WEB_INIT_SUFFIX = (b"\n# NYITSec challenge extension: web-service\n"
                   b"/bin/sh /challenge/.website-start.sh\n")
RANDOM_ARCHIVE_INIT_SUFFIX = (
    b"\n# NYITSec challenge extension: randomized-file-search\n"
    b"chmod 600 /challenge/.scatter.py\n"
    b"/usr/local/bin/python -I /challenge/.scatter.py\n"
)
DNS_INIT_SUFFIX = (
    b"\n# NYITSec challenge extension: local-dns-service\n"
    b"/bin/sh /challenge/.dns-start.sh\n"
)


class UniqueKeyLoader(yaml.SafeLoader):
    """Reject duplicate keys: plain PyYAML would silently keep the last one."""


def construct_unique_mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        if key in result:
            raise ValueError(f"Duplicate YAML key {key!r} on line {key_node.start_mark.line + 1}")
        result[key] = loader.construct_object(value_node, deep=True)
    return result


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_unique_mapping,
)


def read_yaml(path: Path):
    return yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)


def check_repository(root: Path) -> list[str]:
    errors = []
    dojo_file = root / "dojo.yml"
    try:
        dojo = read_yaml(dojo_file)
        if not isinstance(dojo, dict) or not isinstance(dojo.get("modules"), list):
            return ["dojo.yml must contain a 'modules' list"]
    except (OSError, yaml.YAMLError, ValueError) as exc:
        return [f"dojo.yml: {exc}"]

    ids = set()
    for item in dojo["modules"]:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            errors.append(f"Invalid module entry: {item!r}")
            continue
        mid = item["id"]
        if mid in ids:
            errors.append(f"Duplicate dojo module ID: {mid}")
        ids.add(mid)

        module_file = root / mid / "module.yml"
        try:
            module = read_yaml(module_file)
        except (OSError, yaml.YAMLError, ValueError) as exc:
            errors.append(f"{module_file.relative_to(root)}: {exc}")
            continue
        if not isinstance(module, dict):
            errors.append(f"{mid}/module.yml must be a YAML mapping")
            continue

        resources = module.get("resources", [])
        if not isinstance(resources, list):
            errors.append(f"{mid}/module.yml resources must be a list")
            continue
        for i, resource in enumerate(resources, 1):
            if (isinstance(resource, dict) and resource.get("type") == "markdown"
                    and not str(resource.get("content", "")).strip()):
                errors.append(f"{mid}/module.yml resource {i} has empty Markdown content")

        challenges = module.get("challenges", [])
        if not isinstance(challenges, list):
            errors.append(f"{mid}/module.yml challenges must be a list")
            continue
        seen = set()
        for ch in challenges:
            if not isinstance(ch, dict) or not isinstance(ch.get("id"), str):
                errors.append(f"Malformed challenge entry in {mid}/module.yml")
                continue
            cid = ch["id"]
            if cid in seen:
                errors.append(f"Duplicate challenge ID: {mid}/{cid}")
            seen.add(cid)
            if mid in EXEMPT_MODULES:
                # Leave pwn.college's original examples and ungraded lessons alone.
                continue

            folder = root / mid / cid
            for rel in REQUIRED_FILES:
                if not (folder / rel).is_file():
                    errors.append(f"{mid}/{cid}: missing {rel}; use scripts/new_challenge.py")
            for rel in EXECUTABLES:
                path = folder / rel
                if path.is_file() and not path.stat().st_mode & stat.S_IXUSR:
                    errors.append(f"{mid}/{cid}: {rel} must be executable (git mode 100755)")

            # Prevent drift from the tested writable workspace implementation.
            init = folder / ".init"
            worker = folder / ".workspace.py"
            for relative in (".init", ".workspace.py"):
                actual = folder / relative
                expected = ROOT / "templates" / "nyitsec-challenge" / relative
                if actual.is_file() and expected.is_file():
                    actual_data = actual.read_bytes()
                    expected_data = expected.read_bytes()
                    is_valid_web_extension = (
                        relative == ".init"
                        and actual_data == expected_data + WEB_INIT_SUFFIX
                        and (folder / ".website-start.sh").is_file()
                        and (folder / ".website.py").is_file()
                    )
                    is_valid_random_archive_extension = (
                        relative == ".init"
                        and actual_data == expected_data + RANDOM_ARCHIVE_INIT_SUFFIX
                        and (folder / ".scatter.py").is_file()
                        and ".scatter.py" in (
                            (folder / ".ctfignore").read_text(encoding="utf-8").splitlines()
                            if (folder / ".ctfignore").is_file() else []
                        )
                    )
                    is_valid_dns_extension = (
                        relative == ".init"
                        and actual_data == expected_data + DNS_INIT_SUFFIX
                        and (folder / ".dns-start.sh").is_file()
                        and (folder / ".dns-server.py").is_file()
                        and (folder / ".dig-runtime.tar.gz").is_file()
                        and (folder / "bin/dig").is_file()
                        and all(
                            item in (
                                (folder / ".ctfignore").read_text(encoding="utf-8").splitlines()
                                if (folder / ".ctfignore").is_file() else []
                            )
                            for item in (
                                ".dns-start.sh", ".dns-server.py",
                                ".dig-runtime.tar.gz", ".dig-runtime-packages.txt"
                            )
                        )
                    )
                    if (
                        actual_data != expected_data
                        and not is_valid_web_extension
                        and not is_valid_random_archive_extension
                        and not is_valid_dns_extension
                    ):
                        errors.append(
                            f"{mid}/{cid}: {relative} differs from standard template; "
                            "use scripts/new_challenge.py or update the shared template"
                        )
                elif not expected.is_file():
                    errors.append(f"Missing standard template file: {expected}")
            if init.is_file() and (
                "/challenge/.workspace.py" not in init.read_text(encoding="utf-8")
                or "/nyitsec-ctf" not in init.read_text(encoding="utf-8")
            ):
                errors.append(f"{mid}/{cid}: .init must prepare and open /nyitsec-ctf")
            if worker.is_file() and "PROTECTED_NAMES" not in worker.read_text(encoding="utf-8"):
                errors.append(f"{mid}/{cid}: .workspace.py must keep mandatory exclusions")

            desc = folder / "DESCRIPTION.md"
            if not desc.is_file():
                errors.append(f"{mid}/{cid}: missing DESCRIPTION.md")
            else:
                content = desc.read_text(encoding="utf-8")
                if "nyitsec-answer" not in content:
                    errors.append(f"{mid}/{cid}: student instructions must mention nyitsec-answer")
                if "/nyitsec-ctf" not in content:
                    errors.append(f"{mid}/{cid}: student instructions must mention /nyitsec-ctf")
                if "TODO" in content:
                    errors.append(f"{mid}/{cid}: replace TODO markers in DESCRIPTION.md")

            verifier = folder / "verify"
            if verifier.is_file():
                v = verifier.read_text(encoding="utf-8")
                if not v.startswith("#!/usr/bin/exec-suid"):
                    errors.append(f"{mid}/{cid}: verify should use the pwn.college exec-suid shebang")
                if "TODO" in v:
                    errors.append(f"{mid}/{cid}: implement and remove TODO in verify")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()

    errors = check_repository(args.root.resolve())
    if errors:
        for message in errors:
            print(f"ERROR: {message}", file=sys.stderr)
        return 1
    print("NYITSec dojo configuration and challenge conventions: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
