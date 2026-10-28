"""La maison de Marine sur son île (1:5b) : une vraie maison (Denis : « ça ressemble même pas à une
maison, sa maison ! »), dessinée dans art/maison_marine.txt, mise dans des briques libres du décor
$18 (la plage de l'île Croissant) : le toit $a6 $a7 $a8, les murs $a9 $aa, la porte $de (une
brique-porte d'Ages, warpTiles.s, libre dans ce décor : elle mène dedans comme l'ancienne $dd ;
même collision). Couleurs : la palette 0 du décor (rouge sombre, rouge, crème, noir).

Comme tools/make_maison_dx.py : les tuiles prennent les places que les briques des salles du décor
n'utilisent pas (d'abord $80-$ff de l'image). Lancé avant tools/make_songe.py : le Songe ($7e,
copie du $18) a la même maison. Relancer le script redonne la même chose.

Usage : python tools/make_maison_ile.py
"""
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
DECOR = 0x18
SONGE = 0x7e
# les briques, dans l'ordre du dessin (2 rangs de 3) ; la porte copie la collision de $dd
BRICKS = [[0xa6, 0xa7, 0xa8], [0xa9, 0xde, 0xaa]]
PALETTE = 0
LAYOUT_GROUP = {0: 0, 1: 2, 2: 1, 3: 3, 4: 4, 5: 5}


def used_bricks():
    used = set()
    for g in range(6):
        ts = open(os.path.join(DISASM, 'rooms', 'ages', 'group%dTilesets.bin' % g), 'rb').read()
        for r in range(256):
            if ts[r] & 0x7f not in (DECOR, SONGE):
                continue
            for size in ('small', 'large'):
                p = os.path.join(DISASM, 'rooms', 'ages', size, 'room%02x%02x.bin' % (LAYOUT_GROUP[g], r))
                if os.path.exists(p):
                    used |= set(open(p, 'rb').read())
    return used


def main():
    rows = [l.rstrip('\n') for l in open(os.path.join(ROOT, 'art', 'maison_marine.txt'), encoding='utf-8')
            if l.strip() and not l.startswith('#')]
    assert len(rows) == 32 and all(len(r) == 48 for r in rows)
    gfx_path = os.path.join(DISASM, 'gfx', 'ages', 'gfx_tileset%02x.png' % DECOR)
    lay = os.path.join(DISASM, 'tileset_layouts_expanded', 'ages', 'tileset%s%02x.bin')
    original = Image.open(gfx_path)
    palette = original.getpalette()
    gfx = original.convert('L')
    maps = bytearray(open(lay % ('Mappings', DECOR), 'rb').read())
    cols = bytearray(open(lay % ('Collisions', DECOR), 'rb').read())
    ours = {b for row in BRICKS for b in row}
    others = used_bricks() - ours
    keep = set()
    for mt in others:
        for q in range(4):
            if maps[mt * 8 + 4 + q] & 0x08:
                keep.add(maps[mt * 8 + q] ^ 0x80)
    free = [n for n in range(0x80, 256) if n not in keep] + [n for n in range(0x80) if n not in keep]
    placed = {}
    for by, row in enumerate(BRICKS):
        for bx, mt in enumerate(row):
            entry = []
            for ty, tx in ((0, 0), (0, 1), (1, 0), (1, 1)):
                x0, y0 = bx * 16 + tx * 8, by * 16 + ty * 8
                cells = tuple(tuple(255 - 85 * int(rows[y0 + y][x0 + x]) for x in range(8)) for y in range(8))
                if cells not in placed:
                    n = free.pop(0)
                    for y in range(8):
                        for x in range(8):
                            gfx.putpixel(((n % 16) * 8 + x, (n // 16) * 8 + y), cells[y][x])
                    placed[cells] = n
                entry.append(placed[cells] ^ 0x80)
            maps[mt * 8:mt * 8 + 8] = bytes(entry + [0x08 | PALETTE] * 4)
            cols[mt] = cols[0xdd] if mt == 0xde else 0x0f
    out = gfx.convert('P')
    out.putpalette(palette)
    out.putdata([{255: 0, 170: 1, 85: 2, 0: 3}[v] for v in gfx.getdata()])
    out.save(gfx_path)
    open(lay % ('Mappings', DECOR), 'wb').write(maps)
    open(lay % ('Collisions', DECOR), 'wb').write(cols)
    print('maison de Marine : %d briques, %d tuiles (décor $%02x)' % (6, len(placed), DECOR))


if __name__ == '__main__':
    main()
