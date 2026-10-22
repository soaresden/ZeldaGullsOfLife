"""Le Mamono du forain : les chiffres dessinés sur le sable de son arène.

L'arène du Mamono (5:ea, code/ages/balladeMamono.s) a son propre décor, $6a, copie de la plage
d'Ages ($18) faite par tools/make_songe.py. On y ajoute des briques : $41-$68, le sable avec un
chiffre de 1 à 40 (la somme des niveaux des monstres autour ; les monstres eux-mêmes sont les vrais
ennemis du jeu, figés). Leurs tuiles prennent la place de tuiles du décor que l'arène n'affiche
jamais (les tuyaux rouges de l'île du Croissant d'Ages...) : on ne touche à aucune tuile des
briques de la salle.

Images : gfx/ages/gfx_tileset68.png (tuile n de l'image = numéro (n ^ $80) dans la brique, banque
vidéo 1) ; briques : tileset_layouts_expanded/ages/tilesetMappings68.bin (4 tuiles + 4 attributs) ;
collisions : tilesetCollisions68.bin (0 : on marche dessus).

Usage : python tools/make_mamono.py   (après tools/make_songe.py, avant tools/make_rooms.py)
"""
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
TILESET = 0x6a
ROOM = '5:ea'
LAST_NUMBER = 40
SAND = 0xbf                 # la brique de sable lisse
FIRST_NUMBER = 0x40         # brique $40 + n : le chiffre n (1-40)
GREY = {255: 0, 170: 1, 85: 2, 0: 3}
LEVEL = {0: 255, 1: 170, 2: 85, 3: 0}

DIGITS = {
    '0': ['.##.', '#..#', '#..#', '#..#', '#..#', '#..#', '.##.'],
    '1': ['.#..', '##..', '.#..', '.#..', '.#..', '.#..', '###.'],
    '2': ['.##.', '#..#', '...#', '..#.', '.#..', '#...', '####'],
    '3': ['###.', '...#', '...#', '.##.', '...#', '...#', '###.'],
    '4': ['..#.', '.##.', '#.#.', '#.#.', '####', '..#.', '..#.'],
    '5': ['####', '#...', '###.', '...#', '...#', '#..#', '.##.'],
    '6': ['.##.', '#...', '#...', '###.', '#..#', '#..#', '.##.'],
    '7': ['####', '...#', '..#.', '..#.', '.#..', '.#..', '.#..'],
    '8': ['.##.', '#..#', '#..#', '.##.', '#..#', '#..#', '.##.'],
    '9': ['.##.', '#..#', '#..#', '.###', '...#', '...#', '.##.'],
}


def path(kind):
    return {'gfx': os.path.join(DISASM, 'gfx', 'ages', 'gfx_tileset%02x.png' % TILESET),
            'map': os.path.join(DISASM, 'tileset_layouts_expanded', 'ages', 'tilesetMappings%02x.bin' % TILESET),
            'col': os.path.join(DISASM, 'tileset_layouts_expanded', 'ages', 'tilesetCollisions%02x.bin' % TILESET)}[kind]


def room_metatiles():
    """Les briques de l'arène (le plan de story/salles/mamono.txt)."""
    used, cur = set(), False
    for line in open(os.path.join(ROOT, 'story', 'salles', 'mamono.txt'), encoding='utf-8'):
        line = line.split('#')[0].strip()
        if line.startswith('salle'):
            cur = line.split()[1] == ROOM
            continue
        if cur and line:
            used.update(int(t, 16) for t in line.split())
    used.add(SAND)
    return used


def main():
    original = Image.open(path('gfx'))
    palette = original.getpalette()
    im = original.convert('L')
    maps = bytearray(open(path('map'), 'rb').read())
    cols = bytearray(open(path('col'), 'rb').read())

    def tile(n):
        x0, y0 = (n % 16) * 8, (n // 16) * 8
        return [[GREY.get(im.getpixel((x0 + x, y0 + y)), 0) for x in range(8)] for y in range(8)]

    def put_tile(n, pix):
        x0, y0 = (n % 16) * 8, (n // 16) * 8
        for y in range(8):
            for x in range(8):
                im.putpixel((x0 + x, y0 + y), LEVEL[pix[y][x]])

    # Les tuiles qu'on garde : toutes celles des briques de la salle
    keep = set()
    for mt in room_metatiles():
        for q in range(4):
            keep.add(maps[mt * 8 + q] ^ 0x80)
    free = [n for n in range(256) if n not in keep]
    attr = maps[SAND * 8 + 4]               # la palette du sable
    sand_tiles = [maps[SAND * 8 + q] ^ 0x80 for q in range(4)]
    sand = [[tile(sand_tiles[(y // 8) * 2 + x // 8])[y % 8][x % 8] for x in range(16)] for y in range(16)]

    def add_metatile(mt, img):
        """img : 16 x 16 (couleurs 0-3) -> 4 tuiles (réutilise le sable intact), la brique mt."""
        entry = []
        for q in range(4):
            qx, qy = (q % 2) * 8, (q // 2) * 8
            pix = [[img[qy + y][qx + x] for x in range(8)] for y in range(8)]
            if pix == tile(sand_tiles[q]):
                n = sand_tiles[q]
            else:
                assert free, 'plus de tuile libre dans le décor $%02x' % TILESET
                n = free.pop(0)
                put_tile(n, pix)
            entry.append(n ^ 0x80)
        maps[mt * 8:mt * 8 + 8] = bytes(entry + [attr] * 4)
        cols[mt] = 0

    # Les chiffres de 1 à 40, au milieu du sable, foncés avec un liseré clair
    for n in range(1, LAST_NUMBER + 1):
        glyphs = [DIGITS[c] for c in str(n)]
        width = sum(len(g[0]) for g in glyphs) + len(glyphs) - 1
        img = [row[:] for row in sand]
        x0, y0 = (16 - width) // 2, 4
        ink = set()
        for g in glyphs:
            for y, row in enumerate(g):
                for x, c in enumerate(row):
                    if c == '#':
                        ink.add((y0 + y, x0 + x))
            x0 += len(g[0]) + 1
        for (y, x) in ink:
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if 0 <= y + dy < 16 and 0 <= x + dx < 16 and (y + dy, x + dx) not in ink:
                        img[y + dy][x + dx] = 0
        for (y, x) in ink:
            img[y][x] = 3
        add_metatile(FIRST_NUMBER + n, img)

    # Même format que l'image d'origine (en couleurs indexées, même palette)
    index = {palette[3 * i]: i for i in range(4)}
    out = Image.new('P', im.size)
    out.putpalette(palette)
    out.putdata([index[v] for v in im.getdata()])
    out.save(path('gfx'))
    open(path('map'), 'wb').write(maps)
    open(path('col'), 'wb').write(cols)
    print('-> décor $%02x : %d chiffres (%d tuiles libres restantes)' % (TILESET, LAST_NUMBER, len(free)))


main()
