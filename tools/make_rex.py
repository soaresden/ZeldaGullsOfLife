"""Le boss du Terrier des Serpents, la machine possédée, en grand (Denis : « regarde comment c'est dans
Ghost Babel ») : une machine de guerre vue de face, dans l'ombre au fond de l'arène (4:d7), dessinée
dans le décor (des briques), pas en sprites : 7 x 5 briques (112 x 80 pixels). Dessin fait à la main
(des formes), pas copié : le lance-missiles sur le dos, le dôme blindé, les épaulières, les deux
longs canons en diagonale, la tête en coin et ses yeux jaunes, les jambes massives.

Les briques $c0-$e2 du décor $6b (le Terrier) : 7 par rangée, de haut en bas. Leurs tuiles prennent
la place de tuiles de la banque vidéo 1 que le Terrier n'utilise pas ; une tuile et sa copie miroir
n'en font qu'une (la machine est symétrique). Couleurs : la palette 5 du décor (noir, violet sombre,
violet, lavande) ; les tuiles des yeux, la palette 1 (noir, violet sombre, violet, jaune). Le
Terrier n'utilise ni l'une ni l'autre ; PALH_REX les charge quand la machine apparaît
(code/ages/balladeTerrier.s).

Usage : python tools/make_rex.py [APERCU.png]   (après tools/make_songe.py, avant tools/make_rooms.py)
"""
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
DECOR = 0x6b
W, H = 112, 80
BW, BH = 7, 5
FIRST = 0xc0
BODY, EYES = 5, 1
YELLOW = 4          # (dans le dessin : le jaune des yeux, couleur 3 de la palette 1)
LEVEL = {0: 255, 1: 170, 2: 85, 3: 0}
# Les briques du Terrier (story/salles/terrier.txt), et celles que le jeu y pose (volets ouverts,
# portes, coffres) : leurs tuiles restent
TERRIER_BRICKS = {0x08, 0x09, 0x0c, 0x0d, 0x10, 0x1d, 0x26, 0x27, 0x2a, 0x71, 0x73, 0x78, 0x79, 0x7c,
                  0x7d, 0x7e, 0x7f, 0xa0, 0xa3, 0xa4, 0xb0, 0xb1, 0xb2, 0xb3, 0xb8, 0xb9, 0xba, 0xbb,
                  0xf0, 0xf1}
# Les couleurs (RGB 0-31), pour l'aperçu et data/ages/paletteData.s (paletteDataRex)
PAL_BODY = [(0, 0, 0), (7, 4, 12), (14, 11, 22), (23, 21, 30)]
PAL_EYES = [(0, 0, 0), (7, 4, 12), (14, 11, 22), (31, 28, 6)]


def outlined(d, shape, xy, fill, **kw):
    """Une forme remplie, avec un bord violet sombre."""
    getattr(d, shape)(xy, fill=fill, outline=1, **kw)


def draw():
    im = Image.new('P', (W, H), 0)
    d = ImageDraw.Draw(im)
    cx = W // 2
    # Les canons (derrière tout) : deux longues barres en diagonale, des épaules vers le bas, et leurs
    # fixations
    for s in (-1, 1):
        x0, y0, x1, y1 = cx + s * 29, 24, cx + s * 53, 79
        for k, c in ((4, 1), (2, 2), (1, 3)):
            d.line((x0, y0, x1, y1), fill=c, width=k * 2 + 1)
        d.line((x0 + s * 3, y0 + 2, x1 + s * 1, y1), fill=1)          # l'ombre du canon
        for t in (0.35, 0.6, 0.85):
            bx, by = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            d.line((bx - 5, by - 2, bx + 5, by + 2), fill=1, width=3)
            d.point((bx, by), fill=3)
    # Les hanches, entre les jambes
    outlined(d, 'rectangle', (cx - 22, 48, cx + 22, 58), 1)
    # Le lance-missiles, sur le dos : deux caissons à lamelles, un rail au milieu
    for s in (-1, 1):
        bx = cx - 18 if s < 0 else cx + 2
        outlined(d, 'rectangle', (bx, 0, bx + 16, 17), 2)
        for x in range(bx + 3, bx + 15, 3):
            d.line((x, 3, x, 15), fill=1)
        d.line((bx + 1, 1, bx + 15, 1), fill=3)
        d.line((bx + 1, 16, bx + 15, 16), fill=1)
    outlined(d, 'rectangle', (cx - 2, 0, cx + 2, 14), 1)
    # Le corps : le dôme blindé ; son ombre en bas, ses plaques
    outlined(d, 'ellipse', (cx - 28, 11, cx + 28, 55), 2)
    d.arc((cx - 25, 14, cx + 25, 52), 195, 345, fill=3)
    d.arc((cx - 26, 13, cx + 26, 53), 20, 160, fill=1)
    d.arc((cx - 24, 15, cx + 24, 51), 30, 150, fill=1)
    for s in (-1, 1):
        d.line((cx + s * 7, 13, cx + s * 17, 28), fill=1)
        d.line((cx + s * 17, 28, cx + s * 25, 40), fill=1)
        d.line((cx + s * 17, 29, cx + s * 24, 40), fill=3)
        for (rx, ry) in ((19, 36), (14, 20)):
            d.point((cx + s * rx, ry), fill=3)
            d.point((cx + s * rx, ry + 1), fill=1)
    # le petit dôme clair au milieu (le cockpit : le fantôme est dedans)
    outlined(d, 'ellipse', (cx - 11, 17, cx + 11, 35), 3)
    d.arc((cx - 9, 19, cx + 9, 33), 20, 160, fill=2)
    d.line((cx - 6, 21, cx - 3, 20), fill=3)
    # Les épaulières, rondes, et les fixations des canons
    for s in (-1, 1):
        ex = cx + s * 27
        outlined(d, 'ellipse', (ex - 8, 21, ex + 8, 37), 2)
        d.arc((ex - 6, 23, ex + 6, 35), 190, 300, fill=3)
        d.arc((ex - 6, 23, ex + 6, 35), 20, 150, fill=1)
        outlined(d, 'rectangle', (ex + s * 3 - 3, 33, ex + s * 3 + 3, 40), 1)
    # La tête en coin, sous le dôme ; le visage dans l'ombre, les yeux jaunes
    outlined(d, 'polygon', [(cx - 16, 37), (cx + 16, 37), (cx + 12, 52), (cx, 61), (cx - 12, 52)], 2)
    d.polygon([(cx - 12, 42), (cx + 12, 42), (cx + 9, 50), (cx, 56), (cx - 9, 50)], fill=1)
    d.line((cx - 14, 39, cx + 14, 39), fill=3)
    for s in (-1, 1):
        d.polygon([(cx + s * 3, 45), (cx + s * 11, 43), (cx + s * 10, 46), (cx + s * 3, 47)], fill=YELLOW)
    d.line((cx, 48, cx, 58), fill=2)
    d.line((cx - 5, 53, cx + 5, 53), fill=2)
    # Les jambes massives : les cuisses, les genoux, les tibias, les pieds
    for s in (-1, 1):
        lx = cx + s * 17
        outlined(d, 'rectangle', (lx - 7, 52, lx + 7, 71), 2)
        d.line((lx - 5, 54, lx - 5, 69), fill=3)
        d.line((lx + 5, 54, lx + 5, 69), fill=1)
        for y in (60, 66):
            d.line((lx - 6, y, lx + 6, y), fill=1)
        outlined(d, 'ellipse', (lx - 8, 55, lx + 8, 65), 2)
        d.arc((lx - 6, 57, lx + 6, 63), 200, 320, fill=3)
        d.arc((lx - 6, 57, lx + 6, 63), 30, 150, fill=1)
        outlined(d, 'rectangle', (lx - 11, 70, lx + 11, 79), 2)
        d.line((lx - 10, 72, lx + 10, 72), fill=3)
        d.line((lx - 10, 77, lx + 10, 77), fill=1)
        for x in (lx - 6, lx, lx + 6):
            d.line((x, 73, x, 77), fill=1)
    return im


def tiles_of(im):
    """Les tuiles 8 x 8 : (pixels en couleurs 0-3, palette)."""
    px = im.load()
    out = []
    for ty in range(H // 8):
        row = []
        for tx in range(W // 8):
            cells = [[px[tx * 8 + x, ty * 8 + y] for x in range(8)] for y in range(8)]
            eyes = any(c == YELLOW for r in cells for c in r)
            if eyes:
                cells = [[3 if c == YELLOW else min(c, 2) for c in r] for r in cells]
            row.append((tuple(tuple(r) for r in cells), EYES if eyes else BODY))
        out.append(row)
    return out


def path(kind):
    return {'gfx': os.path.join(DISASM, 'gfx', 'ages', 'gfx_tileset%02x.png' % DECOR),
            'map': os.path.join(DISASM, 'tileset_layouts_expanded', 'ages', 'tilesetMappings%02x.bin' % DECOR),
            'col': os.path.join(DISASM, 'tileset_layouts_expanded', 'ages', 'tilesetCollisions%02x.bin' % DECOR)}[kind]


def preview(im, dst):
    out = Image.new('RGB', (W * 4, H * 4))
    tl = tiles_of(im)
    for ty, row in enumerate(tl):
        for tx, (cells, p) in enumerate(row):
            pal = PAL_EYES if p == EYES else PAL_BODY
            for y in range(8):
                for x in range(8):
                    c = tuple(v * 8 for v in pal[cells[y][x]])
                    for dy in range(4):
                        for dx in range(4):
                            out.putpixel(((tx * 8 + x) * 4 + dx, (ty * 8 + y) * 4 + dy), c)
    out.save(dst)


def main():
    im = draw()
    if len(sys.argv) > 1:
        preview(im, sys.argv[1])
        print('->', sys.argv[1])
        return
    original = Image.open(path('gfx'))
    palette = original.getpalette()
    gfx = original.convert('L')
    maps = bytearray(open(path('map'), 'rb').read())
    cols = bytearray(open(path('col'), 'rb').read())
    keep = set()
    for mt in TERRIER_BRICKS:
        for q in range(4):
            if maps[mt * 8 + 4 + q] & 0x08:
                keep.add(maps[mt * 8 + q] ^ 0x80)
    free = [n for n in range(256) if n not in keep]
    placed = {}      # pixels -> (tuile, miroir)

    def tile_index(cells):
        if cells in placed:
            return placed[cells], 0
        mirror = tuple(tuple(reversed(r)) for r in cells)
        if mirror in placed:
            return placed[mirror], 0x20
        n = free.pop(0)
        for y in range(8):
            for x in range(8):
                gfx.putpixel(((n % 16) * 8 + x, (n // 16) * 8 + y), LEVEL[cells[y][x]])
        placed[cells] = n
        return n, 0

    tl = tiles_of(im)
    for by in range(BH):
        for bx in range(BW):
            mt = FIRST + by * BW + bx
            entry, attrs = [], []
            for q in range(4):
                cells, p = tl[by * 2 + q // 2][bx * 2 + q % 2]
                n, flip = tile_index(cells)
                entry.append(n ^ 0x80)
                attrs.append(0x08 | flip | p)
            maps[mt * 8:mt * 8 + 8] = bytes(entry + attrs)
            cols[mt] = 0x0f
    index = {palette[3 * i]: i for i in range(4)}
    out = Image.new('P', gfx.size)
    out.putpalette(palette)
    out.putdata([index[v] for v in gfx.getdata()])
    out.save(path('gfx'))
    open(path('map'), 'wb').write(maps)
    open(path('col'), 'wb').write(cols)
    print('-> la machine du Terrier : %d briques ($%02x-$%02x), %d tuiles, dans le décor $%02x'
          % (BW * BH, FIRST, FIRST + BW * BH - 1, len(placed), DECOR))


if __name__ == '__main__':
    main()
