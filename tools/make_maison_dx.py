"""La maison de Tarkin et Marine façon Link's Awakening DX (Denis : « reprends leur maison de Link's
Awakening ») : les meubles de la maison de Tarin et Marin dans DX (la salle B $A3), en vraies briques
du décor des maisons ($2b) : le lit (haut, bas), la table (gauche, droite), la commode (haut, bas),
la caisse, le tabouret, la jarre, le dallage sous les lits.

Les tuiles viennent du désassemblage de DX (LADX-Disassembly-main) : les briques $C5 $C6 $9B $9C $99
$9A $A6 $C0 $20 $0F de src/data/objects_tilemaps/indoor.cgb.asm (les tuiles $00-$0F :
gfx/indoor/tilesets/08.cgb.png ; $10-$1F : gfx/dungeons/floor/floor_c.cgb.png ; $F0-$FF :
gfx/items/house_a.cgb.png), leurs palettes dans src/data/object_attributes/indoors_b.asm (le
groupe 0) et src/data/palettes/interior.asm (InteriorPalette06, la maison de Marin et Tarin).
Chaque palette de DX prend la palette du décor $2b la plus proche (couleurs rangées par
luminosité : la palette 0 du décor les range autrement ; les pixels suivent).

Les briques $c0-$c4, $c7-$cb du décor $2b ne sont dans aucune salle en $2b (tools/make_maison_dx.py
le vérifie) ; leurs tuiles prennent des tuiles de la banque vidéo 1 qu'aucune autre brique utilisée
ne prend. Relancer le script redonne la même chose.

Usage : python tools/make_maison_dx.py   (après tools/make_songe.py, avant tools/make_rooms.py)
"""
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
DX = os.path.join(ROOT, 'LADX-Disassembly-main', 'src', 'gfx')
DECOR = 0x2b

# Nos briques : nom -> (brique du décor $2b, tuiles DX (haut gauche, haut droite, bas gauche, bas
# droite), palettes DX, solide)
FURNITURE = {
    'lit (haut)':      (0xc0, (0x08, 0x09, 0x0a, 0x0b), (3, 3, 1, 1), True),
    'lit (bas)':       (0xc1, (0x0a, 0x0b, 0x06, 0x07), (1, 1, 1, 1), True),
    'table (gauche)':  (0xc2, (0x0c, 0x04, 0x0e, 0x05), (6, 6, 6, 6), True),
    'table (droite)':  (0xc3, (0x04, 0x0d, 0x05, 0x0f), (6, 6, 6, 6), True),
    'commode (haut)':  (0xc4, (0xfc, 0xfd, 0xfe, 0xff), (7, 7, 7, 7), True),
    'commode (bas)':   (0xc7, (0xfe, 0xff, 0x12, 0x13), (7, 7, 0, 0), True),
    'caisse':          (0xc8, (0xf8, 0xfa, 0xf9, 0xfb), (1, 1, 1, 1), True),
    'tabouret':        (0xc9, (0xf4, 0xf6, 0xf5, 0xf7), (7, 7, 7, 7), True),
    'jarre':           (0xca, (0xf0, 0xf2, 0xf1, 0xf3), (6, 6, 6, 6), True),
    'dallage':         (0xcb, (0x18, 0x19, 0x1a, 0x1b), (5, 5, 5, 5), False),
}
OURS = {b for b, *_ in FURNITURE.values()}

# InteriorPalette06 de DX (la maison de Marin et Tarin), en RGB 8 bits
DX_PALETTES = [
    ('F8F888', 'E8B858', 'A86828', '000000'),
    ('F8F888', '8888A0', '283050', '000000'),
    ('F8F888', 'F81858', '700028', '000000'),
    ('F8F888', 'C87020', '703020', '000000'),
    ('A07810', 'F8F8F8', 'A07810', '000000'),
    ('F07888', 'F81858', '700028', '000000'),
    ('E8B858', 'C87020', '703020', '000000'),
    ('E8B858', 'F8F800', '987000', '000000'),
]
# Les palettes du décor $2b (PALH_TILESET_INDOORS_PRESENT : 0 = paletteData48e0, 2-7 =
# paletteData5600), en RGB 5 bits
DECOR_PALETTES = {
    0: [(13, 1, 5), (29, 1, 3), (31, 26, 17), (0, 0, 0)],
    2: [(17, 17, 9), (28, 18, 0), (16, 8, 2), (0, 0, 0)],
    3: [(30, 23, 14), (19, 13, 6), (10, 7, 0), (0, 0, 0)],
    4: [(28, 25, 15), (17, 16, 9), (8, 10, 6), (0, 0, 0)],
    5: [(28, 25, 15), (15, 18, 1), (5, 8, 0), (0, 0, 0)],
    6: [(31, 31, 17), (17, 11, 25), (12, 5, 16), (0, 0, 0)],
    7: [(28, 28, 30), (11, 16, 20), (5, 10, 15), (0, 0, 0)],
}


def lum(c):
    return 0.30 * c[0] + 0.59 * c[1] + 0.11 * c[2]


# Choix à la main : le gris-bleu des draps et de la caisse (DX 1) va au bleu du décor (7), pas au
# violet (6) que son blanc jaunâtre attirerait
OVERRIDE = {1: 7}


def closest_palette(dx, force=None):
    """La palette du décor la plus proche, couleurs rangées de la plus claire à la plus sombre (la
    palette 0 du décor les range autrement), et l'ordre de ses couleurs : order[k] = la couleur du
    décor qui prend la place de la k-ième plus claire."""
    cols = sorted((tuple(int(h[i:i + 2], 16) >> 3 for i in (0, 2, 4)) for h in dx), key=lum, reverse=True)
    best = None
    for p, pal in DECOR_PALETTES.items():
        if force is not None and p != force:
            continue
        order = sorted(range(4), key=lambda k: lum(pal[k]), reverse=True)
        d = sum(sum((a - b) ** 2 for a, b in zip(c, pal[k])) for c, k in zip(cols, order))
        if best is None or d < best[0]:
            best = (d, p, order)
    return best[1], best[2]


def dx_tile(t, sheets):
    """Une tuile 8 x 8 de DX (niveaux de gris : 255 = couleur 0 ... 0 = couleur 3)."""
    if t < 0x10:
        name, n, wide = 'indoor/tilesets/08.cgb.png', t, 2
    elif t < 0x20:
        name, n, wide = 'dungeons/floor/floor_c.cgb.png', t - 0x10, 2
    else:
        name, n, wide = 'items/house_a.cgb.png', t - 0xf0, 16
    im = sheets.setdefault(name, Image.open(os.path.join(DX, name)).convert('L'))
    x0, y0 = (n % wide) * 8, (n // wide) * 8
    return tuple(tuple(im.getpixel((x0 + x, y0 + y)) for x in range(8)) for y in range(8))


def used_bricks():
    used = set()
    for g in range(4):
        ts = open(os.path.join(DISASM, 'rooms', 'ages', 'group%dTilesets.bin' % g), 'rb').read()
        for r in range(256):
            if ts[r] != DECOR:
                continue
            for size in ('small', 'large'):
                p = os.path.join(DISASM, 'rooms', 'ages', size, 'room%02x%02x.bin' % (g, r))
                if os.path.exists(p):
                    used |= set(open(p, 'rb').read())
    return used


def main():
    if not os.path.isdir(DX):
        print('maison DX : pas de désassemblage de DX, le décor $2b reste tel quel')
        return
    gfx_path = os.path.join(DISASM, 'gfx', 'ages', 'gfx_tileset%02x.png' % DECOR)
    lay = os.path.join(DISASM, 'tileset_layouts_expanded', 'ages', 'tileset%s%02x.bin')
    original = Image.open(gfx_path)
    palette = original.getpalette()
    gfx = original.convert('L')
    maps = bytearray(open(lay % ('Mappings', DECOR), 'rb').read())
    cols = bytearray(open(lay % ('Collisions', DECOR), 'rb').read())
    used = used_bricks()
    others = used - OURS
    clash = OURS & others
    assert not clash, 'briques déjà prises dans le décor $2b : %s' % sorted(clash)
    keep = set()
    for mt in others:
        for q in range(4):
            if maps[mt * 8 + 4 + q] & 0x08:
                keep.add(maps[mt * 8 + q] ^ 0x80)
    # D'abord les tuiles $80-$ff de l'image (en mémoire vidéo $9000-$97ff : les sprites n'y vont
    # jamais) ; celles d'avant ($8800-$8fff) peuvent être écrasées par les images des objets de la
    # salle (la table de Tarkin l'était par son sprite)
    free = [n for n in range(0x80, 256) if n not in keep] + [n for n in range(0x80) if n not in keep]
    print('maison DX : %d tuiles libres hautes' % sum(1 for n in free if n >= 0x80))
    pals = [closest_palette(p, OVERRIDE.get(k)) for k, p in enumerate(DX_PALETTES)]
    # Les couleurs de DX, de la plus claire à la plus sombre : leur rang (une tuile de DX va de la
    # couleur 0, la plus claire, à 3)
    dxrank = []
    for dx in DX_PALETTES:
        dcols = [tuple(int(h[i:i + 2], 16) >> 3 for i in (0, 2, 4)) for h in dx]
        ranked = sorted(range(4), key=lambda k: lum(dcols[k]), reverse=True)
        dxrank.append({k: ranked.index(k) for k in range(4)})
    gray = {255: 0, 170: 1, 85: 2, 0: 3}
    sheets, placed = {}, {}
    for name, (mt, tiles, dxpals, solid) in FURNITURE.items():
        entry, attrs = [], []
        for t, p in zip(tiles, dxpals):
            dp, order = pals[p]
            cells = tuple(tuple(255 - 85 * order[dxrank[p][gray[v]]] for v in row) for row in dx_tile(t, sheets))
            if cells not in placed:
                n = free.pop(0)
                for y in range(8):
                    for x in range(8):
                        gfx.putpixel(((n % 16) * 8 + x, (n // 16) * 8 + y), cells[y][x])
                placed[cells] = n
            entry.append(placed[cells] ^ 0x80)
            attrs.append(0x08 | dp)
        maps[mt * 8:mt * 8 + 8] = bytes(entry + attrs)
        cols[mt] = 0x0f if solid else 0x00
    out = gfx.convert('P')
    out.putpalette(palette)
    out.putdata([{255: 0, 170: 1, 85: 2, 0: 3}[v] for v in gfx.getdata()])
    out.save(gfx_path)
    open(lay % ('Mappings', DECOR), 'wb').write(maps)
    open(lay % ('Collisions', DECOR), 'wb').write(cols)
    print('maison DX : %d briques, %d tuiles, palettes DX -> décor %s' % (
        len(FURNITURE), len(placed), {k: v[0] for k, v in enumerate(pals)}))


if __name__ == '__main__':
    main()
