#!/usr/bin/env bash
# Checks that every README translation keeps the same heading structure as the
# base README.md, per markdown-readme's rule: "Keep the section structure
# identical across versions. A translation that drifts structurally becomes
# impossible to review." Structure means the sequence of heading levels
# (## vs ###), not the translated text.
set -euo pipefail
cd "$(dirname "$0")/.."

base="README.md"
status=0

structure() {
  grep -oE '^#{2,3} ' "$1" | tr -d ' \n'
}

base_structure="$(structure "$base")"

for translation in README.*.md; do
  [[ "$translation" == "$base" ]] && continue
  translation_structure="$(structure "$translation")"

  if [[ "$translation_structure" != "$base_structure" ]]; then
    echo "FAIL: $translation heading structure differs from $base" >&2
    echo "  $base:       $base_structure" >&2
    echo "  $translation: $translation_structure" >&2
    status=1
  fi
done

if [[ $status -eq 0 ]]; then
  echo "OK: every README translation matches $base's heading structure"
fi

exit $status
