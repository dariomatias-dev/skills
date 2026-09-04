#!/usr/bin/env python3
"""Validate the plugin marketplace manifest and every technology's plugin manifest.

Checks, mirroring what `claude plugin validate` enforces plus this repo's own
authoring rules from CONTRIBUTING.md:

- marketplace.json parses and every listed plugin's source directory exists.
- Each <technology>/.claude-plugin/plugin.json parses and has the required fields.
- Every SKILL.md under a technology folder is discovered by "skills": ["./"].
- A skill's folder name matches the `name:` field in its own frontmatter.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    global had_failure
    had_failure = True


had_failure = False


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"{path.relative_to(ROOT)}: file not found")
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)}: invalid JSON ({exc})")
    return None


def frontmatter_name(skill_md: Path) -> str | None:
    text = skill_md.read_text(encoding="utf-8")
    match = re.search(r"^name:\s*(\S+)\s*$", text, re.MULTILINE)
    return match.group(1) if match else None


def check_plugin(technology_dir: Path) -> None:
    plugin_json = technology_dir / ".claude-plugin" / "plugin.json"
    data = load_json(plugin_json)
    if data is None:
        return

    for field in ("name", "version", "description", "skills"):
        if field not in data:
            fail(f"{plugin_json.relative_to(ROOT)}: missing required field '{field}'")

    skill_dirs = sorted(
        p.parent for p in technology_dir.glob("*/SKILL.md")
    )
    if not skill_dirs:
        fail(f"{technology_dir.relative_to(ROOT)}: no SKILL.md found under this plugin")

    for skill_dir in skill_dirs:
        name = frontmatter_name(skill_dir / "SKILL.md")
        if name is None:
            fail(f"{skill_dir.relative_to(ROOT)}/SKILL.md: no 'name:' field in frontmatter")
        elif name != skill_dir.name:
            fail(
                f"{skill_dir.relative_to(ROOT)}/SKILL.md: "
                f"frontmatter name '{name}' does not match folder name '{skill_dir.name}'"
            )


def main() -> int:
    marketplace_json = ROOT / ".claude-plugin" / "marketplace.json"
    marketplace = load_json(marketplace_json)
    if marketplace is not None:
        for plugin in marketplace.get("plugins", []):
            source = plugin.get("source")
            if not source:
                fail(f"{marketplace_json.relative_to(ROOT)}: plugin entry missing 'source'")
                continue
            technology_dir = (ROOT / source).resolve()
            if not technology_dir.is_dir():
                fail(
                    f"{marketplace_json.relative_to(ROOT)}: "
                    f"source '{source}' does not resolve to a directory"
                )
                continue
            check_plugin(technology_dir)

    if had_failure:
        return 1

    print("OK: marketplace and plugin manifests are consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
