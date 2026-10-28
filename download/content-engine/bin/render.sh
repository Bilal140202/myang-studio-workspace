#!/usr/bin/env bash
# =============================================================================
# Render pipeline: art -> mix -> render -> export  (+ thumbnail when configured)
# Usage:  bash render.sh <project_dir>
# Env:    MS_ENCODER=x264 (CPU sandbox); unset for GPU default
# =============================================================================
set -uo pipefail
PROJ="${1:?usage: render.sh <project_dir>}"
export MS_ENCODER="${MS_ENCODER:-x264}"
MS="${MYANG_MEGASHOT:-/home/z/my-project/mega-shot}"
XP="$MS/xp"
cd "$PROJ" || exit 1

step() { echo "── $* ─────────────────────────────────"; }

# Long xp jobs can be SIGKILLed by sandbox watchdogs AFTER writing valid
# artifacts; per-scene caches make re-runs resume cheaply. Retry once each.
run() {
  step "$1"
  bash "$XP" "$@" || bash "$XP" "$@" || echo "!! '$1' still failing — inspect $PROJ/build logs"
}

run art
run mix
run render
run export
[ -f anh_bia.yaml ] && run thumbnail

echo "── done — verify with:  bin/qa_gate.py $PROJ"
