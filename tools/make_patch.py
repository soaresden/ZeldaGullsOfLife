"""Fabrique le patch BPS de Gulls of Life, à appliquer sur Oracle of Ages (USA).

On ne distribue jamais la ROM : seulement ce patch (out/gulls_of_life.bps).

Usage : python tools/make_patch.py "chemin/Legend of Zelda, The - Oracle of Ages (USA).gbc"
"""
import os
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bps  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGES_USA_CRC = 0x3800a387


def main():
    source = open(sys.argv[1], 'rb').read()
    crc = zlib.crc32(source)
    if crc != AGES_USA_CRC:
        sys.exit('ROM inattendue (CRC32 %08x) : il faut Oracle of Ages (USA), CRC32 %08x'
                 % (crc, AGES_USA_CRC))
    target = open(os.path.join(ROOT, 'out', 'gulls_of_life.gbc'), 'rb').read()
    patch = bps.encode(source, target)
    assert bps.decode(source, patch) == target
    out = os.path.join(ROOT, 'out', 'gulls_of_life.bps')
    open(out, 'wb').write(patch)
    print('%s : %d octets (ROM obtenue : CRC32 %08x)' % (out, len(patch), zlib.crc32(target)))


main()
