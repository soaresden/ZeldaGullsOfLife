"""Ajoute à la police du jeu (gfx/common/gfx_font.png) les lettres qui manquent en français.

La police américaine n'a pas de « ô » : on le dessine à la place que lui donne la version
européenne (caractère $d1, voir EU_additional dans tools/build/parseText.py, lancé avec --EU).
Il est fait du « ö » ($ac) dont on remplace le tréma par l'accent du « â » ($a1).

La police d'origine est relue dans git (branche hack-base) : on peut relancer le script.

Usage : python tools/make_font.py   (depuis la racine du dépôt)
"""
import io
import os
import subprocess

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
PNG = 'gfx/common/gfx_font.png'


def cell(c):
    """Coin haut gauche du caractère c (8x16, 16 caractères par ligne)."""
    return (c % 16) * 8, (c // 16) * 16


def copy_rows(px, src, dst, rows):
    sx, sy = cell(src)
    dx, dy = cell(dst)
    for y in rows:
        for x in range(8):
            px[dx + x, dy + y] = px[sx + x, sy + y]


def main():
    png = subprocess.run(['git', 'show', 'upstream/hack-base:' + PNG], cwd=DISASM,
                         capture_output=True, check=True).stdout
    im = Image.open(io.BytesIO(png))
    im.load()
    px = im.load()
    # ô ($d1) : le corps du « ö » ($ac), puis l'accent du « â » ($a1) à la place du tréma
    copy_rows(px, 0xac, 0xd1, range(16))
    ax, ay = cell(0xa1)
    umlaut = cell(0xa2)
    accent_rows = [y for y in range(9)
                   if any(px[ax + x, ay + y] != px[umlaut[0] + x, umlaut[1] + y] for x in range(8))]
    copy_rows(px, 0xa1, 0xd1, range(min(accent_rows), max(accent_rows) + 1))
    im.save(os.path.join(DISASM, PNG))
    print('police : ô ajouté ->', PNG)


main()
