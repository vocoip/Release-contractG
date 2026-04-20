#!/bin/zsh
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON_BIN="${PYTHON_BIN:-python3}"

if [ ! -x "$(command -v "$PYTHON_BIN")" ]; then
  echo "找不到 Python 解释器: $PYTHON_BIN"
  exit 1
fi

if ! "$PYTHON_BIN" -c 'import sys; raise SystemExit(0 if (3,10) <= sys.version_info[:2] <= (3,12) else 2)'; then
  echo "Python 版本不受支持: $("$PYTHON_BIN" -c 'import sys; print(f\"{sys.version_info[0]}.{sys.version_info[1]}\")')"
  echo "请使用 Python 3.10 ~ 3.12（含边界）进行打包。"
  exit 1
fi

if [ -x ".venv/bin/python" ]; then
  VENV_PY_VER=$(.venv/bin/python -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')
  TARGET_PY_VER=$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')
  if [ "$VENV_PY_VER" != "$TARGET_PY_VER" ]; then
    rm -rf .venv
  fi
fi

if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
fi

source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt

export PYINSTALLER_CONFIG_DIR="$PWD/.pyinstaller-cache"

python - <<'PY'
import shutil
from pathlib import Path
for name in ("build", "dist", ".pyinstaller-cache"):
    p = Path(name)
    if p.exists():
        shutil.rmtree(p)
PY

pyinstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name contractG \
  --add-data "resources:resources" \
  --add-data "src/assets:src/assets" \
  src/launcher.py

rm -f "dist/contractG.dmg"
hdiutil create \
  -volname "contractG" \
  -srcfolder "dist/contractG.app" \
  -ov \
  -format UDZO \
  "dist/contractG.dmg"
