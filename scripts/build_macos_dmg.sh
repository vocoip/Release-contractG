#!/bin/zsh
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON_BIN="${PYTHON_BIN:-python3}"
SIGN_IDENTITY="${SIGN_IDENTITY:-}"
NOTARY_PROFILE="${NOTARY_PROFILE:-}"
NOTARY_KEY_PATH="${NOTARY_KEY_PATH:-}"
NOTARY_KEY_ID="${NOTARY_KEY_ID:-}"
NOTARY_ISSUER="${NOTARY_ISSUER:-}"

if [ ! -x "$(command -v "$PYTHON_BIN")" ]; then
  echo "找不到 Python 解释器: $PYTHON_BIN"
  exit 1
fi

if ! "$PYTHON_BIN" -c 'import sys; raise SystemExit(0 if (3,10) <= sys.version_info[:2] <= (3,12) else 2)'; then
  echo "Python 版本不受支持: $("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
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

VENV_PY="$PWD/.venv/bin/python3"
if [ ! -x "$VENV_PY" ]; then
  echo "虚拟环境 Python 不存在: $VENV_PY"
  exit 1
fi

"$VENV_PY" -m pip install -U pip
"$VENV_PY" -m pip install -r requirements.txt

export PYINSTALLER_CONFIG_DIR="$PWD/.pyinstaller-cache"

rm -rf build dist .pyinstaller-cache || true

"$VENV_PY" -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name contractG \
  --add-data "resources:resources" \
  --add-data "src/assets:src/assets" \
  src/launcher.py

if [ -z "$SIGN_IDENTITY" ]; then
  SIGN_IDENTITY="$(security find-identity -v -p codesigning 2>/dev/null | awk -F '\"' '/Developer ID Application:/{print $2; exit}')"
fi

if [ -n "$SIGN_IDENTITY" ]; then
  echo "使用签名证书: $SIGN_IDENTITY"
  codesign --force --deep --timestamp --options runtime --sign "$SIGN_IDENTITY" "dist/contractG.app"
  codesign --verify --deep --strict --verbose=2 "dist/contractG.app"
  spctl -a -vv "dist/contractG.app" || true
else
  echo "未找到可用的 Developer ID Application 证书，将跳过签名"
fi

notary_submit_with_retry() {
  local target="$1"
  shift
  local attempt=1
  local max_attempts=3
  while true; do
    if xcrun notarytool submit "$target" "$@" --wait; then
      return 0
    fi
    if [ "$attempt" -ge "$max_attempts" ]; then
      return 1
    fi
    attempt=$((attempt + 1))
    sleep $((attempt * 10))
  done
}

NOTARIZE_MODE=""
if [ -n "$NOTARY_PROFILE" ]; then
  NOTARIZE_MODE="profile"
elif [ -n "$NOTARY_KEY_PATH" ] && [ -n "$NOTARY_KEY_ID" ] && [ -n "$NOTARY_ISSUER" ] && [ -f "$NOTARY_KEY_PATH" ]; then
  NOTARIZE_MODE="api_key"
fi

if [ -n "$NOTARIZE_MODE" ]; then
  rm -f "dist/contractG.app.zip"
  ditto -c -k --keepParent "dist/contractG.app" "dist/contractG.app.zip"

  if [ "$NOTARIZE_MODE" = "profile" ]; then
    echo "开始公证 APP: $NOTARY_PROFILE"
    if ! notary_submit_with_retry "dist/contractG.app.zip" --keychain-profile "$NOTARY_PROFILE"; then
      echo "APP 公证失败，将跳过 stapler（可重试执行脚本）"
      NOTARIZE_MODE=""
    fi
  else
    echo "开始公证 APP: App Store Connect API Key"
    if ! notary_submit_with_retry "dist/contractG.app.zip" --key "$NOTARY_KEY_PATH" --key-id "$NOTARY_KEY_ID" --issuer "$NOTARY_ISSUER"; then
      echo "APP 公证失败，将跳过 stapler（可重试执行脚本）"
      NOTARIZE_MODE=""
    fi
  fi

  if [ -n "$NOTARIZE_MODE" ]; then
    xcrun stapler staple "dist/contractG.app"
    spctl -a -vv "dist/contractG.app" || true
  fi
fi

rm -f "dist/contractG.dmg"
rm -rf "dist/dmg_stage"
mkdir -p "dist/dmg_stage"
ditto "dist/contractG.app" "dist/dmg_stage/contractG.app"
ln -s "/Applications" "dist/dmg_stage/Applications"
hdiutil create \
  -volname "contractG" \
  -srcfolder "dist/dmg_stage" \
  -ov \
  -format UDZO \
  "dist/contractG.dmg"

if [ -n "$NOTARIZE_MODE" ]; then
  if [ "$NOTARIZE_MODE" = "profile" ]; then
    echo "开始公证 DMG: $NOTARY_PROFILE"
    if ! notary_submit_with_retry "dist/contractG.dmg" --keychain-profile "$NOTARY_PROFILE"; then
      echo "DMG 公证失败，将跳过 stapler（可重试执行脚本）"
      exit 0
    fi
  else
    echo "开始公证 DMG: App Store Connect API Key"
    if ! notary_submit_with_retry "dist/contractG.dmg" --key "$NOTARY_KEY_PATH" --key-id "$NOTARY_KEY_ID" --issuer "$NOTARY_ISSUER"; then
      echo "DMG 公证失败，将跳过 stapler（可重试执行脚本）"
      exit 0
    fi
  fi

  xcrun stapler staple "dist/contractG.dmg"
  xcrun stapler validate -v "dist/contractG.dmg"
else
  echo "未设置 NOTARY_PROFILE / NOTARY_KEY_PATH，跳过公证与 stapler"
fi
