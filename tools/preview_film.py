"""Aperçu en couleurs d'une image du film, sans compiler (après tools/make_film.py).

Recompose le décor depuis map/flg et pose les sprites aux positions du film, avec les
couleurs de PALH_FILM.

Usage : python tools/preview_film.py SORTIE.png
"""
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = os.path.join(ROOT, 'oracles-disasm', 'gfx_compressible', 'ages')


def rgb(r, g, b):
    return (r * 8, g * 8, b * 8)


BG = [[rgb(0, 0, 0)] * 4,
      [rgb(4, 10, 24), rgb(10, 18, 28), rgb(18, 25, 31), rgb(31, 27, 18)],
      [rgb(2, 6, 18), rgb(5, 12, 25), rgb(12, 23, 29), rgb(29, 31, 31)]]
SP = {0: [None, rgb(0, 0, 0), rgb(2, 21, 8), rgb(31, 26, 17)],
      1: [None, rgb(0, 0, 0), rgb(31, 1, 5), rgb(31, 26, 17)],
      2: [None, rgb(10, 5, 1), rgb(20, 11, 4), rgb(28, 21, 10)],
      3: [None, rgb(31, 15, 1), rgb(31, 27, 5), rgb(31, 31, 21)],
      4: [None, rgb(0, 0, 0), rgb(31, 1, 5), rgb(31, 31, 31)],
      5: [None, rgb(12, 4, 6), rgb(31, 11, 4), rgb(31, 26, 18)]}


def main():
    tiles = Image.open(os.path.join(G, 'gfx_film_bg.png')).convert('L')
    m = open(os.path.join(G, 'map_film_bg.bin'), 'rb').read()
    f = open(os.path.join(G, 'flg_film_bg.bin'), 'rb').read()
    grey2c = {255: 0, 170: 1, 85: 2, 0: 3}
    scr = Image.new('RGB', (160, 144))
    for ty in range(18):
        for tx in range(20):
            t, p = m[ty * 32 + tx], f[ty * 32 + tx]
            for y in range(8):
                for x in range(8):
                    g = tiles.getpixel(((t % 16) * 8 + x, (t // 16) * 8 + y))
                    scr.putpixel((tx * 8 + x, ty * 8 + y), BG[p][grey2c[g]])
    spr = Image.open(os.path.join(G, 'spr_film.png')).convert('L')
    g2 = {0: 0, 85: 1, 170: 2, 255: 3}

    def put(cx, cy, w, h, sx, sy, pal, flip=False):
        for y in range(h):
            for x in range(w):
                xx = w - 1 - x if flip else x
                c = g2[spr.getpixel((cx * 16 + xx, cy * 16 + y))]
                if c and 0 <= sx + x < 160 and 0 <= sy + y < 144:
                    scr.putpixel((sx + x, sy + y), SP[pal][c])

    # Du fond vers le premier plan
    put(3, 1, 32, 16, 104, 64, 3)      # soleil
    put(0, 1, 48, 16, 48, 100, 2)      # rondin
    put(0, 2, 32, 32, 36, 18, 5)       # visage de Marine
    put(2, 2, 16, 16, 56, 14, 4)       # sa fleur
    put(1, 0, 16, 16, 54, 88, 0)       # Link de dos, il lève les yeux
    scr.resize((480, 432), Image.NEAREST).save(sys.argv[1])


main()
