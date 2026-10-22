"""Le Labyrinthe des Lynels (le 3e jeu du forain, façon Pac-Man) : son décor et son plan.

Lit art/labyrinthe.txt (15 x 11 cases) et fabrique le décor $69 (copie du décor de grotte $59 faite
par tools/make_songe.py, avec la palette PALH_LABYRINTHE) : fond noir, des murs dessinés comme ceux
de Pac-Man (un trait bleu qui suit le contour de chaque mur, arrondi aux coins, et un second trait
sur le bord de la salle), les rubis à ramasser, les gemmes de force (deux images : elles clignotent)
et la porte rose de l'enclos des Lynels. Puis écrit le plan story/salles/labyrinthe.txt (salle 5:e9,
lue par tools/make_rooms.py).

Briques (code/ages/balladePac.s les connaît) :
  $a0 le sol ; $a3 un rubis ; $a4 / $a5 une gemme (deux images) ; $a6 la porte de l'enclos ;
  $c8 et suivantes : les murs (une brique par dessin différent).
Images : gfx/ages/gfx_tileset69.png (tuile n = numéro n ^ $80, banque vidéo 1) ; palettes du décor :
2 les murs, 3 les rubis, 4 la gemme, 5 la gemme qui brille, 6 la porte.

Usage : python tools/make_pacman.py   (après tools/make_songe.py, avant tools/make_rooms.py)
"""
import math
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
TILESET = 0x69
ROOM = '5:e9'
FLOOR, RUPEE, GEM, GEM_FLASH, DOOR, FIRST_WALL = 0xa0, 0xa3, 0xa4, 0xa5, 0xa6, 0xc8
W, H = 15, 11

# 16 x 16 ; '.' = fond noir, 1-3 = couleurs de la palette
RUPEE_ART = [
    '................',
    '................',
    '................',
    '................',
    '.......1........',
    '......131.......',
    '.....13221......',
    '.....13221......',
    '.....13221......',
    '......121.......',
    '.......1........',
    '................',
    '................',
    '................',
    '................',
    '................',
]
GEM_ART = [
    '................',
    '................',
    '................',
    '......1111......',
    '.....122221.....',
    '....12332221....',
    '...1233222221...',
    '...1232222221...',
    '...1222222221...',
    '....12222221....',
    '.....122221.....',
    '......1221......',
    '.......11.......',
    '................',
    '................',
    '................',
]
DOOR_ART = ['................'] * 6 + ['2222222222222222', '3333333333333333', '2222222222222222'] + \
    ['................'] * 7


def path(kind):
    return {'gfx': os.path.join(DISASM, 'gfx', 'ages', 'gfx_tileset%02x.png' % TILESET),
            'map': os.path.join(DISASM, 'tileset_layouts_expanded', 'ages', 'tilesetMappings%02x.bin' % TILESET),
            'col': os.path.join(DISASM, 'tileset_layouts_expanded', 'ages', 'tilesetCollisions%02x.bin' % TILESET)}[kind]


def read_maze():
    rows = [l.rstrip('\n') for l in open(os.path.join(ROOT, 'art', 'labyrinthe.txt'), encoding='utf-8')
            if l.strip() and not l.startswith('# ')]
    assert len(rows) == H and all(len(r) == W for r in rows), 'art/labyrinthe.txt : %d x %d' % (W, H)
    return rows


def wall_images(rows):
    """Le dessin de chaque case de mur (16 x 16, couleurs 0-2) : les traits à 3 et 6 pixels du vide."""
    open_cells = [(x, y) for y in range(H) for x in range(W) if rows[y][x] != '#']

    def dist(px, py):
        best = 99.0
        for x, y in open_cells:
            dx = max(x * 16 - px, 0, px - (x * 16 + 16))
            dy = max(y * 16 - py, 0, py - (y * 16 + 16))
            if abs(dx) < 12 and abs(dy) < 12:
                best = min(best, math.hypot(dx, dy))
        return best

    images = {}
    for y in range(H):
        for x in range(W):
            if rows[y][x] != '#':
                continue
            edge = x in (0, W - 1) or y in (0, H - 1)
            img = []
            for py in range(16):
                line = []
                for px in range(16):
                    d = dist(x * 16 + px + 0.5, y * 16 + py + 0.5)
                    if 3 <= d < 4.2:
                        line.append(2)
                    elif edge and 6 <= d < 7.2:
                        line.append(1)
                    else:
                        line.append(0)
                img.append(line)
            images[(x, y)] = img
    return images


def art(rows):
    return [[0 if c == '.' else int(c) for c in r] for r in rows]


def main():
    rows = read_maze()
    original = Image.open(path('gfx'))
    palette = original.getpalette()
    im = Image.new('L', original.size, 255)
    maps = bytearray(open(path('map'), 'rb').read())
    cols = bytearray(open(path('col'), 'rb').read())
    level = {0: 255, 1: 170, 2: 85, 3: 0}
    tiles = {}                  # dessin 8 x 8 -> numéro de tuile

    def tile_of(pix):
        key = tuple(tuple(r) for r in pix)
        if key not in tiles:
            n = len(tiles)
            assert n < 256, 'trop de tuiles'
            tiles[key] = n
            x0, y0 = (n % 16) * 8, (n // 16) * 8
            for yy in range(8):
                for xx in range(8):
                    im.putpixel((x0 + xx, y0 + yy), level[pix[yy][xx]])
        return tiles[key]

    def put(mt, img, pal, solid):
        entry = []
        for q in range(4):
            qx, qy = (q % 2) * 8, (q // 2) * 8
            entry.append(tile_of([[img[qy + yy][qx + xx] for xx in range(8)] for yy in range(8)]) ^ 0x80)
        maps[mt * 8:mt * 8 + 8] = bytes(entry + [0x08 | pal] * 4)
        cols[mt] = 0x0f if solid else 0

    blank = [[0] * 16 for _ in range(16)]
    put(FLOOR, blank, 2, False)
    put(RUPEE, art(RUPEE_ART), 3, False)
    put(GEM, art(GEM_ART), 4, False)
    put(GEM_FLASH, art(GEM_ART), 5, False)
    put(DOOR, art(DOOR_ART), 6, True)

    # Les murs : une brique par dessin
    walls, plan = {}, []
    images = wall_images(rows)
    for y in range(H):
        line = []
        for x in range(W):
            c = rows[y][x]
            if c == '#':
                key = tuple(tuple(r) for r in images[(x, y)])
                if key not in walls:
                    mt = FIRST_WALL + len(walls)
                    assert mt < 0xf0, 'trop de murs différents'
                    walls[key] = mt
                    put(mt, images[(x, y)], 2, True)
                line.append(walls[key])
            else:
                line.append({'.': RUPEE, 'o': GEM, '-': DOOR}.get(c, FLOOR))
        plan.append(line)

    index = {palette[3 * i]: i for i in range(4)}
    out = Image.new('P', im.size)
    out.putpalette(palette)
    out.putdata([index[v] for v in im.getdata()])
    out.save(path('gfx'))
    open(path('map'), 'wb').write(maps)
    open(path('col'), 'wb').write(cols)

    with open(os.path.join(ROOT, 'story', 'salles', 'labyrinthe.txt'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# Le Labyrinthe des Lynels (le 3e jeu du forain). ÉCRIT PAR tools/make_pacman.py depuis\n'
                '# art/labyrinthe.txt : modifier le labyrinthe là-bas.\n')
        f.write('salle %s decor %02x\n' % (ROOM, TILESET))
        for line in plan:
            f.write(' '.join('%02x' % t for t in line) + '\n')
    rupees = sum(r.count('.') for r in rows)
    print('-> décor $%02x : %d murs, %d tuiles ; %d rubis, %d gemmes' %
          (TILESET, len(walls), len(tiles), rupees, sum(r.count('o') for r in rows)))


main()
