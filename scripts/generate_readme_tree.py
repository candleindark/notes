#!/usr/bin/env python3
"""Generate a tree of notes for README.md.

Walks the repository's subfolders, collects every Markdown note, and renders a
nested tree where each note is shown by its title (the first level-1 heading,
falling back to the file name) linked to the corresponding file. The rendered
tree is written into README.md between the TREE:START and TREE:END markers.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import quote

REPO_ROOT = Path(__file__).resolve().parent.parent
README = REPO_ROOT / "README.md"

START_MARKER = "<!-- TREE:START -->"
END_MARKER = "<!-- TREE:END -->"

# Directories that should never be scanned for notes.
EXCLUDED_DIRS = {".git", ".idea", "scripts", ".github"}

INDENT = "  "

_H1 = re.compile(r"^#\s+(.*\S)\s*$")


def note_title(path: Path) -> str:
    """Return the note's title: its first H1, or its file stem as a fallback."""
    try:
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                match = _H1.match(line)
                if match:
                    return match.group(1)
    except OSError:
        pass
    return path.stem


def folder_title(name: str) -> str:
    """Turn a directory name into a display title, e.g. 'ai_usage' -> 'Ai Usage'."""
    return name.replace("_", " ").replace("-", " ").title()


def link(path: Path) -> str:
    """A Markdown link to a note, relative to the repo root, URL-encoded."""
    rel = path.relative_to(REPO_ROOT).as_posix()
    href = "/".join(quote(part) for part in rel.split("/"))
    return f"[{note_title(path)}]({href})"


def render(directory: Path, depth: int) -> list[str]:
    """Render `directory`'s subdirectories and notes as indented list items.

    Files at the repository root (depth 0) are intentionally skipped: only the
    contents of subfolders are listed.
    """
    lines: list[str] = []
    entries = sorted(
        directory.iterdir(), key=lambda p: (p.is_file(), p.name.lower())
    )
    for entry in entries:
        if entry.is_dir():
            if entry.name in EXCLUDED_DIRS:
                continue
            child_lines = render(entry, depth + 1)
            if not child_lines:
                continue
            lines.append(f"{INDENT * depth}- **{folder_title(entry.name)}**")
            lines.extend(child_lines)
        elif depth > 0 and entry.suffix == ".md":
            lines.append(f"{INDENT * depth}- {link(entry)}")
    return lines


def build_tree() -> str:
    lines = render(REPO_ROOT, 0)
    return "\n".join(lines) if lines else "_No notes yet._"


def main() -> int:
    text = README.read_text(encoding="utf-8")

    if START_MARKER not in text or END_MARKER not in text:
        raise SystemExit(
            f"README.md is missing the {START_MARKER} / {END_MARKER} markers."
        )

    tree = build_tree()
    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL
    )
    replacement = f"{START_MARKER}\n\n{tree}\n\n{END_MARKER}"
    updated = pattern.sub(lambda _: replacement, text)

    if updated != text:
        README.write_text(updated, encoding="utf-8")
        print("README.md tree updated.")
    else:
        print("README.md tree already up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
