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

# 生成 app bundle 图标：以运行时使用的 resources/icon.ico 作为唯一图标源，
# 转换出 .icns 交给 PyInstaller，确保启动前（Finder/Dock）与启动后图标一致。
ICON_SRC="resources/icon.ico"
ICON_ICNS="resources/icon.icns"
ICON_ARG=""
if [ -f "$ICON_SRC" ] && command -v iconutil >/dev/null 2>&1; then
  echo "由 $ICON_SRC 生成 $ICON_ICNS"
  TMP_ICONS=$(mktemp -d)
  "$VENV_PY" - "$ICON_SRC" "$TMP_ICONS" <<'PY'
import sys
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
image = Image.open(src).convert("RGBA")
for size in (16, 32, 64, 128, 256, 512, 1024):
    image.resize((size, size), Image.LANCZOS).save(f"{out}/{size}.png")
PY
  ICONSET="$TMP_ICONS/icon.iconset"
  mkdir -p "$ICONSET"
  cp "$TMP_ICONS/16.png"   "$ICONSET/icon_16x16.png"
  cp "$TMP_ICONS/32.png"   "$ICONSET/icon_16x16@2x.png"
  cp "$TMP_ICONS/32.png"   "$ICONSET/icon_32x32.png"
  cp "$TMP_ICONS/64.png"   "$ICONSET/icon_32x32@2x.png"
  cp "$TMP_ICONS/128.png"  "$ICONSET/icon_128x128.png"
  cp "$TMP_ICONS/256.png"  "$ICONSET/icon_128x128@2x.png"
  cp "$TMP_ICONS/256.png"  "$ICONSET/icon_256x256.png"
  cp "$TMP_ICONS/512.png"  "$ICONSET/icon_256x256@2x.png"
  cp "$TMP_ICONS/512.png"  "$ICONSET/icon_512x512.png"
  cp "$TMP_ICONS/1024.png" "$ICONSET/icon_512x512@2x.png"
  iconutil -c icns "$ICONSET" -o "$ICON_ICNS"
  rm -rf "$TMP_ICONS"
  ICON_ARG="--icon $ICON_ICNS"
fi

"$VENV_PY" -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name contractG \
  ${=ICON_ARG} \
  --add-data "resources:resources" \
  --add-data "src/assets:src/assets" \
  src/launcher.py

# 精简未使用的 Qt 框架：PyQt5 的 hook 会打包整个 Qt5 lib 及全部插件，其中多数本应用并不需要。
# 原则：只删除可证明未被引用的内容，绝不按固定清单硬删——例如 cocoa 平台插件 libqcocoa.dylib
# 依赖 QtDBus/QtPrintSupport，误删会导致启动时 QGuiApplicationPrivate::createPlatformIntegration 崩溃。
APP_BUNDLE="dist/contractG.app"
QT_LIB_DIR="$APP_BUNDLE/Contents/Frameworks/PyQt5/Qt5/lib"
QT_PLUGIN_DIR="$APP_BUNDLE/Contents/Resources/PyQt5/Qt5/plugins"
if [ -d "$QT_LIB_DIR" ]; then
  # 1) 删除应用不会使用的平台插件（webgl），它会连带引用 QtQuick/QtQml/QtNetwork 等重型框架
  rm -f "$QT_PLUGIN_DIR"/platforms/libqwebgl.dylib 2>/dev/null || true

  # 2) 依赖分析：删除在 bundle 内（排除 Qt5/lib 自身）无任何二进制引用的框架
  referenced="$(
    find "$APP_BUNDLE/Contents" -path "$QT_LIB_DIR" -prune -o -type f \
      \( -name '*.so' -o -name '*.dylib' -o -perm -111 \) -print0 2>/dev/null \
      | xargs -0 otool -L 2>/dev/null | awk '/^\t/{print $1}' | sort -u || true
  )"
  for meta in "$QT_LIB_DIR"/*.framework; do
    [ -d "$meta" ] || continue
    name="$(basename "$meta" .framework)"
    if printf '%s\n' "$referenced" | grep -qxE "(@rpath/|.*/)$name"; then
      echo "保留 Qt 框架: $name"
    else
      rm -rf "$meta"
      echo "裁剪 Qt 框架: $name"
    fi
  done

  # 3) 清理因删除框架而悬空的转发符号链接（否则 codesign --deep 会报 No such file or directory）
  find "$APP_BUNDLE" -type l ! -exec test -e {} \; -delete 2>/dev/null || true

  # 4) 校验：确保剩余二进制引用的 Qt 框架均存在，否则中止构建，避免产出启动即崩溃的包
  post_refs="$(
    find "$APP_BUNDLE/Contents" -type f \( -name '*.so' -o -name '*.dylib' -o -perm -111 \) -print0 2>/dev/null \
      | xargs -0 otool -L 2>/dev/null | awk '/^\t/{print $1}' | sort -u || true
  )"
  missing=""
  for dep in ${(f)post_refs}; do
    case "$dep" in
      @rpath/*) n="${dep#@rpath/}" ;;
      *) continue ;;
    esac
    printf '%s' "$n" | grep -qE '^Qt[A-Za-z]+$' || continue
    [ -e "$QT_LIB_DIR/$n.framework" ] || missing="$missing $n"
  done
  if [ -n "$missing" ]; then
    echo "构建校验失败：以下被引用的 Qt 框架已缺失 ->$missing" >&2
    exit 1
  fi
  echo "Qt 框架精简完成"
fi

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

if hdiutil create \
  -volname "contractG" \
  -srcfolder "dist/dmg_stage" \
  -ov \
  -format UDZO \
  "dist/contractG.dmg" 2>/dev/null; then
  echo "DMG 生成完成（hdiutil create）"
else
  # 回退：受限环境（如沙箱）禁止对裸设备 /dev/rdisk* 写入，hdiutil create 不可用。
  # makehybrid 纯用户态构建 HFS+，无需设备访问；但它会把 HFS+ 目录记录中的 FinderInfo
  # 物化为 com.apple.FinderInfo xattr，挂载后导致 codesign --strict 报
  # "resource fork, Finder information, or similar detritus not allowed"。
  # 因此需以读写方式挂载到可写的挂载点（不能用只读的 /Volumes），清除该 xattr 后再压缩。
  echo "hdiutil create 不可用，改用 makehybrid 回退方案"
  rm -f "dist/contractG_raw.dmg"
  rm -rf "dist/cg_mnt"
  mkdir -p "dist/cg_mnt"
  hdiutil makehybrid -hfs -hfs-volume-name "contractG" -o "dist/contractG_raw.dmg" "dist/dmg_stage"
  hdiutil attach "dist/contractG_raw.dmg" -mountpoint "dist/cg_mnt" -nobrowse >/dev/null
  xattr -cr "dist/cg_mnt/contractG.app"
  for i in 1 2 3; do
    hdiutil detach "dist/cg_mnt" >/dev/null 2>&1 && break
    sleep 2
  done
  if mount | grep -q "dist/cg_mnt"; then
    hdiutil detach "dist/cg_mnt" -force >/dev/null 2>&1 || true
  fi
  hdiutil convert "dist/contractG_raw.dmg" -format UDZO -o "dist/contractG.dmg"
  rm -f "dist/contractG_raw.dmg"
  rm -rf "dist/cg_mnt"
  echo "DMG 生成完成（makehybrid 回退）"
fi

hdiutil verify "dist/contractG.dmg"

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
