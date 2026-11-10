#!/usr/bin/env python3
"""Generate NYITSec challenges with a writable, disposable /nyitsec-ctf workspace."""

import argparse
from pathlib import Path
import re
import shutil
import stat

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = PROJECT_ROOT / "templates" / "nyitsec-challenge"
RESERVED_MODULES = {"linux-cli-intro"}
SLUG_RE = re.compile(r"^[a-z][a-z0-9-]*$")


def load_yaml(path: Path):
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return data


def save_yaml(path: Path, data) -> None:
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=1000),
        encoding="utf-8",
    )


def create_challenge(root: Path, module_id: str, challenge_id: str,
                     title: str, new_module_name: str | None = None) -> Path:
    for label, value in [("module", module_id), ("challenge", challenge_id)]:
        if not SLUG_RE.fullmatch(value):
            raise ValueError(f"Invalid {label} ID {value!r}. Use lowercase letters, numbers, and hyphens.")

    if module_id in RESERVED_MODULES:
        raise ValueError("The ungraded Linux & CLI introduction does not accept challenges.")

    dojo_file = root / "dojo.yml"
    dojo = load_yaml(dojo_file)
    if not isinstance(dojo.get("modules"), list):
        raise ValueError("dojo.yml must have a modules list")

    module_dir = root / module_id
    module_file = module_dir / "module.yml"
    target = module_dir / challenge_id

    if target.exists():
        raise FileExistsError(f"Challenge already exists: {target}")

    if module_file.exists():
        if new_module_name:
            raise ValueError("Module already exists; omit --new-module-name")
        module = load_yaml(module_file)
        if module.get("challenges") is None:
            raise ValueError("This module does not have a challenges list")
        if not isinstance(module["challenges"], list):
            raise ValueError("Module's challenges must be a list")
    else:
        if module_dir.exists():
            raise ValueError(f"Directory exists without module.yml: {module_dir}")
        if not new_module_name:
            raise ValueError("New module requires --new-module-name")
        if any(m.get("id") == module_id for m in dojo["modules"] if isinstance(m, dict)):
            raise ValueError(f"Module ID is already registered: {module_id}")
        module = {"name": new_module_name, "challenges": []}

    if any(ch.get("id") == challenge_id for ch in module["challenges"]
           if isinstance(ch, dict)):
        raise ValueError(f"Challenge ID already registered: {challenge_id}")

    for name in [".init", ".workspace.py", ".ctfignore", "verify", "bin/nyitsec-answer", "DESCRIPTION.md", "README.md"]:
        if not (TEMPLATE / name).is_file():
            raise FileNotFoundError(f"Missing NYITSec template file: {name}")

    # The template is the single place to change defaults for future challenges.
    shutil.copytree(TEMPLATE, target)
    for path in target.rglob("*"):
        if path.is_file():
            content = path.read_text(encoding="utf-8")
            content = (content.replace("{{CHALLENGE_TITLE}}", title)
                              .replace("{{MODULE_ID}}", module_id)
                              .replace("{{CHALLENGE_ID}}", challenge_id))
            path.write_text(content, encoding="utf-8")

    # chmod explicitly because Windows checkouts may lose Unix file-mode bits.
    for relative in [".init", "verify", "bin/nyitsec-answer"]:
        executable = target / relative
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    module["challenges"].append({"id": challenge_id, "name": title})
    module_dir.mkdir(parents=True, exist_ok=True)
    save_yaml(module_file, module)

    if new_module_name:
        (module_dir / "DESCRIPTION.md").write_text(
            f"# {new_module_name}\n\nNYITSec cybersecurity training challenges.\n",
            encoding="utf-8",
        )
        # Keep the optional CLI reading module first; append future CTF modules.
        dojo["modules"].append({"id": module_id})
        save_yaml(dojo_file, dojo)

    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", required=True, help="Existing or new module ID")
    parser.add_argument("--id", required=True, help="New challenge ID (lowercase, hyphens)")
    parser.add_argument("--name", required=True, help="Student-facing challenge name")
    parser.add_argument("--new-module-name", help="Create the module as well")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT,
                        help=argparse.SUPPRESS)
    args = parser.parse_args()

    try:
        target = create_challenge(
            args.root.resolve(), args.module, args.id,
            args.name, args.new_module_name,
        )
    except (ValueError, FileNotFoundError, FileExistsError) as exc:
        parser.error(str(exc))

    print(f"Created {target}")
    print("NEXT: implement verify.is_correct(), edit DESCRIPTION.md, and run validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
