#!/usr/bin/env bash
# The local gate: runs exactly what CI runs, so a green run here means a green
# pipeline. See flutter-ci's own "One gate, two places" rule, which this
# script follows for the skills repository itself.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== Manifest and plugin consistency =="
python3 scripts/check_manifests.py

echo
echo "== Skill frontmatter (Agent Skills spec) =="
status=0
while IFS= read -r -d '' skill_md; do
  skill_dir="$(dirname "$skill_md")"
  if ! npx --yes skills-ref validate "$skill_dir" >/tmp/skills-ref-out 2>&1; then
    cat /tmp/skills-ref-out >&2
    status=1
  fi
done < <(find flutter markdown -mindepth 2 -maxdepth 2 -name SKILL.md -print0)
if [[ $status -eq 0 ]]; then
  echo "OK: every SKILL.md validates against the Agent Skills spec"
else
  exit 1
fi

echo
echo "== README translation structure =="
./scripts/check_readme_locales.sh

echo
echo "== Local markdown links =="
python3 scripts/check_links.py

echo
echo "All checks passed."
