#!/usr/bin/env bash
# =============================================================================
# MYANG STUDIO ENGINE — bootstrap
# Restores the render toolchain after a machine/sandbox reset.
# Usage:  bash bootstrap.sh
# =============================================================================
set -euo pipefail

BASE="${MYANG_HOME:-/home/z/my-project}"
ENGINE="$BASE/download/content-engine"
MS="$BASE/mega-shot"
STUDIO="$BASE/studio"

echo "[1/4] edge-tts (narration + word timestamps)"
python3 -c "import edge_tts" 2>/dev/null || pip install -q edge-tts

echo "[2/4] mega-shot CLI (xp)"
if [ ! -f "$MS/xp" ] && [ -z "$(ls -A "$MS" 2>/dev/null)" ]; then
  rm -rf "$MS"
  git clone --depth 1 https://github.com/stevenguyenbt/mega-shot "$MS"
fi

echo "[3/4] studio workspace"
mkdir -p "$STUDIO/videos"

echo "[4/4] xp assets (chromium + huashu drawn styles + fonts)"
cd "$STUDIO" && bash "$MS/xp" setup --install chromium huashu fonts || \
  echo "NOTE: xp setup failed — check node runtime, re-run later. Per-scene caches make re-runs cheap."

echo "Bootstrap done. Next: python3 bin/new_video.py <slug>"
