"""Fabrique l'écran titre de Gulls of Life (à la place de celui d'Oracle of Ages).

Une image de 160 x 144 en bandes, chacune avec sa palette de 4 couleurs (Game Boy Color) :
- en haut, le ciel de la nuit et « THE LEGEND OF ZELDA » (police du jeu) ;
- le logo « GULLS OF LIFE » doré (art/titre_logo.txt) et Marine en mouette, qui vole
  (art/marine_mouette.txt, agrandie deux fois) ;
- l'aube : le soleil se lève sur l'horizon (art/film_sprites.txt) ;
- la mer.

Écrit dans oracles-disasm :
- gfx_compressible/ages/gfx_title_bg.png, map_title_bg.bin, flg_title_bg.bin (GFXH_TITLE) ;
- data/ages/paletteData.s : paletteDataTitle (PALH_TITLE), entre deux repères.

Usage : python tools/make_title.py   (depuis la racine du dépôt)
"""
import os
import re

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
GFX = os.path.join(DISASM, 'gfx_compressible', 'ages')
PALDATA = os.path.join(DISASM, 'data', 'ages', 'paletteData.s')
BEGIN, END = '; BALLADE-TITRE-DEBUT (tools/make_title.py)', '; BALLADE-TITRE-FIN'
W, H = 160, 144

# Palettes de l'écran titre (couleurs 0 à 3, en RGB 8 bits), dans l'ordre des attributs
PALETTES = [
    ('ciel de la nuit, texte', [(16, 24, 74), (40, 60, 132), (255, 255, 255), (128, 144, 200)]),
    ('logo doré', [(60, 88, 168), (58, 28, 8), (248, 192, 48), (255, 244, 176)]),
    ('Marine en mouette', [(60, 88, 168), (32, 24, 32), (220, 40, 40), (255, 244, 220)]),
    ('aube', [(244, 168, 120), (232, 112, 40), (252, 216, 72), (255, 248, 208)]),
    ('soleil levant', [(244, 168, 120), (232, 112, 40), (252, 216, 72), (255, 248, 208)]),
    ('mer', [(28, 60, 144), (48, 112, 208), (112, 192, 240), (248, 248, 248)]),
]
SKY, LOGO, GULL, DAWN, SUN, SEA = range(6)
ART = {'k': 1, 'r': 2, 'w': 3}


def dither(x, y):
    return [[0.2, 0.6], [0.8, 0.4]][y % 2][x % 2]


def read_blocks(path):
    """Blocs de dessin d'un fichier art/ : {nom: lignes} (« @nom » ou commentaire « # nom »)."""
    blocks, name = {}, None
    for line in open(path, encoding='utf-8').read().split('\n'):
        if line.startswith('@'):
            name = line[1:].split()[0]
            blocks[name] = []
        elif line.startswith('#') or not line.strip():
            continue
        elif name is not None:
            blocks[name].append(line)
    return blocks


def gull_flying():
    rows = [l for l in open(os.path.join(ROOT, 'art', 'marine_mouette.txt'), encoding='utf-8').read().split('\n')
            if l.strip() and not l.startswith('#')]
    return rows[32:48]   # image 3 : en vol


def draw():
    pix = [[0] * W for _ in range(H)]
    pal = [[SKY] * W for _ in range(H)]

    def put(x, y, p, c):
        pix[y][x] = c
        pal[y][x] = p

    # Ciel de la nuit, et « THE LEGEND OF ZELDA » avec la police du jeu (ombre décalée)
    for y in range(24):
        for x in range(W):
            put(x, y, SKY, 1 if y / 23 > dither(x, y) + 0.2 else 0)
    font = Image.open(os.path.join(DISASM, 'gfx', 'common', 'gfx_font.png'))
    fp = font.load()
    background = fp[0, 0]
    text = 'THE LEGEND OF ZELDA'
    left = (W - len(text) * 8) // 2
    for i, ch in enumerate(text):
        gx, gy = (ord(ch) % 16) * 8, (ord(ch) // 16) * 16
        for y in range(16):
            for x in range(8):
                if fp[gx + x, gy + y] != background:
                    X, Y = left + i * 8 + x, 2 + y
                    put(X, Y, SKY, 2)
                    if Y + 1 < 24 and X + 1 < W and pix[Y + 1][X + 1] != 2:
                        put(X + 1, Y + 1, SKY, 3)

    # Le logo, doré : clair en haut, contour sombre
    for y in range(24, 88):
        for x in range(W):
            put(x, y, LOGO, 0)
    words = read_blocks(os.path.join(ROOT, 'art', 'titre_logo.txt'))

    def stamp(rows, ox, oy):
        h, w = len(rows), len(rows[0])

        def inside(x, y):
            return 0 <= x < w and 0 <= y < h and rows[y][x] == '#'
        for y in range(-2, h + 2):
            for x in range(-2, w + 2):
                X, Y = ox + x, oy + y
                if inside(x, y):
                    put(X, Y, LOGO, 3 if y < h * 0.42 else 2)
                elif any(inside(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                    put(X, Y, LOGO, 1)
    gulls, oflife = words['GULLS'], words['OF']
    stamp(gulls, (W - len(gulls[0])) // 2, 29)
    stamp(oflife, (W - len(oflife[0])) // 2 - 12, 62)

    # Marine en mouette, agrandie deux fois, qui vole vers le logo
    for yy, row in enumerate(gull_flying()):
        for xx, ch in enumerate(row):
            if ch != '.':
                for dy in range(2):
                    for dx in range(2):
                        put(128 + (15 - xx) * 2 + dx, 56 + yy * 2 + dy, GULL, ART[ch])

    # L'aube et le soleil levant
    sun = read_blocks(os.path.join(ROOT, 'art', 'film_sprites.txt'))['sun']
    for y in range(88, 104):
        for x in range(W):
            put(x, y, DAWN, 0)   # uni : le soleil ne laisse pas de rectangle
    for yy, row in enumerate(sun):
        for xx, ch in enumerate(row):
            if ch != '.':
                put(64 + xx, 88 + yy, SUN, ART[ch])

    # La mer
    for y in range(104, H):
        for x in range(W):
            d = y - 104
            c = 2 if d < 3 else 1 if d <= 20 else 0
            if ((x + d * 3) // 6 + d // 3) % 7 == 0 and d % 5 == 1:
                c = 3 if d < 12 else 2
            put(x, y, SEA, c)
    return pix, pal


def build():
    pix, pal = draw()
    tiles, index, tilemap, attrs = [], {}, [], []
    for ty in range(18):
        for tx in range(32):
            sx = min(tx, 19)   # colonnes hors de l'écran : comme la dernière
            cells = [(sx * 8 + x, ty * 8 + y) for y in range(8) for x in range(8)]
            palettes = {pal[y][x] for x, y in cells}
            # Une tuile n'a qu'une palette : là où la mouette ou le soleil passent devant le fond,
            # c'est la leur, et le fond prend leur couleur 0 (le même ciel, sans le tramage)
            objects = palettes & {GULL, SUN}
            if objects:
                assert len(objects) == 1, 'tuile (%d, %d) : %s' % (sx, ty, objects)
                p = objects.pop()
                for x, y in cells:
                    if pal[y][x] != p:
                        pal[y][x], pix[y][x] = p, 0
                palettes = {p}
            assert len(palettes) == 1, 'tuile (%d, %d) : plusieurs palettes %s' % (sx, ty, palettes)
            t = tuple(pix[y][x] for x, y in cells)
            if t not in index:
                index[t] = len(tiles)
                tiles.append(t)
            tilemap.append(index[t])
            attrs.append(palettes.pop())
    assert len(tiles) <= 256, len(tiles)
    # Deux fichiers de 128 tuiles au plus (limite d'un en-tête) : $8800 puis $9000. Chacun finit
    # par une tuile qui contient les 4 nuances (le convertisseur les trie par luminosité) ;
    # dans le premier, elle prend la place 127, que la carte n'utilise pas.
    shades = tuple([0, 1, 2, 3] * 16)
    chunks = [tiles[:127] + [shades], tiles[127:] + [shades]]
    assert len(chunks[1]) <= 128, len(tiles)
    for name, chunk in zip(('gfx_title_bg', 'gfx_title_bg_2'), chunks):
        rows = (len(chunk) + 15) // 16
        im = Image.new('P', (128, rows * 8))
        im.putpalette([v for g in (255, 170, 85, 0) for v in (g, g, g)] + [0] * (768 - 12))
        for i, t in enumerate(chunk):
            for p, c in enumerate(t):
                im.putpixel(((i % 16) * 8 + p % 8, (i // 16) * 8 + p // 8), c)
        im.save(os.path.join(GFX, name + '.png'))
    # Numéro de tuile (adressage signé) : premier fichier en $8800 -> $80 + k ; second en $9000 -> k
    tilemap = [0x80 + i if i < 127 else i - 127 for i in tilemap]
    open(os.path.join(GFX, 'map_title_bg.bin'), 'wb').write(bytes(tilemap))
    open(os.path.join(GFX, 'flg_title_bg.bin'), 'wb').write(bytes(attrs))

    # Palettes
    lines = [BEGIN, 'paletteDataTitle: ; écran titre de Gulls of Life']
    for name, colors in PALETTES:
        lines.append('\t; %s' % name)
        lines += ['\tm_RGB16 $%02x $%02x $%02x' % tuple(v >> 3 for v in c) for c in colors]
    lines.append(END)
    data = open(PALDATA, encoding='utf-8').read()
    block = '\n'.join(lines)
    if BEGIN in data:
        data = data[:data.index(BEGIN)] + block + data[data.index(END) + len(END):]
    else:
        data = data.rstrip('\n') + '\n\n' + block + '\n'
    open(PALDATA, 'w', encoding='utf-8', newline='\n').write(data)
    print('écran titre : %d tuiles' % len(tiles))

    # Aperçu (pour la page du jeu)
    preview = Image.new('RGB', (W, H))
    for y in range(H):
        for x in range(W):
            preview.putpixel((x, y), PALETTES[pal[y][x]][1][pix[y][x]])
    os.makedirs(os.path.join(ROOT, 'out'), exist_ok=True)
    preview.save(os.path.join(ROOT, 'out', 'titre.png'))


build()
