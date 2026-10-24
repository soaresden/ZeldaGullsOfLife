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

Aussi : les notes du joueur dans le Mamono (B sur une case pas creusée, Denis : 1, 2... jusqu'à 5,
puis plus rien ; briques $69-$6d, le chiffre clair cerné de foncé sur le sable meuble) ; et la plage
du Creuse-Rubis (1:ac, décor $68, copie de la même plage) reçoit les chiffres 1 à 8 ($41-$48) : le
nombre de bombes autour d'une case creusée, sous le rubis (code/ages/balladeCreuse.s) ; et le
drapeau ($49 : B, « ici, une bombe ! », sur le sable meuble).

Usage : python tools/make_mamono.py   (après tools/make_songe.py, avant tools/make_rooms.py)
"""
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
# (décor, fichier du plan, salle, dernier chiffre, marques du joueur : 'notes' ou 'drapeau')
DECORS = [(0x6a, 'mamono.txt', '5:ea', 40, 'notes'), (0x68, 'ile_brume.txt', 'ac', 8, 'drapeau')]
FIRST_NOTE = 0x68           # brique $68 + n : la note n du joueur (1-5), sur le sable meuble
FLAG = 0x49                 # le drapeau du Creuse-Rubis, sur le sable meuble
UNDUG = 0x12                # la brique de sable meuble (pas creusé)
SPRITE_TILES = {0x29, 0x2a, 0x2b, 0x5c, 0x5d, 0x5e, 0x5f}   # réécrites pendant le Mamono
SAND = 0xbf                 # la brique de sable lisse
FIRST_NUMBER = 0x40         # brique $40 + n : le chiffre n (1-40)
FLAG_ART = ['................',
            '................',
            '....##..........',
            '....#.##........',
            '....#...##......',
            '....#.....#.....',
            '....#...##......',
            '....#.##........',
            '....##..........',
            '....#...........',
            '....#...........',
            '....#...........',
            '...###..........',
            '................',
            '................',
            '................']
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
    used.add(UNDUG)
    return used


def decor(TILESET, plan, room, last_number, marks):
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
    # Ni celles que le jeu réécrit pendant la partie (les images des monstres modèles et de leurs
    # effets, en mémoire vidéo $8800-$8fff : sondé dans l'émulateur, Denis voyait des chiffres
    # cassés) ; d'abord les tuiles $80-$ff de l'image ($9000-$97ff : les sprites n'y vont jamais)
    free = [n for n in free if n not in SPRITE_TILES]
    free = [n for n in free if n >= 0x80] + [n for n in free if n < 0x80]
    def shown(n, attr):
        """La tuile n telle qu'on la voit avec ses attributs (miroirs : bits 5 et 6)."""
        pix = tile(n)
        if attr & 0x20:
            pix = [row[::-1] for row in pix]
        if attr & 0x40:
            pix = pix[::-1]
        return pix

    def ground(mt):
        """Une brique de sol : ses tuiles, son image 16 x 16 (miroirs compris), ses attributs."""
        tiles = [maps[mt * 8 + q] ^ 0x80 for q in range(4)]
        attrs = list(maps[mt * 8 + 4:mt * 8 + 8])
        quads = [shown(tiles[q], attrs[q]) for q in range(4)]
        img = [[quads[(y // 8) * 2 + x // 8][y % 8][x % 8] for x in range(16)] for y in range(16)]
        return tiles, img, attrs

    sand_tiles, sand, sand_attrs = ground(SAND)
    undug_tiles, undug, undug_attrs = ground(UNDUG)

    def add_metatile(mt, img, base_tiles=sand_tiles, attrs=sand_attrs):
        """img : 16 x 16 (couleurs 0-3) -> 4 tuiles (réutilise le sol intact), la brique mt."""
        entry, out_attrs = [], []
        for q in range(4):
            qx, qy = (q % 2) * 8, (q // 2) * 8
            pix = [[img[qy + y][qx + x] for x in range(8)] for y in range(8)]
            if pix == shown(base_tiles[q], attrs[q]):
                n, at = base_tiles[q], attrs[q]
            else:
                assert free, 'plus de tuile libre dans le décor $%02x' % TILESET
                n, at = free.pop(0), attrs[q] & ~0x60     # une tuile neuve, à l'endroit
                put_tile(n, pix)
            entry.append(n ^ 0x80)
            out_attrs.append(at)
        maps[mt * 8:mt * 8 + 8] = bytes(entry + out_attrs)
        cols[mt] = 0

    def number(n, base=sand, ink_color=3, edge_color=0):
        """Le chiffre n au milieu du sol, foncé avec un liseré clair (les notes du joueur : clair
        cerné de foncé, sur le sable meuble)."""
        glyphs = [DIGITS[c] for c in str(n)]
        width = sum(len(g[0]) for g in glyphs) + len(glyphs) - 1
        img = [row[:] for row in base]
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
                        img[y + dy][x + dx] = edge_color
        for (y, x) in ink:
            img[y][x] = ink_color
        return img

    def flag():
        """Le drapeau : la hampe foncée, la toile claire cernée de foncé, sur le sable meuble."""
        img = [row[:] for row in undug]
        for y, row in enumerate(FLAG_ART):
            for x, c in enumerate(row):
                if c == '#':
                    img[y][x] = 3
        for y in range(3, 8):               # la toile : entre la hampe et le bord du triangle
            for x in range(5, 11):
                if FLAG_ART[y][x] == '.' and '#' in FLAG_ART[y][x:]:
                    img[y][x] = 0
        return img

    for n in range(1, last_number + 1):
        add_metatile(FIRST_NUMBER + n, number(n))
    if marks == 'notes':
        for n in range(1, 6):
            add_metatile(FIRST_NOTE + n, number(n, undug, 0, 3), undug_tiles, undug_attrs)
    else:
        add_metatile(FLAG, flag(), undug_tiles, undug_attrs)

    # Même format que l'image d'origine (en couleurs indexées, même palette)
    index = {palette[3 * i]: i for i in range(4)}
    out = Image.new('P', im.size)
    out.putpalette(palette)
    out.putdata([index[v] for v in im.getdata()])
    out.save(path('gfx', TILESET))
    open(path('map', TILESET), 'wb').write(maps)
    open(path('col', TILESET), 'wb').write(cols)
    print('-> décor $%02x : %d chiffres, %s (%d tuiles libres restantes, dont %d hautes)'
          % (TILESET, last_number, '5 notes' if marks == 'notes' else 'le drapeau', len(free),
             sum(1 for n in free if n >= 0x80)))


def main():
    for args in DECORS:
        decor(*args)


main()
