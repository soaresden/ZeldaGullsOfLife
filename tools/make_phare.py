"""Le Phare Éteint vu de dehors (le cap, 1:7b) : un vrai phare, pas une maison (Denis).

Le cap a son propre décor, $6c (copie du village du passé, $10 ; son Songe : $6d, en bleuté), faits
par tools/make_songe.py. On y ajoute onze briques ($c0-$ca) : une tour de 3 x 4 briques (48 x 64
pixels), rayée blanc et rouge, sa lanterne jaune et son dôme rouge ; la porte d'Ages (la brique de)
reste au pied, au milieu (le passage vers le donjon ne change pas). Les tuiles des nouvelles
briques prennent la place de tuiles du décor que le cap n'affiche jamais.

Couleurs (les palettes du décor $10) : 4 les rouges (0 le sol clair, 1 rouge, 2 rouge foncé, 3 noir),
6 le blanc et le bleu (0 crème, 1 bleu : la mer, 2 bleu foncé, 3 noir), 7 la lanterne (0 jaune).

Usage : python tools/make_phare.py   (après tools/make_songe.py, avant tools/make_rooms.py)
"""
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
DECORS = (0x6c, 0x6d)
ROOM_BRICKS = {0xfc, 0xfa, 0x3b, 0x0c, 0xde}   # les briques du cap (story/salles/ile_brume.txt)
FIRST = 0xc0
GREY = {255: 0, 170: 1, 85: 2, 0: 3}
LEVEL = {0: 255, 1: 170, 2: 85, 3: 0}
RED, WHITE, LAMP = 4, 6, 7
W, H = 48, 64


def lighthouse():
    """L'image (48 x 64, couleurs 0-3) et la palette de chaque tuile (6 x 8)."""
    img = [[0] * W for _ in range(H)]
    pal = [[RED] * 6 for _ in range(8)]
    # Les côtés du haut (deux rangées de briques) : la mer (palette 6, bleu)
    for ty in range(4):
        for tx in (0, 5):
            pal[ty][tx] = WHITE
            for y in range(ty * 8, ty * 8 + 8):
                for x in range(tx * 8, tx * 8 + 8):
                    img[y][x] = 1
    # Le dôme (rouge, liseré noir)
    for y in range(8):
        half = (4, 7, 10, 12, 13, 14, 15, 16)[y]
        for x in range(24 - half, 24 + half):
            edge = x in (24 - half, 24 + half - 1) or y == 0
            img[y][x] = 3 if edge else (1 if x < 24 else 2)
    # La lanterne (jaune) : un cadre noir, des montants
    for tx in range(1, 5):
        pal[1][tx] = LAMP
    for y in range(8, 16):
        for x in range(8, 40):
            frame = y in (8, 15) or x in (8, 16, 24, 31, 39)
            img[y][x] = 3 if frame else 0
    # La galerie : la rambarde (rouge foncé, poteaux noirs)
    for y in range(16, 24):
        for x in range(8, 40):
            if y in (16, 23):
                img[y][x] = 3
            elif y in (17, 18):
                img[y][x] = 2
            else:
                img[y][x] = 3 if x % 4 == 0 else 1
    # Les rayures : blanc (palette 6), rouge (palette 4), blanc, rouge (le pied, avec la porte)
    for ty, p in ((3, WHITE), (4, RED), (5, WHITE), (6, RED), (7, RED)):
        for tx in range(1, 5):
            pal[ty][tx] = p
        for y in range(ty * 8, ty * 8 + 8):
            for x in range(8, 40):
                if x in (8, 39):
                    img[y][x] = 3
                elif p == WHITE:
                    img[y][x] = 0                        # (le blanc : sans ombre, la palette 6 n'a que du bleu)
                else:
                    img[y][x] = 1 if x > 12 else 2
    # Le pied : les côtés sur le sol (palette 4, le sol clair)
    for ty in range(4, 8):
        for tx in (0, 5):
            pal[ty][tx] = RED
            for y in range(ty * 8, ty * 8 + 8):
                for x in range(tx * 8, tx * 8 + 8):
                    img[y][x] = 0
    return img, pal


def path(kind, ts):
    return {'gfx': os.path.join(DISASM, 'gfx', 'ages', 'gfx_tileset%02x.png' % ts),
            'map': os.path.join(DISASM, 'tileset_layouts_expanded', 'ages', 'tilesetMappings%02x.bin' % ts),
            'col': os.path.join(DISASM, 'tileset_layouts_expanded', 'ages', 'tilesetCollisions%02x.bin' % ts)}[kind]


def decor(ts, img, pal):
    original = Image.open(path('gfx', ts))
    palette = original.getpalette()
    im = original.convert('L')
    maps = bytearray(open(path('map', ts), 'rb').read())
    cols = bytearray(open(path('col', ts), 'rb').read())
    keep = set()
    for mt in ROOM_BRICKS:
        for q in range(4):
            keep.add(maps[mt * 8 + q] ^ 0x80)
    # (pas les tuiles que l'animation de la mer réécrit sans cesse : 4-19 et 232-239 de l'image,
    # data/ages/animationGfxHeaders.s ; on garde de la marge)
    free = [n for n in range(32, 224) if n not in keep]
    door = maps[0xde * 8:0xde * 8 + 8]

    def put_tile(n, x0, y0):
        for y in range(8):
            for x in range(8):
                im.putpixel(((n % 16) * 8 + x, (n // 16) * 8 + y), LEVEL[img[y0 + y][x0 + x]])

    # Les briques : (rangée, colonne) dans la tour -> numéro ; la porte d'Ages au milieu du pied
    bricks = [(r, c) for r in range(4) for c in range(3) if (r, c) != (3, 1)]
    for k, (r, c) in enumerate(bricks):
        mt = FIRST + k
        entry, attrs = [], []
        for q in range(4):
            tx, ty = c * 2 + q % 2, r * 2 + q // 2
            n = free.pop(0)
            put_tile(n, tx * 8, ty * 8)
            entry.append(n ^ 0x80)
            attrs.append(0x08 | pal[ty][tx])     # banque vidéo 1, la palette
        maps[mt * 8:mt * 8 + 8] = bytes(entry + attrs)
        cols[mt] = 0x0f                          # la tour : un mur
    index = {palette[3 * i]: i for i in range(4)}
    out = Image.new('P', im.size)
    out.putpalette(palette)
    out.putdata([index[v] for v in im.getdata()])
    out.save(path('gfx', ts))
    open(path('map', ts), 'wb').write(maps)
    open(path('col', ts), 'wb').write(cols)
    assert bytes(door) == bytes(maps[0xde * 8:0xde * 8 + 8])
    return len(bricks)


def main():
    img, pal = lighthouse()
    for ts in DECORS:
        n = decor(ts, img, pal)
    print('-> le phare du cap : %d briques ($%02x-$%02x) dans les décors $6c et $6d' % (n, FIRST, FIRST + n - 1))


if __name__ == '__main__':
    main()
