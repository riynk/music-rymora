#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
git -C "$ROOT" submodule update --init --recursive
python3 "$ROOT/scripts/apply_rymora_branding.py" "$ROOT/android/vendor/koda"
python3 "$ROOT/scripts/apply_rymora_lyrics.py" "$ROOT/android/vendor/koda"
printf '\nOpen android/vendor/koda in Android Studio.\n'