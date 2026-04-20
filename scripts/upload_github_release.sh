#!/bin/zsh
set -euo pipefail

cd "$(dirname "$0")/.."

: "${GH_TOKEN:?请先设置 GH_TOKEN（GitHub Personal Access Token）}"
: "${RELEASE_TAG:?请先设置 RELEASE_TAG（例如 v1.1.1）}"

DMG_PATH="${DMG_PATH:-dist/contractG.dmg}"
TITLE="${TITLE:-contractG ${RELEASE_TAG}}"
NOTES="${NOTES:-macOS dmg release}"

if [ ! -f "$DMG_PATH" ]; then
  echo "找不到 DMG 文件：$DMG_PATH"
  exit 1
fi

if gh release view "$RELEASE_TAG" >/dev/null 2>&1; then
  gh release upload "$RELEASE_TAG" "$DMG_PATH" --clobber
else
  gh release create "$RELEASE_TAG" "$DMG_PATH" --title "$TITLE" --notes "$NOTES"
fi
