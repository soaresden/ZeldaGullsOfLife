#!/bin/bash
# Compile The Legend of Zelda: Gulls of Life (base : Oracle of Ages, hack-base).
# À lancer depuis Git Bash. Requiert MSYS2 (make), Python 3 + pyyaml/pillow,
# et WLA-DX v10.6 (voir setup.sh). Régénère d'abord les textes et les sprites.
set -e
PYTHON="${PYTHON:-$(command -v python)}"
ROOT="$(cd "$(dirname "$0")" && pwd)"
WLA="${WLA:-$ROOT/tools-build/wla-dx/build/binaries}"
export PATH="$WLA:/c/msys64/usr/bin:$PATH"
# Les outils Python lisent les .yaml sans préciser l'encodage : forcer l'UTF-8 (accents)
export PYTHONUTF8=1
"$PYTHON" "$ROOT/tools/make_text.py"
"$PYTHON" "$ROOT/tools/make_sprites.py"
"$PYTHON" -W ignore "$ROOT/tools/make_film.py"
"$PYTHON" "$ROOT/tools/make_photos.py"
"$PYTHON" "$ROOT/tools/make_title.py"
"$PYTHON" "$ROOT/tools/make_menus_fr.py"
"$PYTHON" "$ROOT/tools/make_blurbs.py"
"$PYTHON" "$ROOT/tools/make_songe.py"
"$PYTHON" "$ROOT/tools/make_mamono.py"
"$PYTHON" "$ROOT/tools/make_rooms.py"
"$PYTHON" "$ROOT/tools/make_music.py"
cd "$ROOT/oracles-disasm"
make -j8 PYTHON="$PYTHON" ages
cp -f ages.gbc "$ROOT/out/gulls_of_life.gbc"
echo "-> out/gulls_of_life.gbc"
