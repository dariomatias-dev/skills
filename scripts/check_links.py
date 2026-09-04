#!/usr/bin/env python3
"""Check that every local markdown link resolves to a real file or directory.

markdown-readme's own anti-patterns list this exact failure: "Links to
sections that were renamed, which break silently." This script catches the
file/directory half of that (a renamed or moved target); it does not resolve
`#anchor` fragments, since GitHub's anchor algorithm is not worth reimplementing
here and a wrong anchor still lands on the right page.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
LINK_PATTERN = re.compile(r"\]\(([^)]+)\)")


def is_external(target: str) -> bool:
    scheme = urlsplit(target).scheme
    return scheme in ("http", "https", "mailto")


def main() -> int:
    had_failure = False

    for md_file in sorted(ROOT.rglob("*.md")):
        if any(part in (".git", "node_modules") for part in md_file.parts):
            continue

        text = md_file.read_text(encoding="utf-8")
        for match in LINK_PATTERN.finditer(text):
            target = match.group(1).strip()

            if not target or target.startswith("#") or is_external(target):
                continue

            path_part = target.split("#", 1)[0]
            resolved = (md_file.parent / path_part).resolve()

            if not resolved.exists():
                print(
                    f"FAIL: {md_file.relative_to(ROOT)}: "
                    f"link target '{target}' does not exist "
                    f"(resolved to {resolved.relative_to(ROOT) if ROOT in resolved.parents or resolved == ROOT else resolved})",
                    file=sys.stderr,
                )
                had_failure = True

    if had_failure:
        return 1

    print("OK: every local markdown link resolves")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
