#!/bin/sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
APPDIR="$ROOT/build/appimage/AppDir"
OUTPUT="$ROOT/dist/GenPatcher-Linux-x86_64.AppImage"

if [ "$(uname -m)" != "x86_64" ]; then
    echo "This build script currently supports x86_64 only." >&2
    exit 1
fi

if [ -n "${APPIMAGETOOL:-}" ]; then
    TOOL="$APPIMAGETOOL"
elif command -v appimagetool >/dev/null 2>&1; then
    TOOL="$(command -v appimagetool)"
else
    echo "appimagetool is required. Install it or set APPIMAGETOOL to its path." >&2
    exit 1
fi

rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/share/genpatcher" "$APPDIR/usr/share/icons/hicolor/256x256/apps" "$ROOT/dist"

cp "$ROOT/GenPatcher.py" "$APPDIR/usr/share/genpatcher/"
cp -a "$ROOT/CSS" "$ROOT/lang" "$ROOT/Offline" "$ROOT/Images" "$APPDIR/usr/share/genpatcher/"
cp "$ROOT/Images/Logo/GenPatcher logo.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/genpatcher.png"
cp "$ROOT/Images/Logo/GenPatcher logo.png" "$APPDIR/genpatcher.png"
cp "$ROOT/packaging/AppRun" "$ROOT/packaging/genpatcher.desktop" "$APPDIR/"
chmod +x "$APPDIR/AppRun"

if command -v desktop-file-validate >/dev/null 2>&1; then
    desktop-file-validate "$APPDIR/genpatcher.desktop"
fi

ARCH=x86_64 APPIMAGE_EXTRACT_AND_RUN=1 "$TOOL" "$APPDIR" "$OUTPUT"
chmod +x "$OUTPUT"
echo "Created $OUTPUT"
