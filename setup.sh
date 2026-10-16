#!/bin/bash
# Prépare l'environnement de compilation (une seule fois) :
# - le désassemblage oracles-disasm, branche hack/gulls-of-life du fork
#   soaresden/oracles-disasm (partie de la branche hack-base de Stewmath)
# - WLA-DX v10.6 (l'assembleur)
# Requiert MSYS2 (C:\msys64) avec cmake, make et gcc (mingw64), et Python 3
# avec pyyaml et pillow (pip install pyyaml pillow), plus pyboy pour les tests.
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"

if [ ! -d "$ROOT/oracles-disasm" ]; then
    git clone -b hack/gulls-of-life https://github.com/soaresden/oracles-disasm.git "$ROOT/oracles-disasm"
    cd "$ROOT/oracles-disasm"
    # tools/aux : nom réservé sous Windows, inutile pour compiler
    git sparse-checkout set --no-cone '/*' '!/tools/aux/'
    git remote add upstream https://github.com/Stewmath/oracles-disasm.git
    git fetch upstream hack-base
fi

WLA="$ROOT/tools-build/wla-dx"
if [ ! -x "$WLA/build/binaries/wla-gb.exe" ]; then
    mkdir -p "$ROOT/tools-build"
    [ -d "$WLA" ] || git clone --depth 1 -b v10.6 https://github.com/vhelin/wla-dx.git "$WLA"
    cmake -S "$WLA" -B "$WLA/build" -G "MSYS Makefiles" -DCMAKE_BUILD_TYPE=Release -DCMAKE_POLICY_VERSION_MINIMUM=3.5
    cmake --build "$WLA/build" --target wla-gb wlalink -j8
fi
echo "Prêt : ./build.sh compile le jeu dans out/gulls_of_life.gbc"
