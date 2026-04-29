#!/usr/bin/env python3
"""Install this skill into Claude Code and/or Codex skill directories."""

import argparse
import shutil
import sys
from pathlib import Path
from typing import Optional


SKILL_NAME = "synced-slides"
EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", "renders", "snapshots", ".waveform-cache", ".thumbnails"}
EXCLUDE_SUFFIXES = {".mp3", ".wav", ".m4a", ".mp4", ".mov", ".webm", ".swp", ".swo"}
EXCLUDE_NAMES = {".DS_Store", ".env"}


def source_root() -> Path:
    return Path(__file__).resolve().parents[1]


def should_ignore(path: Path) -> bool:
    if path.name in EXCLUDE_NAMES:
        return True
    if path.name in EXCLUDE_DIRS:
        return True
    if path.suffix.lower() in EXCLUDE_SUFFIXES:
        return True
    if path.name.endswith(".payload.json"):
        return True
    return False


def copy_skill(src: Path, dest: Path, force: bool) -> None:
    if dest.exists():
        if not force:
            raise SystemExit(f"Destination exists: {dest}. Re-run with --force to replace it.")
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    def ignore(directory: str, names: list[str]) -> set[str]:
        ignored = set()
        for name in names:
            candidate = Path(directory) / name
            if should_ignore(candidate):
                ignored.add(name)
        return ignored

    shutil.copytree(src, dest, ignore=ignore)
    print(f"Installed {SKILL_NAME} -> {dest}")


def claude_dest(scope: str, project_dir: Optional[Path]) -> Path:
    if scope == "personal":
        return Path.home() / ".claude" / "skills" / SKILL_NAME
    if not project_dir:
        project_dir = Path.cwd()
    return project_dir.resolve() / ".claude" / "skills" / SKILL_NAME


def codex_dest() -> Path:
    return Path.home() / ".codex" / "skills" / SKILL_NAME


def main() -> int:
    parser = argparse.ArgumentParser(description="Install synced-slides for Claude Code and/or Codex.")
    parser.add_argument("--target", choices=["claude", "codex", "both"], default="both")
    parser.add_argument("--scope", choices=["personal", "project"], default="personal", help="Claude Code install scope")
    parser.add_argument("--project-dir", type=Path, help="Project directory for --scope project")
    parser.add_argument("--force", action="store_true", help="Replace an existing installed skill")
    args = parser.parse_args()

    src = source_root()
    if not (src / "SKILL.md").exists():
        raise SystemExit(f"Could not find SKILL.md at {src}")

    targets: list[Path] = []
    if args.target in {"claude", "both"}:
        targets.append(claude_dest(args.scope, args.project_dir))
    if args.target in {"codex", "both"}:
        targets.append(codex_dest())

    for dest in targets:
        if src.resolve() == dest.resolve():
            print(f"Already installed at {dest}")
            continue
        copy_skill(src, dest, args.force)

    return 0


if __name__ == "__main__":
    sys.exit(main())
