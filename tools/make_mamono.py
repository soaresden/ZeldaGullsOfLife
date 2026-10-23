"""Les jeux du forain : les chiffres dessinés sur le sable (le Mamono, le Creuse-Rubis).

L'arène du Mamono (5:ea, code/ages/balladeMamono.s) a son propre décor, $6a, copie de la plage
d'Ages ($18) faite par tools/make_songe.py. On y ajoute des briques : $41-$68, le sable avec un
chiffre de 1 à 40 (la somme des niveaux des monstres autour ; les monstres eux-mêmes sont les vrais
ennemis du jeu, figés). Leurs tuiles prennent la place de tuiles du décor que l'arène n'affiche
jamais (les tuyaux rouges de l'île du Croissant d'Ages...) : on ne touche à aucune tuile des
briques de la salle.

Images : gfx/ages/gfx_tileset68.png (tuile n de l'image = numéro (n ^ $80) dans la brique, banque
vidéo 1) ; briques : tileset_layouts_expanded/ages/tilesetMappings68.bin (4 tuiles + 4 attributs) ;
collisions : tilesetCollisions68.bin (0 : on marche dessus).

Aussi : les monstres vaincus du Mamono laissent leur niveau dans un cadre (briques $69-$6d, 1 à 5 :
on voit qu'il y avait là un monstre, pour continuer à compter) ; et la plage du Creuse-Rubis (1:ac,
décor $68, copie de la même plage) reçoit les chiffres 1 à 8 ($41-$48) : le nombre de bombes autour
d'une case creusée, sous le rubis (code/ages/balladeCreuse.s).

Usage : python tools/make_mamono.py   (après tools/make_songe.py, avant tools/make_rooms.py)
"""
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
# (décor, fichier du plan, salle, dernier chiffre, cadres des monstres vaincus)
DECORS = [(0x6a, 'mamono.txt', '5:ea', 40, True), (0x68, 'ile_brume.txt', 'ac', 8, False)]
FIRST_BOXED = 0x68          # brique $68 + n : le monstre vaincu de niveau n (1-5)
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


def path(kind, tileset):
    return {'gfx': os.path.join(DISASM, 'gfx', 'ages', 'gfx_tileset%02x.png' % tileset),
            'map': os.path.join(DISASM, 'tileset_layouts_expanded', 'ages', 'tilesetMappings%02x.bin' % tileset),
            'col': os.path.join(DISASM, 'tileset_layouts_expanded', 'ages', 'tilesetCollisions%02x.bin' % tileset)}[kind]


def room_metatiles(plan, room):
    """Les briques de la salle (son plan dans story/salles/)."""
    used, cur = set(), False
    for line in open(os.path.join(ROOT, 'story', 'salles', plan), encoding='utf-8'):
        line = line.split('#')[0].strip()
        if line.startswith('salle'):
            cur = line.split()[1] == room
            continue
        if cur and line:
            used.update(int(t, 16) for t in line.split())
    used.add(SAND)
    return used


def decor(TILESET, plan, room, last_number, boxed):
    original = Image.open(path('gfx', TILESET))
    palette = original.getpalette()
    im = original.convert('L')
    maps = bytearray(open(path('map', TILESET), 'rb').read())
    cols = bytearray(open(path('col', TILESET), 'rb').read())

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
    for mt in room_metatiles(plan, room):
        for q in range(4):
            keep.add(maps[mt * 8 + q] ^ 0x80)
    # (pas les tuiles que l'animation de la mer réécrit sans cesse : 4-19 et 232-239 de l'image,
    # data/ages/animationGfxHeaders.s ; Denis voyait un trou à la place du « 3 »)
    free = [n for n in range(256) if n not in keep and not (4 <= n < 20 or 232 <= n < 240)]
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

    def number(n, box=False):
        """Le chiffre n au milieu du sable, foncé avec un liseré clair ; box : dans un cadre foncé
        (un monstre vaincu)."""
        glyphs = [DIGITS[c] for c in str(n)]
        width = sum(len(g[0]) for g in glyphs) + len(glyphs) - 1
        img = [row[:] for row in sand]
        if box:
            for y in range(1, 15):
                for x in range(1, 15):
                    edge = y in (1, 14) or x in (1, 14)
                    corner = (y in (1, 14)) and (x in (1, 14))
                    if corner:
                        continue
                    img[y][x] = 3 if edge else 0
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
                        if not box or not (y + dy in (1, 14) or x + dx in (1, 14)):
                            img[y + dy][x + dx] = 0
        for (y, x) in ink:
            img[y][x] = 3
        return img

    for n in range(1, last_number + 1):
        add_metatile(FIRST_NUMBER + n, number(n))
    if boxed:
        for n in range(1, 6):
            add_metatile(FIRST_BOXED + n, number(n, box=True))

    # Même format que l'image d'origine (en couleurs indexées, même palette)
    index = {palette[3 * i]: i for i in range(4)}
    out = Image.new('P', im.size)
    out.putpalette(palette)
    out.putdata([index[v] for v in im.getdata()])
    out.save(path('gfx', TILESET))
    open(path('map', TILESET), 'wb').write(maps)
    open(path('col', TILESET), 'wb').write(cols)
    print('-> décor $%02x : %d chiffres%s (%d tuiles libres restantes)'
          % (TILESET, last_number, ' et 5 cadres' if boxed else '', len(free)))


def main():
    for args in DECORS:
        decor(*args)


main()
