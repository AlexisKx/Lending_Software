#!/usr/bin/env bash
# Build Tailwind output.css using the standalone CLI binary.
# Downloads the binary on first run (no Node required).
#
# Use --watch for dev:  ./scripts/build_tailwind.sh --watch

set -euo pipefail

BIN_DIR=".tailwind"
BIN="$BIN_DIR/tailwindcss"
VERSION="${TAILWIND_VERSION:-v3.4.13}"

uname_s="$(uname -s)"
uname_m="$(uname -m)"
case "$uname_s-$uname_m" in
  Linux-x86_64)   ASSET="tailwindcss-linux-x64" ;;
  Linux-aarch64)  ASSET="tailwindcss-linux-arm64" ;;
  Darwin-x86_64)  ASSET="tailwindcss-macos-x64" ;;
  Darwin-arm64)   ASSET="tailwindcss-macos-arm64" ;;
  *) echo "Unsupported platform: $uname_s-$uname_m" >&2; exit 1 ;;
esac

if [[ ! -x "$BIN" ]]; then
  mkdir -p "$BIN_DIR"
  URL="https://github.com/tailwindlabs/tailwindcss/releases/download/$VERSION/$ASSET"
  echo "Downloading Tailwind CLI ($VERSION, $ASSET)..."
  curl -sSL "$URL" -o "$BIN"
  chmod +x "$BIN"
fi

mkdir -p static/css
"$BIN" -i ./static/css/input.css -o ./static/css/output.css --minify "$@"
